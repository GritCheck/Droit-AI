"""
Parser Service - Dual-pathway document processing
Supports both local Docling parsing and Azure Document Intelligence
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import Docling for local parsing
try:
    DOCLING_AVAILABLE = True
except ImportError:
    logger.warning("Docling not available. Local parsing will be disabled.")
    DOCLING_AVAILABLE = False

# Try to import Azure Document Intelligence
try:
    AZURE_DOC_INTEL_AVAILABLE = True
except ImportError:
    logger.warning("Azure Document Intelligence not available. Cloud parsing will be disabled.")
    AZURE_DOC_INTEL_AVAILABLE = False


class DocumentChunk:
    """Represents a chunk of processed document"""
    
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
    
    def to_search_document(self) -> Dict[str, Any]:
        """Convert to Azure AI Search document format"""
        return {
            "id": self.metadata.get("chunk_id", ""),
            "content": self.content,
            "title": self.metadata.get("title", ""),
            "source_link": self.metadata.get("source_link", ""),
            "page_number": self.metadata.get("page_number"),
            "chunk_id": self.metadata.get("chunk_id", ""),
            "document_id": self.metadata.get("document_id", ""),
            "file_name": self.metadata.get("file_name", ""),
            "allowed_groups": self.metadata.get("allowed_groups", []),
            "ingestion_timestamp": self.metadata.get("ingestion_timestamp"),
            "parser_used": self.metadata.get("parser_used", "unknown"),
            "content_type": self.metadata.get("content_type", "text"),
            "language": self.metadata.get("language", "en"),
            "chunk_type": self.metadata.get("chunk_type", "text"),
            "token_count": self.metadata.get("token_count", 0),
            "vector": self.metadata.get("vector", None)  # Will be added during indexing
        }


class BaseParser(ABC):
    """Abstract base class for document parsers"""
    
    @abstractmethod
    async def process_file(self, content: bytes, filename: str, **kwargs) -> List[DocumentChunk]:
        """Process document and return chunks"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats"""
        pass


# Import the actual parser implementations
try:
    from app.services.docling_service import DoclingParser
except ImportError:
    DoclingParser = None

try:
    from app.services.azure_doc_intel_service import AzureDocIntelParser
except ImportError:
    AzureDocIntelParser = None


class ParserFactory:
    """Factory for creating appropriate parser based on configuration"""
    
    @staticmethod
    def get_parser(mode: Optional[str] = None) -> BaseParser:
        """Get parser instance based on mode or configuration"""
        
        if mode is None:
            # Use configuration to determine mode
            mode = "local" if settings.enable_local_parsing else "azure"
        
        if mode == "local":
            if DoclingParser is None:
                logger.error("Local parsing requested but Docling is not available")
                raise ImportError("Docling is not available for local parsing")
            
            logger.info("Using Docling parser for local processing")
            return DoclingParser()
        
        elif mode == "azure":
            if AzureDocIntelParser is None:
                logger.error("Azure parsing requested but Document Intelligence is not available")
                raise ImportError("Azure Document Intelligence is not available for cloud parsing")
            
            if not settings.azure_doc_intelligence_endpoint:
                logger.error("Azure Document Intelligence endpoint not configured")
                raise ValueError("Azure Document Intelligence not configured")
            
            logger.info("Using Azure Document Intelligence parser")
            return AzureDocIntelParser()
        
        else:
            raise ValueError(f"Unknown parser mode: {mode}")
    
    @staticmethod
    def get_available_parsers() -> Dict[str, bool]:
        """Get status of available parsers"""
        return {
            "docling": DoclingParser is not None,
            "azure_document_intelligence": AzureDocIntelParser is not None
        }


# Convenience function for dependency injection
def get_parser_service(mode: Optional[str] = None) -> BaseParser:
    """Get parser service instance"""
    return ParserFactory.get_parser(mode)
