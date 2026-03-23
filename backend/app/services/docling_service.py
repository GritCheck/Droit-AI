"""
Docling Service - Local document parsing with IBM Docling
Cutting-edge document understanding with layout-aware chunking
"""

import io
import logging
from typing import List, Dict, Any
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import Docling components
try:
    from docling.document_converter import DocumentConverter
    from docling.chunking import HybridChunker
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    logger.warning("Docling not available. Install with: pip install docling>=2.12.0")
    DOCLING_AVAILABLE = False


class DoclingParser:
    """
    Local document parser using IBM Docling
    Provides layout-aware chunking that preserves document structure
    """
    
    def __init__(self):
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling is not available. Install with: pip install docling>=2.12.0")
        
        # Configure Docling for optimal RAG performance
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = False  # Save memory for RAG
        
        # Initialize converter with optimized settings
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pipeline_options
            }
        )
        
        # Initialize HybridChunker for semantic layout-aware chunking
        # This is the key innovation: respects document structure
        self.chunker = HybridChunker(
            max_tokens=800,  # Optimized for GPT-4 context window
            overlap_tokens=100,
            min_chunk_tokens=200
        )
        
        # Cache directory for models
        cache_dir = Path(settings.local_processed_path) / "docling_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Docling parser initialized with HybridChunker")
    
    async def process_file(self, content: bytes, filename: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Process document using Docling with layout-aware chunking
        
        Args:
            content: Raw file bytes
            filename: Original filename
            **kwargs: Additional metadata (document_id, allowed_groups, etc.)
        
        Returns:
            List of formatted chunks with rich metadata
        """
        try:
            logger.info(f"Processing {filename} with Docling...")
            
            # Convert bytes to stream
            source = io.BytesIO(content)
            
            # Parse document - Docling automatically detects format
            result = self.converter.convert(source)
            
            if not result or not result.document:
                raise ValueError(f"Failed to parse document: {filename}")
            
            # Apply layout-aware chunking
            # This is the innovation: preserves tables, sections, hierarchies
            doc_chunks = self.chunker.chunk(result.document)
            
            # Format chunks for RAG system
            formatted_chunks = []
            document_id = kwargs.get("document_id", filename)
            allowed_groups = kwargs.get("allowed_groups", [])
            
            for i, chunk in enumerate(doc_chunks):
                # Extract rich metadata from Docling
                metadata = self._extract_chunk_metadata(chunk, filename, i, kwargs)
                
                formatted_chunk = {
                    "id": f"{document_id}-chunk-{i}",
                    "content": chunk.text.strip(),
                    "metadata": metadata
                }
                
                formatted_chunks.append(formatted_chunk)
            
            logger.info(f"Docling processed {filename}: {len(formatted_chunks)} layout-aware chunks")
            return formatted_chunks
            
        except Exception as e:
            logger.error(f"Docling processing failed for {filename}: {str(e)}")
            raise
    
    def _extract_chunk_metadata(self, chunk, filename: str, chunk_index: int, kwargs: Dict) -> Dict[str, Any]:
        """Extract rich metadata from Docling chunk"""
        metadata = {
            # Basic file info
            "source": filename,
            "document_id": kwargs.get("document_id", filename),
            "file_name": filename,
            "chunk_index": chunk_index,
            
            # Docling-specific metadata
            "parser_used": "Docling",
            "chunk_type": "layout_aware",
            
            # Security and governance
            "allowed_groups": kwargs.get("allowed_groups", []),
            "ingestion_timestamp": kwargs.get("ingestion_timestamp"),
            "ingested_by": kwargs.get("ingested_by", "Droit_AI_API"),
            
            # Content classification
            "content_type": "text",
            "language": "en",  # Docling can detect language if needed
            "token_count": len(chunk.text.split()) * 1.3,  # Approximate token count
        }
        
        # Extract page numbers if available
        if hasattr(chunk, 'meta') and chunk.meta:
            if hasattr(chunk.meta, 'page_numbers') and chunk.meta.page_numbers:
                metadata["page_numbers"] = list(chunk.meta.page_numbers)
                if chunk.meta.page_numbers:
                    metadata["page_number"] = min(chunk.meta.page_numbers)
            
            # Extract section headings if available
            if hasattr(chunk.meta, 'headings') and chunk.meta.headings:
                metadata["section_heading"] = chunk.meta.headings[0] if chunk.meta.headings else "General"
                metadata["section_hierarchy"] = chunk.meta.headings
            
            # Extract table information if chunk contains table
            if hasattr(chunk.meta, 'is_table') and chunk.meta.is_table:
                metadata["contains_table"] = True
                metadata["chunk_type"] = "table"
            
            # Extract list information if chunk contains list
            if hasattr(chunk.meta, 'is_list') and chunk.meta.is_list:
                metadata["contains_list"] = True
                metadata["chunk_type"] = "list"
        
        # Add title if available
        title = kwargs.get("title", filename)
        metadata["title"] = title
        
        return metadata
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats"""
        return [
            ".pdf", ".docx", ".doc", ".txt", ".md", ".html", 
            ".htm", ".pptx", ".ppt", ".xlsx", ".xls", 
            ".png", ".jpg", ".jpeg", ".bmp", ".tiff"
        ]
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get parser information and capabilities"""
        return {
            "name": "Docling",
            "version": "2.12.0+",
            "type": "local",
            "capabilities": [
                "layout_aware_chunking",
                "table_preservation", 
                "hierarchy_understanding",
                "ocr_support",
                "multi_format_support"
            ],
            "chunking_strategy": "HybridChunker",
            "innovation_points": [
                "Semantic layout preservation",
                "Table structure maintenance", 
                "Section hierarchy awareness",
                "Context-aware chunking"
            ]
        }


# Factory function for dependency injection
def create_docling_parser() -> DoclingParser:
    """Create Docling parser instance"""
    return DoclingParser()


# Health check function
def check_docling_health() -> Dict[str, Any]:
    """Check Docling parser health and availability"""
    return {
        "available": DOCLING_AVAILABLE,
        "parser": "Docling",
        "version": "2.12.0+",
        "type": "local",
        "status": "healthy" if DOCLING_AVAILABLE else "unavailable",
        "supported_formats": DoclingParser().get_supported_formats() if DOCLING_AVAILABLE else [],
        "innovation_features": [
            "Layout-aware chunking with HybridChunker",
            "Table structure preservation", 
            "Section hierarchy understanding",
            "Multi-format document support"
        ] if DOCLING_AVAILABLE else []
    }
