"""
Document Ingestion API - Dual-pathway document processing
Handles uploads to Azure Data Lake Storage with metadata and indexing
"""

import logging
import uuid
import magic
import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.services.parser_service import ParserFactory, DocumentChunk, get_parser_service
from app.services.search_service import GovernedSearchService
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingestion", tags=["ingestion"])
settings = get_settings()

# File validation constants
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'text/plain',
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/gif'
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MIN_FILE_SIZE = 100  # 100 bytes

DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.app', '.deb', '.pkg', '.dmg', '.rpm', '.deb', '.msi', '.msm', '.msp'
}

# Azure Data Lake Storage client (lazy initialization)
_adls_client = None
_file_system_client = None


def _validate_file_extension(filename: str) -> None:
    """Validate file extension against dangerous extensions"""
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    if f'.{file_ext}' in DANGEROUS_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dangerous file extension not allowed: .{file_ext}"
        )


def _validate_file_size(file_size: int) -> None:
    """Validate file size limits"""
    if file_size < MIN_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too small. Minimum size: {MIN_FILE_SIZE} bytes"
        )
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )


def _validate_mime_type(content: bytes, filename: str) -> str:
    """Validate MIME type using python-magic"""
    try:
        # Use python-magic to detect actual file type
        mime_type = magic.from_buffer(content, mime=True)
        
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {mime_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
            )
        
        return mime_type
        
    except Exception as e:
        logger.warning(f"Failed to detect MIME type for {filename}: {str(e)}")
        # Fallback to extension-based validation
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        ext_mime_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'tiff': 'image/tiff',
            'gif': 'image/gif'
        }
        
        mime_type = ext_mime_map.get(ext)
        if not mime_type or mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension not allowed: .{ext}"
            )
        
        return mime_type


def _scan_file_content(content: bytes) -> None:
    """Basic content scanning for malicious patterns"""
    # Check for common malicious patterns
    malicious_patterns = [
        b'<script',
        b'javascript:',
        b'vbscript:',
        b'data:text/html',
        b'eval(',
        b'exec(',
        b'system(',
        b'shell_exec('
    ]
    
    content_lower = content.lower()
    for pattern in malicious_patterns:
        if pattern in content_lower:
            logger.warning(f"Potentially malicious content detected: {pattern}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains potentially malicious content"
            )


def _calculate_file_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of file for deduplication"""
    return hashlib.sha256(content).hexdigest()


def get_adls_client():
    """Initialize and return ADLS client"""
    global _adls_client, _file_system_client
    
    if _adls_client is None:
        try:
            from azure.storage.filedatalake import DataLakeServiceClient
            
            if not settings.adls_connection_string:
                raise ValueError("ADLS connection string not configured")
            
            _adls_client = DataLakeServiceClient.from_connection_string(
                settings.adls_connection_string
            )
            _file_system_client = _adls_client.get_file_system_client(
                settings.adls_container_name
            )
            
            logger.info("Azure Data Lake Storage client initialized")
            
        except ImportError:
            logger.error("Azure Storage Blob DataLake not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure Data Lake Storage not available"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ADLS client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to initialize storage: {str(e)}"
            )
    
    return _file_system_client


@router.post("/upload")
async def ingest_document(
    file: UploadFile = File(..., description="Document to ingest"),
    group_ids: str = Form(..., description="Comma-separated group IDs for access control"),
    title: Optional[str] = Form(None, description="Document title (optional)"),
    use_local_parsing: Optional[bool] = Form(False, description="Use local Docling parsing"),
    document_id: Optional[str] = Form(None, description="Custom document ID (optional)"),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """
    Ingest document with dual-pathway processing and comprehensive security validation
    
    - **file**: Document file (PDF, DOCX, images, etc.)
    - **group_ids**: Comma-separated group IDs for row-level security
    - **use_local_parsing**: Force use of local Docling parser
    - **title**: Optional document title
    - **document_id**: Optional custom document ID
    
    Returns processing status and indexing results
    """
    
    # Step 1: Basic input validation
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not group_ids.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group IDs are required for access control"
        )
    
    # Step 2: File security validation
    _validate_file_extension(file.filename)
    
    # Step 3: Read and validate file content
    content = await file.read()
    _validate_file_size(len(content))
    
    # Step 4: MIME type validation
    detected_mime_type = _validate_mime_type(content, file.filename)
    
    # Step 5: Content security scanning
    _scan_file_content(content)
    
    # Step 6: Calculate file hash for deduplication
    file_hash = _calculate_file_hash(content)
    logger.info(f"File hash calculated for {file.filename}: {file_hash[:16]}...")
    
    # Step 7: Parse group IDs
    allowed_groups = [gid.strip() for gid in group_ids.split(",") if gid.strip()]
    if not allowed_groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one valid group ID is required"
        )
    
    # Step 8: Validate group ID format (UUID or alphanumeric)
    import re
    group_id_pattern = re.compile(r'^[a-zA-Z0-9\-_]{1,50}$')
    for group_id in allowed_groups:
        if not group_id_pattern.match(group_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid group ID format: {group_id}. Must be alphanumeric, max 50 chars"
            )
    
    # Generate document ID if not provided
    doc_id = document_id or str(uuid.uuid4())
    ingestion_timestamp = datetime.utcnow().isoformat()
    
    try:
        # Stage 1: Upload to Azure Data Lake Storage with metadata
        storage_path = await _upload_to_data_lake(
            file, doc_id, allowed_groups, ingestion_timestamp, use_local_parsing, title, 
            content, detected_mime_type, file_hash
        )
        
        # Stage 2: Parse document using selected pathway
        parser_mode = "local" if use_local_parsing else "azure"
        parser = ParserFactory.get_parser(parser_mode)
        
        # Parse document
        chunks = await parser.process_file(
            content=content,
            filename=file.filename,
            document_id=doc_id,
            allowed_groups=allowed_groups,
            ingestion_timestamp=ingestion_timestamp,
            title=title or file.filename
        )
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Document parsing produced no content"
            )
        
        # Stage 3: Index chunks in Azure AI Search
        indexed_count = await _index_chunks(search_service, chunks)
        
        # Log successful ingestion
        logger.info(f"Successfully ingested {file.filename}: "
                   f"{len(chunks)} chunks indexed, "
                   f"parser: {parser_mode}, "
                   f"mime_type: {detected_mime_type}, "
                   f"file_size: {len(content)}, "
                   f"groups: {allowed_groups}")
        
        return {
            "status": "success",
            "document_id": doc_id,
            "filename": file.filename,
            "title": title or file.filename,
            "storage_path": storage_path,
            "parser_used": parser_mode,
            "chunks_created": len(chunks),
            "chunks_indexed": indexed_count,
            "allowed_groups": allowed_groups,
            "ingestion_timestamp": ingestion_timestamp,
            "file_size": len(content),
            "content_type": detected_mime_type,
            "file_hash": file_hash
        }
        
    except Exception as e:
        logger.error(f"Document ingestion failed for {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}"
        )


async def _upload_to_data_lake(
    file: UploadFile, 
    doc_id: str, 
    allowed_groups: List[str], 
    ingestion_timestamp: str,
    use_local_parsing: bool,
    title: Optional[str],
    content: bytes,
    mime_type: str,
    file_hash: str
) -> str:
    """Upload file to Azure Data Lake Storage with metadata"""
    
    try:
        file_system_client = get_adls_client()
        
        # Create unique file path
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        safe_filename = f"{doc_id}_{file.filename}"
        file_path = f"documents/{safe_filename}"
        
        # Get file client
        file_client = file_system_client.get_file_client(file_path)
        
        # Prepare metadata
        metadata = {
            "document_id": doc_id,
            "allowed_groups": ",".join(allowed_groups),
            "ingested_by": "SentinelRAG_API",
            "parser_used": "Docling" if use_local_parsing else "AzureDocIntel",
            "ingestion_timestamp": ingestion_timestamp,
            "content_type": mime_type,
            "original_filename": file.filename,
            "title": title or file.filename,
            "file_hash": file_hash,
            "file_size": str(len(content)),
            "security_validated": "true"
        }
        
        # Create file with metadata
        file_client.create_file(overwrite=True, metadata=metadata)
        file_client.append_data(content, offset=0, length=len(content))
        file_client.flush_data(len(content))
        
        storage_path = f"adls://{settings.adls_container_name}/{file_path}"
        logger.info(f"Uploaded {file.filename} to {storage_path}")
        
        return storage_path
        
    except Exception as e:
        logger.error(f"Failed to upload to Data Lake: {str(e)}")
        raise


async def _index_chunks(search_service: GovernedSearchService, chunks: List[DocumentChunk]) -> int:
    """Index document chunks in Azure AI Search"""
    
    try:
        # Convert chunks to search documents
        search_documents = []
        
        for chunk in chunks:
            doc = chunk.to_search_document()
            
            # Ensure required fields for security filtering
            if not doc.get("allowed_groups"):
                logger.warning(f"Chunk {doc.get('chunk_id')} has no allowed_groups")
                continue
            
            search_documents.append(doc)
        
        if not search_documents:
            raise ValueError("No valid chunks to index")
        
        # Index in batches
        batch_size = 50
        indexed_count = 0
        
        for i in range(0, len(search_documents), batch_size):
            batch = search_documents[i:i + batch_size]
            await search_service.index_documents(batch)
            indexed_count += len(batch)
            
            logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch)} chunks")
        
        return indexed_count
        
    except Exception as e:
        logger.error(f"Failed to index chunks: {str(e)}")
        raise


@router.get("/parsers/status")
async def get_parser_status():
    """Get available parsers and their status"""
    return {
        "available_parsers": ParserFactory.get_available_parsers(),
        "default_mode": "local" if settings.enable_local_parsing else "azure",
        "local_parsing_enabled": settings.enable_local_parsing,
        "azure_doc_intelligence_enabled": settings.enable_azure_doc_intelligence,
        "supported_formats": {
            "local": DoclingParser().get_supported_formats() if ParserFactory.get_available_parsers()["docling"] else [],
            "azure": AzureDocumentIntelligenceParser().get_supported_formats() if ParserFactory.get_available_parsers()["azure_document_intelligence"] else []
        }
    }


@router.get("/health")
async def ingestion_health():
    """Health check for ingestion service"""
    parser_status = ParserFactory.get_available_parsers()
    
    health_info = {
        "status": "healthy",
        "parsers": parser_status,
        "storage_configured": bool(settings.adls_connection_string),
        "search_configured": bool(settings.azure_search_endpoint),
        "features": {
            "local_parsing": parser_status.get("docling", False),
            "azure_parsing": parser_status.get("azure_document_intelligence", False),
            "metadata_storage": bool(settings.adls_connection_string),
            "group_based_security": True
        }
    }
    
    # Check if at least one parser is available
    if not any(parser_status.values()):
        health_info["status"] = "degraded"
        health_info["error"] = "No parsers available"
    
    return health_info


@router.post("/test-parsing")
async def test_parsing(
    file: UploadFile = File(...),
    use_local_parsing: Optional[bool] = Form(False)
):
    """Test document parsing without indexing"""
    
    try:
        # Get parser
        parser_mode = "local" if use_local_parsing else "azure"
        parser = ParserFactory.get_parser(parser_mode)
        
        # Read content
        content = await file.read()
        
        # Parse
        chunks = await parser.process_file(
            content=content,
            filename=file.filename,
            document_id="test_" + str(uuid.uuid4()),
            allowed_groups=["test-group"],
            ingestion_timestamp=datetime.utcnow().isoformat()
        )
        
        return {
            "parser_used": parser_mode,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "sample_chunks": [
                {
                    "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks[:3]  # Return first 3 chunks as sample
            ]
        }
        
    except Exception as e:
        logger.error(f"Test parsing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test parsing failed: {str(e)}"
        )


# Import parser classes for type hints (avoid circular imports)
try:
    from app.services.parser_service import DoclingParser, AzureDocumentIntelligenceParser
except ImportError:
    # Handle case where parsers aren't available
    DoclingParser = None
    AzureDocumentIntelligenceParser = None
