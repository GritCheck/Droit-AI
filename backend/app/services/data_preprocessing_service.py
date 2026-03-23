"""
Data Preprocessing Service - Azure-first document processing pipeline
Handles document ingestion, preprocessing, and loading to Azure services
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from azure.storage.blob import BlobServiceClient

from app.core.config import get_settings
from app.services.parser_service import get_parser_service
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)
settings = get_settings()


class DataPreprocessingService:
    """
    Azure-first data preprocessing service
    Handles document ingestion pipeline with Azure Document Intelligence
    """
    
    def __init__(self):
        self.parser = get_parser_service()
        self.search_service = SearchService()
        
        # Initialize Azure Storage client
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        
        logger.info("DataPreprocessingService initialized with Azure services")
    
    async def process_document_folder(
        self, 
        folder_path: str, 
        allowed_groups: Optional[List[str]] = None,
        container_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process all documents in a folder and load to Azure services
        
        Args:
            folder_path: Path to folder containing documents
            allowed_groups: List of Azure AD groups that can access these documents
            container_name: Azure Storage container name (defaults to configured)
            
        Returns:
            Processing results summary
        """
        try:
            folder_path = Path(folder_path)
            if not folder_path.exists():
                raise ValueError(f"Folder does not exist: {folder_path}")
            
            container_name = container_name or settings.azure_storage_container_name
            allowed_groups = allowed_groups or ["default-users"]
            
            logger.info(f"Starting document processing for folder: {folder_path}")
            
            # Get all supported documents
            document_files = self._get_supported_documents(folder_path)
            logger.info(f"Found {len(document_files)} documents to process")
            
            processing_results = {
                "total_files": len(document_files),
                "processed": 0,
                "failed": 0,
                "failed_files": [],
                "processing_time": 0,
                "chunks_created": 0,
                "container_name": container_name
            }
            
            start_time = datetime.utcnow()
            
            # Process each document
            for file_path in document_files:
                try:
                    result = await self._process_single_document(
                        file_path, allowed_groups, container_name
                    )
                    
                    if result["success"]:
                        processing_results["processed"] += 1
                        processing_results["chunks_created"] += result["chunks_count"]
                        logger.info(f"Successfully processed: {file_path.name}")
                    else:
                        processing_results["failed"] += 1
                        processing_results["failed_files"].append({
                            "file": file_path.name,
                            "error": result["error"]
                        })
                        logger.error(f"Failed to process {file_path.name}: {result['error']}")
                        
                except Exception as e:
                    processing_results["failed"] += 1
                    processing_results["failed_files"].append({
                        "file": file_path.name,
                        "error": str(e)
                    })
                    logger.error(f"Exception processing {file_path.name}: {str(e)}")
            
            end_time = datetime.utcnow()
            processing_results["processing_time"] = (end_time - start_time).total_seconds()
            
            logger.info(f"Document processing completed: {processing_results}")
            return processing_results
            
        except Exception as e:
            logger.error(f"Document folder processing failed: {str(e)}")
            raise
    
    async def _process_single_document(
        self, 
        file_path: Path, 
        allowed_groups: List[str],
        container_name: str
    ) -> Dict[str, Any]:
        """Process a single document through the Azure pipeline"""
        
        try:
            # Read document content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Prepare metadata
            document_id = f"{file_path.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            metadata = {
                "document_id": document_id,
                "allowed_groups": allowed_groups,
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "ingested_by": "DataPreprocessingService",
                "title": file_path.stem,
                "file_name": file_path.name,
                "file_size": len(content),
                "file_type": file_path.suffix.lower()
            }
            
            # Process with Azure Document Intelligence
            logger.info(f"Processing {file_path.name} with Azure Document Intelligence...")
            chunks = await self.parser.process_file(content, file_path.name, **metadata)
            
            if not chunks:
                raise ValueError("No chunks generated from document processing")
            
            # Upload original document to Azure Storage
            storage_path = await self._upload_to_storage(
                content, file_path.name, container_name, metadata
            )
            
            # Add storage metadata to chunks
            for chunk in chunks:
                if isinstance(chunk, dict):
                    chunk["metadata"]["storage_path"] = storage_path
                    chunk["metadata"]["storage_container"] = container_name
                else:
                    chunk.metadata["storage_path"] = storage_path
                    chunk.metadata["storage_container"] = container_name
            
            # Index chunks in Azure AI Search
            await self.search_service.index_documents(chunks)
            
            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks")
            
            return {
                "success": True,
                "chunks_count": len(chunks),
                "storage_path": storage_path
            }
            
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "chunks_count": 0
            }
    
    def _get_supported_documents(self, folder_path: Path) -> List[Path]:
        """Get list of supported document files in folder"""
        supported_extensions = self.parser.get_supported_formats()
        document_files = []
        
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                document_files.append(file_path)
        
        return sorted(document_files)
    
    async def _upload_to_storage(
        self, 
        content: bytes, 
        filename: str, 
        container_name: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload document to Azure Storage with metadata"""
        
        try:
            # Get container client
            container_client = self.blob_service_client.get_container_client(container_name)
            
            # Create container if it doesn't exist
            await container_client.create_container_if_not_exists()
            
            # Create blob with metadata
            blob_name = f"documents/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"
            blob_client = container_client.get_blob_client(blob_name)
            
            # Prepare metadata for blob (convert to strings)
            blob_metadata = {
                k: str(v) if not isinstance(v, (list, dict)) else json.dumps(v)
                for k, v in metadata.items()
            }
            
            # Upload blob
            await blob_client.upload_blob(
                content,
                metadata=blob_metadata,
                overwrite=True
            )
            
            logger.info(f"Uploaded {filename} to Azure Storage: {blob_name}")
            return blob_name
            
        except Exception as e:
            logger.error(f"Failed to upload {filename} to Azure Storage: {str(e)}")
            raise
    
    async def get_processing_status(self, container_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of processed documents in Azure Storage"""
        
        try:
            container_name = container_name or settings.azure_storage_container_name
            container_client = self.blob_service_client.get_container_client(container_name)
            
            # List all blobs in container
            blobs = []
            async for blob in container_client.list_blobs():
                blobs.append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                    "metadata": blob.metadata or {}
                })
            
            # Get search index statistics
            search_stats = await self.search_service.get_index_statistics()
            
            return {
                "storage_container": container_name,
                "total_documents": len(blobs),
                "documents": blobs,
                "search_index_stats": search_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing status: {str(e)}")
            raise


# Factory function for dependency injection
def create_data_preprocessing_service() -> DataPreprocessingService:
    """Create data preprocessing service instance"""
    return DataPreprocessingService()


# Health check function
async def check_data_preprocessing_health() -> Dict[str, Any]:
    """Check data preprocessing service health"""
    try:
        service = DataPreprocessingService()
        
        # Test Azure Storage connection
        settings = get_settings()
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        
        # Test access to account info
        account_info = blob_service_client.get_account_information()
        
        # Test parser availability
        parser_info = service.parser.get_parser_info() if hasattr(service.parser, 'get_parser_info') else {"name": "Azure Document Intelligence"}
        
        return {
            "status": "healthy",
            "service": "DataPreprocessingService",
            "azure_storage_connected": True,
            "azure_storage_account": account_info.get("sku_name", "Unknown"),
            "parser": parser_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "DataPreprocessingService", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
