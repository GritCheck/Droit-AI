"""
Azure Document Intelligence Service - Cloud-based document processing
High-fidelity parsing with Azure AI Form Recognizer
"""

import io
import logging
from typing import List, Dict, Any
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import Azure Document Intelligence
try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_DOC_INTEL_AVAILABLE = True
except ImportError:
    logger.warning("Azure Document Intelligence not available. Install with: pip install azure-ai-documentintelligence")
    AZURE_DOC_INTEL_AVAILABLE = False


class AzureDocIntelParser:
    """
    Cloud document parser using Azure Document Intelligence
    Provides high-fidelity parsing with advanced OCR and layout analysis
    """
    
    def __init__(self):
        if not AZURE_DOC_INTEL_AVAILABLE:
            raise ImportError("Azure Document Intelligence not available. Install with: pip install azure-ai-documentintelligence")
        
        if not settings.azure_doc_intelligence_endpoint or not settings.azure_doc_intelligence_key:
            raise ValueError("Azure Document Intelligence credentials not configured")
        
        # Initialize Azure Document Intelligence client
        self.client = DocumentIntelligenceClient(
            endpoint=settings.azure_doc_intelligence_endpoint,
            credential=AzureKeyCredential(settings.azure_doc_intelligence_key)
        )
        
        logger.info(f"Azure Document Intelligence client initialized: {settings.azure_doc_intelligence_endpoint}")
    
    async def process_file(self, content: bytes, filename: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Process document using Azure Document Intelligence
        
        Args:
            content: Raw file bytes
            filename: Original filename
            **kwargs: Additional metadata
        
        Returns:
            List of formatted chunks with Azure metadata
        """
        try:
            logger.info(f"Processing {filename} with Azure Document Intelligence...")
            
            # Determine appropriate model based on file type
            model_id = self._get_model_id(filename)
            content_type = self._get_content_type(filename)
            
            # Analyze document
            poller = self.client.begin_analyze_document(
                model_id=model_id,
                body=content,
                content_type=content_type,
                output_content_format="markdown"  # Get structured markdown output
            )
            
            # Wait for analysis to complete
            result = await self._await_analysis(poller)
            
            if not result:
                raise ValueError(f"Azure Document Intelligence failed to analyze: {filename}")
            
            # Extract text content and create chunks
            chunks = self._create_chunks_from_result(result, filename, kwargs)
            
            logger.info(f"Azure Document Intelligence processed {filename}: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Azure Document Intelligence processing failed for {filename}: {str(e)}")
            raise
    
    async def _await_analysis(self, poller):
        """Wait for Azure analysis to complete"""
        import asyncio
        
        # Run the blocking poller in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, poller.result)
    
    def _get_model_id(self, filename: str) -> str:
        """Get appropriate Azure Document Intelligence model based on file type"""
        ext = Path(filename).suffix.lower()
        
        model_mapping = {
            ".pdf": "prebuilt-layout",
            ".docx": "prebuilt-document", 
            ".doc": "prebuilt-document",
            ".jpg": "prebuilt-read",
            ".jpeg": "prebuilt-read",
            ".png": "prebuilt-read",
            ".bmp": "prebuilt-read",
            ".tiff": "prebuilt-read",
            ".tif": "prebuilt-read",
            ".html": "prebuilt-document",
            ".htm": "prebuilt-document"
        }
        
        return model_mapping.get(ext, "prebuilt-layout")
    
    def _get_content_type(self, filename: str) -> str:
        """Get appropriate content type for Azure API"""
        ext = Path(filename).suffix.lower()
        
        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", 
            ".png": "image/png",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".html": "text/html",
            ".htm": "text/html"
        }
        
        return content_types.get(ext, "application/octet-stream")
    
    def _create_chunks_from_result(self, result, filename: str, kwargs: Dict) -> List[Dict[str, Any]]:
        """Create chunks from Azure Document Intelligence result"""
        chunks = []
        document_id = kwargs.get("document_id", filename)
        
        # Extract content from result
        full_content = ""
        if hasattr(result, 'content') and result.content:
            full_content = result.content
        elif hasattr(result, 'analyze_result') and result.analyze_result:
            # Fallback to older API format
            if hasattr(result.analyze_result, 'content'):
                full_content = result.analyze_result.content
            else:
                # Extract from paragraphs
                paragraphs = []
                if hasattr(result.analyze_result, 'paragraphs'):
                    for para in result.analyze_result.paragraphs:
                        if hasattr(para, 'content'):
                            paragraphs.append(para.content)
                full_content = "\n\n".join(paragraphs)
        
        # Create intelligent chunks
        chunk_size = 800  # Target tokens per chunk
        overlap = 100
        
        words = full_content.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words).strip()
            
            if not chunk_text:
                continue
            
            chunk_index = i // (chunk_size - overlap)
            
            # Extract rich metadata
            metadata = self._extract_azure_metadata(
                result, filename, chunk_index, chunk_text, kwargs
            )
            
            chunk = {
                "id": f"{document_id}-chunk-{chunk_index}",
                "content": chunk_text,
                "metadata": metadata
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def _extract_azure_metadata(self, result, filename: str, chunk_index: int, chunk_text: str, kwargs: Dict) -> Dict[str, Any]:
        """Extract rich metadata from Azure Document Intelligence result"""
        metadata = {
            # Basic file info
            "source": filename,
            "document_id": kwargs.get("document_id", filename),
            "file_name": filename,
            "chunk_index": chunk_index,
            
            # Azure-specific metadata
            "parser_used": "AzureDocIntel",
            "chunk_type": "azure_layout",
            "azure_model_used": self._get_model_id(filename),
            
            # Security and governance
            "allowed_groups": kwargs.get("allowed_groups", []),
            "ingestion_timestamp": kwargs.get("ingestion_timestamp"),
            "ingested_by": kwargs.get("ingested_by", "Droit_AI_API"),
            
            # Content classification
            "content_type": "text",
            "language": "en",
            "token_count": len(chunk_text.split()) * 1.3,  # Approximate
        }
        
        # Extract Azure-specific information if available
        if hasattr(result, 'analyze_result') and result.analyze_result:
            analyze_result = result.analyze_result
            
            # Extract page information
            if hasattr(analyze_result, 'pages') and analyze_result.pages:
                pages = analyze_result.pages
                if pages:
                    metadata["page_count"] = len(pages)
                    metadata["page_number"] = pages[0].page_number if hasattr(pages[0], 'page_number') else 1
            
            # Extract language information
            if hasattr(analyze_result, 'languages') and analyze_result.languages:
                languages = analyze_result.languages
                if languages:
                    metadata["detected_languages"] = [
                        lang.locale if hasattr(lang, 'locale') else str(lang) 
                        for lang in languages
                    ]
                    metadata["language"] = languages[0].locale if hasattr(languages[0], 'locale') else "en"
            
            # Extract document type
            if hasattr(analyze_result, 'doc_type') and analyze_result.doc_type:
                metadata["azure_doc_type"] = analyze_result.doc_type
            
            # Extract style information
            if hasattr(analyze_result, 'styles') and analyze_result.styles:
                metadata["has_formatted_content"] = True
                metadata["style_count"] = len(analyze_result.styles)
        
        # Add title
        title = kwargs.get("title", filename)
        metadata["title"] = title
        
        return metadata
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats"""
        return [
            ".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png", 
            ".bmp", ".tiff", ".tif", ".html", ".htm"
        ]
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get parser information and capabilities"""
        return {
            "name": "Azure Document Intelligence",
            "version": "1.0.0",
            "type": "cloud",
            "endpoint": settings.azure_doc_intelligence_endpoint,
            "capabilities": [
                "high_fidelity_ocr",
                "table_extraction",
                "form_processing",
                "handwriting_recognition",
                "language_detection"
            ],
            "models": [
                "prebuilt-layout",
                "prebuilt-document", 
                "prebuilt-read"
            ],
            "innovation_points": [
                "Cloud-based processing",
                "Advanced OCR capabilities",
                "Handwriting recognition",
                "Multi-language support",
                "Form and table extraction"
            ]
        }


# Factory function for dependency injection
def create_azure_doc_intel_parser() -> AzureDocIntelParser:
    """Create Azure Document Intelligence parser instance"""
    return AzureDocIntelParser()


# Health check function
def check_azure_doc_intel_health() -> Dict[str, Any]:
    """Check Azure Document Intelligence service health"""
    health = {
        "available": AZURE_DOC_INTEL_AVAILABLE,
        "parser": "Azure Document Intelligence",
        "version": "1.0.0",
        "type": "cloud",
        "endpoint": settings.azure_doc_intelligence_endpoint,
        "configured": bool(settings.azure_doc_intelligence_endpoint and settings.azure_doc_intelligence_key)
    }
    
    if AZURE_DOC_INTEL_AVAILABLE and health["configured"]:
        health["status"] = "healthy"
        health["supported_formats"] = AzureDocIntelParser().get_supported_formats()
        health["innovation_features"] = [
            "High-fidelity OCR with handwriting recognition",
            "Advanced table and form extraction",
            "Multi-language document processing",
            "Cloud-based scalability"
        ]
    else:
        health["status"] = "unhealthy"
        health["error"] = "Azure Document Intelligence not available or not configured"
        health["supported_formats"] = []
        health["innovation_features"] = []
    
    return health
