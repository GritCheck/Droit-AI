"""
Enhanced Data Preprocessing Service - Azure-first document processing pipeline
Handles document ingestion with user folders and group ID metadata for query filtering
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from azure.storage.blob import BlobServiceClient

from app.core.config import get_settings
from app.services.parser_service import get_parser_service
from app.services.search_service import GovernedSearchService

logger = logging.getLogger(__name__)
settings = get_settings()


class EnhancedDataPreprocessingService:
    """
    Enhanced Azure-first data preprocessing service with user folders and metadata
    Handles document ingestion pipeline with proper hierarchical storage and filtering
    """
    
    def __init__(self):
        self.parser = get_parser_service()
        self.search_service: Optional[GovernedSearchService] = None
        
        # Initialize Azure Storage client with Managed Identity support
        try:
            # Try Managed Identity first (for deployed app)
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_shared_token_cache_credential=True,
                exclude_visual_studio_code_credential=True,
                exclude_visual_studio_credential=True,
                exclude_azure_cli_credential=True,
                exclude_interactive_browser_credential=True
            )
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.azure_storage_account_name}.blob.core.windows.net",
                credential=credential
            )
            logger.info("Using Managed Identity credential for enhanced preprocessing service")
        except Exception as e:
            logger.error(f"Managed Identity failed: {str(e)}")
            # Fallback to Connection String for local development
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.azure_storage_connection_string
                )
                logger.info("Using Connection String credential for enhanced preprocessing service (local dev)")
            except Exception as ce:
                logger.error(f"Connection String failed: {str(ce)}")
                self.blob_service_client = None
        
        logger.info("Enhanced DataPreprocessingService initialized with Azure services")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.blob_service_client:
            self.blob_service_client.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.blob_service_client:
            await self.blob_service_client.close()
    
    async def process_document_folder(
        self, 
        folder_path: str, 
        allowed_groups: Optional[List[str]] = None,
        container_name: Optional[str] = None,
        user_folder: Optional[str] = None,
        group_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process all documents in a folder and load to Azure services with user folders and metadata
        
        Args:
            folder_path: Path to folder containing documents
            allowed_groups: List of Azure AD groups that can access these documents
            container_name: Azure Storage container name (defaults to settings)
            user_folder: User-specific folder name for hierarchical storage
            group_ids: List of Azure AD group IDs for query filtering
            
        Returns:
            Processing results summary
        """
        try:
            folder_path = Path(folder_path)
            if not folder_path.exists():
                raise ValueError(f"Folder does not exist: {folder_path}")
            
            container_name = container_name or settings.azure_storage_container_name
            allowed_groups = allowed_groups or ["default-users"]
            user_folder = user_folder or "default-user"
            group_ids = group_ids or []
            
            # Get all supported documents
            supported_extensions = {'.pdf', '.docx', '.txt', '.md'}
            document_files = [
                f for f in folder_path.iterdir() 
                if f.is_file() and f.suffix.lower() in supported_extensions
            ]
            
            logger.info(f"Found {len(document_files)} documents to process")
            
            processed_docs = []
            failed_docs = []
            
            for file_path in document_files:
                try:
                    result = await self._process_single_document(
                        file_path, allowed_groups, container_name, user_folder, group_ids
                    )
                    processed_docs.append(result)
                    logger.info(f"Successfully processed: {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {file_path.name}: {str(e)}")
                    failed_docs.append({
                        "file": file_path.name,
                        "error": str(e)
                    })
            
            return {
                "total_files": len(document_files),
                "processed": len(processed_docs),
                "failed": len(failed_docs),
                "processed_documents": processed_docs,
                "failed_documents": failed_docs,
                "user_folder": user_folder,
                "container": container_name,
                "group_ids": group_ids,
                "allowed_groups": allowed_groups
            }
            
        except Exception as e:
            logger.error(f"Document folder processing failed: {str(e)}")
            raise
    
    async def _process_single_document(
        self, 
        file_path: Path, 
        allowed_groups: List[str],
        container_name: str,
        user_folder: str,
        group_ids: List[str]
    ) -> Dict[str, Any]:
        """Process a single document with enhanced metadata and user folder"""
        
        try:
            # Read document content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Create hierarchical blob name with user folder
            blob_name = f"{user_folder}/{file_path.name}"
            
            # Prepare enhanced metadata for query filtering
            document_id = f"{file_path.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            metadata = {
                "document_id": document_id,
                "allowed_groups": json.dumps(allowed_groups),
                "group_ids": json.dumps(group_ids),  # For query filtering
                "user_folder": user_folder,
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "ingested_by": "EnhancedDataPreprocessingService",
                "title": file_path.stem,
                "file_name": file_path.name,
                "file_size": str(len(content)),  # Convert to string
                "file_type": file_path.suffix.lower(),
                "security_metadata": json.dumps({  # Convert to string
                    "access_groups": allowed_groups,
                    "user_folder": user_folder,
                    "group_ids": group_ids
                }),
                "processing_status": "success"
            }
            
            # Process with Azure Document Intelligence
            logger.info(f"Processing {file_path.name} with Azure Document Intelligence...")
            chunks = await self.parser.process_file(content, file_path.name, **metadata)
            
            if not chunks:
                raise ValueError("No chunks generated from document processing")
            
            # Upload original document to Azure Storage with user folder
            storage_path = await self._upload_to_storage(
                content, blob_name, container_name, metadata
            )
            
            # Add enhanced storage metadata to chunks
            for chunk in chunks:
                if isinstance(chunk, dict):
                    chunk["metadata"]["storage_path"] = storage_path
                    chunk["metadata"]["storage_container"] = container_name
                    chunk["metadata"]["user_folder"] = user_folder
                    chunk["metadata"]["group_ids"] = group_ids
                else:
                    chunk.metadata["storage_path"] = storage_path
                    chunk.metadata["storage_container"] = container_name
                    chunk.metadata["user_folder"] = user_folder
                    chunk.metadata["group_ids"] = group_ids
            
            # Index chunks in Azure AI Search with enhanced metadata
            if self.search_service:
                await self.search_service.index_chunks(chunks)
                logger.info(f"Indexed {len(chunks)} chunks from {file_path.name}")
            
            return {
                "file_name": file_path.name,
                "document_id": document_id,
                "storage_path": storage_path,
                "chunks_count": len(chunks),
                "user_folder": user_folder,
                "group_ids": group_ids,
                "allowed_groups": allowed_groups,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Document processing failed for {file_path.name}: {str(e)}")
            return {
                "file_name": file_path.name,
                "error": str(e),
                "status": "failed"
            }
    
    async def _upload_to_storage(
        self, 
        content: bytes, 
        blob_name: str, 
        container_name: str, 
        metadata: Dict[str, Any]
    ) -> str:
        """Upload content to Azure Storage with user folder structure"""
        
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            # Upload with metadata
            blob_client.upload_blob(
                content,
                metadata=metadata,
                overwrite=True
            )
            
            storage_path = f"https://{settings.azure_storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}"
            logger.info(f"Uploaded to Azure Storage: {storage_path}")
            
            return storage_path
            
        except Exception as e:
            logger.error(f"Storage upload failed: {str(e)}")
            raise

    async def get_processing_status(self, container_name: Optional[str] = None) -> Dict[str, Any]:
        """Get processing status for documents in container"""
        try:
            if not self.blob_service_client:
                raise ValueError("Azure Storage client not initialized")
            
            container_name = container_name or settings.azure_storage_container_name
            container_client = self.blob_service_client.get_container_client(container_name)
            
            # List all blobs and their metadata (with pagination for large containers)
            blob_list = container_client.list_blobs(max_results_per_page=100)
            
            processed_docs = []
            failed_docs = []
            total_size = 0
            
            for blob in blob_list:
                metadata = blob.metadata or {}
                status = metadata.get("processing_status", "unknown")
                
                # Safe JSON parsing with error handling
                try:
                    group_ids = json.loads(metadata.get("group_ids", "[]"))
                    if not isinstance(group_ids, list):
                        group_ids = []
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Invalid group_ids JSON in blob {blob.name}")
                    group_ids = []
                
                try:
                    allowed_groups = json.loads(metadata.get("allowed_groups", "[]"))
                    if not isinstance(allowed_groups, list):
                        allowed_groups = []
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Invalid allowed_groups JSON in blob {blob.name}")
                    allowed_groups = []
                
                if status == "success":
                    processed_docs.append({
                        "name": blob.name,
                        "size": blob.size,
                        "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                        "user_folder": metadata.get("user_folder", "unknown"),
                        "group_ids": group_ids,
                        "allowed_groups": allowed_groups
                    })
                    total_size += blob.size
                elif status == "failed":
                    failed_docs.append({
                        "name": blob.name,
                        "error": metadata.get("error", "Unknown error"),
                        "user_folder": metadata.get("user_folder", "unknown")
                    })
            
            return {
                "container_name": container_name,
                "total_documents": len(list(blob_list)),
                "processed": len(processed_docs),
                "failed": len(failed_docs),
                "total_size_bytes": total_size,
                "processed_documents": processed_docs,
                "failed_documents": failed_docs,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing status: {str(e)}")
            return {
                "container_name": container_name or "unknown",
                "status": "error",
                "error": str(e),
                "total_documents": 0,
                "processed": 0,
                "failed": 0
            }


def create_enhanced_data_preprocessing_service() -> EnhancedDataPreprocessingService:
    """Factory function for enhanced data preprocessing service"""
    return EnhancedDataPreprocessingService()


def check_enhanced_data_preprocessing_health() -> Dict[str, Any]:
    """Health check for enhanced data preprocessing service"""
    try:
        # Check Azure Storage connectivity
        service = create_enhanced_data_preprocessing_service()
        
        # Test storage connection
        if service.blob_service_client:
            try:
                service.blob_service_client.get_account_information()
                storage_status = "healthy"
                storage_features = ["Azure Blob Storage", "User folders", "Metadata support"]
            except Exception as e:
                storage_status = "degraded"
                storage_features = [f"Azure Storage error: {str(e)}"]
        else:
            storage_status = "unhealthy"
            storage_features = ["Azure Storage not available"]
        
        # Check Document Intelligence availability
        try:
            from app.services.parser_service import get_parser_service
            parser = get_parser_service()
            if hasattr(parser, 'process_file'):
                doc_intel_status = "healthy"
                doc_intel_features = ["Azure Document Intelligence", "Content extraction", "Text analysis"]
            else:
                doc_intel_status = "not_configured"
                doc_intel_features = ["Azure Document Intelligence not configured"]
        except Exception as e:
            doc_intel_status = "error"
            doc_intel_features = [f"Document Intelligence error: {str(e)}"]
        
        return {
            "status": "healthy" if storage_status == "healthy" else "degraded",
            "service": "Enhanced Data Preprocessing Service",
            "details": {
                "storage_status": storage_status,
                "doc_intel_status": doc_intel_status,
                "features": [
                    "User-specific folders",
                    "Group ID metadata", 
                    "Hierarchical storage",
                    "Enhanced query filtering"
                ] + storage_features + doc_intel_features
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Enhanced Data Preprocessing Service",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
