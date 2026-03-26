"""
Azure Storage Service Integration
Real-time document management from Azure Blob Storage
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Try to import Azure Storage SDK
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_STORAGE_AVAILABLE = True
    
    # Reduce Azure Storage logging verbosity
    logging.getLogger('azure.storage.blob').setLevel(logging.WARNING)
    
except ImportError as e:
    logger.warning(f"Azure Storage SDK not available: {e}")
    AZURE_STORAGE_AVAILABLE = False


class AzureStorageService:
    """
    Real-time document management from Azure Blob Storage
    Integrates with Azure Storage for document operations
    """
    
    def __init__(self):
        """Initialize Azure Storage service"""
        if not AZURE_STORAGE_AVAILABLE:
            logger.warning("Azure Storage SDK not available")
            self.blob_service_client = None
            return
            
        try:
            # Use Managed Identity for deployed app, Client Secret for local dev
            from azure.identity import DefaultAzureCredential, ClientSecretCredential
            
            # Check if running in Azure (managed identity available)
            try:
                # Try Managed Identity first (for deployed app)
                credential = DefaultAzureCredential(
                    exclude_environment_credential=True,
                    exclude_managed_identity_credential=False,
                    exclude_shared_token_cache_credential=True,
                    exclude_visual_studio_code_credential=True,
                    exclude_visual_studio_credential=True,
                    exclude_azure_cli_credential=True,
                    exclude_interactive_browser_credential=True
                )
                logger.info("Using Managed Identity credential for Azure Storage")
            except Exception as e:
                logger.error(f"Managed Identity failed: {str(e)}")
                # Fallback to Client Secret for local development
                if (settings.azure_client_id and settings.azure_client_secret and settings.azure_tenant_id):
                    try:
                        credential = ClientSecretCredential(
                            tenant_id=settings.azure_tenant_id,
                            client_id=settings.azure_client_id,
                            client_secret=settings.azure_client_secret
                        )
                        logger.info("Using Client Secret credential for Azure Storage (local dev)")
                    except Exception as ce:
                        logger.error(f"Client Secret failed: {str(ce)}")
                        logger.warning("No Azure credentials available for Storage")
                        self.blob_service_client = None
                        return
                else:
                    logger.warning("No Azure credentials available for Storage")
                    self.blob_service_client = None
                    return
            
            # Initialize Blob Service Client
            account_url = f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential
            )
            
            # Test connection
            self.blob_service_client.get_account_information()
            logger.info("Azure Storage service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage service: {str(e)}")
            self.blob_service_client = None
    
    def __del__(self):
        """Cleanup resources when service is destroyed"""
        if self.blob_service_client:
            try:
                self.blob_service_client.close()
                logger.info("Azure Storage service client closed")
            except Exception as e:
                logger.warning(f"Error closing Storage client: {str(e)}")
    
    def close(self):
        """Explicit cleanup method"""
        self.__del__()
    
    async def list_documents(self, prefix: str = "", max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List documents from Azure Blob Storage
        """
        try:
            if not self.blob_service_client:
                logger.warning("Blob service client not initialized, returning fallback data")
                return self._get_fallback_documents()
            
            logger.info(f"Attempting to list documents from container: {settings.azure_storage_container_name}")
            
            # Get container client
            container_client = self.blob_service_client.get_container_client(
                settings.azure_storage_container_name
            )
            
            # Check if container exists
            if not container_client.exists():
                logger.warning(f"Container {settings.azure_storage_container_name} does not exist")
                return self._get_fallback_documents()
            
            logger.info(f"Container exists, listing blobs with prefix: '{prefix}'")
            
            # List blobs (max_results parameter doesn't exist in this SDK version)
            documents = []
            blob_list = container_client.list_blobs(name_starts_with=prefix)
            
            blob_count = 0
            for blob in blob_list:
                blob_count += 1
                logger.info(f"Found blob: {blob.name}, size: {blob.size}")
                
                # Get blob properties
                blob_client = container_client.get_blob_client(blob.name)
                properties = blob_client.get_blob_properties()
                
                document_data = {
                    "id": blob.name,
                    "name": blob.name.split("/")[-1] if "/" in blob.name else blob.name,
                    "path": blob.name,
                    "size": blob.size,
                    "contentType": properties.content_settings.content_type if properties.content_settings else "application/octet-stream",
                    "lastModified": blob.last_modified.isoformat() if blob.last_modified else datetime.utcnow().isoformat(),
                    "created": properties.creation_time.isoformat() if properties.creation_time else datetime.utcnow().isoformat(),
                    "etag": properties.etag if properties.etag else "",
                    "metadata": properties.metadata if properties.metadata else {},
                    "url": f"https://{settings.azure_storage_account_name}.blob.core.windows.net/{settings.azure_storage_container_name}/{blob.name}"
                }
                documents.append(document_data)
            
            logger.info(f"Successfully retrieved {blob_count} blobs from Azure Storage")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents from Azure Storage: {str(e)}")
            logger.info("Falling back to mock data")
            return self._get_fallback_documents()
    
    async def get_document(self, document_name: str) -> Dict[str, Any]:
        """
        Get a specific document from Azure Blob Storage
        """
        try:
            if not self.blob_service_client:
                logger.warning("Blob service client not initialized, returning fallback data")
                return self._get_fallback_document(document_name)
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=settings.azure_storage_container_name,
                blob=document_name
            )
            
            # Check if blob exists
            if not blob_client.exists():
                return {"error": "Document not found"}
            
            # Get blob properties
            properties = blob_client.get_blob_properties()
            
            document_data = {
                "id": document_name,
                "name": document_name.split("/")[-1] if "/" in document_name else document_name,
                "path": document_name,
                "size": properties.size,
                "contentType": properties.content_settings.content_type if properties.content_settings else "application/octet-stream",
                "lastModified": properties.last_modified.isoformat() if properties.last_modified else datetime.utcnow().isoformat(),
                "created": properties.creation_time.isoformat() if properties.creation_time else datetime.utcnow().isoformat(),
                "etag": properties.etag if properties.etag else "",
                "metadata": properties.metadata if properties.metadata else {},
                "url": f"https://{settings.azure_storage_account_name}.blob.core.windows.net/{settings.azure_storage_container_name}/{document_name}",
                "downloadUrl": blob_client.url if hasattr(blob_client, 'url') else f"https://{settings.azure_storage_account_name}.blob.core.windows.net/{settings.azure_storage_container_name}/{document_name}"
            }
            
            logger.info(f"Retrieved document: {document_name}")
            return document_data
            
        except Exception as e:
            logger.error(f"Failed to get document from Azure Storage: {str(e)}")
            return self._get_fallback_document(document_name)
    
    async def upload_document(self, document_name: str, content: bytes, content_type: str = "application/octet-stream", metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Upload a document to Azure Blob Storage
        """
        try:
            if not self.blob_service_client:
                logger.warning("Blob service client not initialized")
                return {"error": "Storage service not available"}
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=settings.azure_storage_container_name,
                blob=document_name
            )
            
            # Upload blob
            blob_client.upload_blob(
                content=content,
                content_settings= {"content_type": content_type},
                metadata=metadata or {},
                overwrite=True
            )
            
            # Get uploaded document info
            properties = blob_client.get_blob_properties()
            
            document_data = {
                "id": document_name,
                "name": document_name.split("/")[-1] if "/" in document_name else document_name,
                "path": document_name,
                "size": properties.size,
                "contentType": properties.content_settings.content_type if properties.content_settings else content_type,
                "lastModified": properties.last_modified.isoformat() if properties.last_modified else datetime.utcnow().isoformat(),
                "created": properties.creation_time.isoformat() if properties.creation_time else datetime.utcnow().isoformat(),
                "etag": properties.etag if properties.etag else "",
                "metadata": properties.metadata if properties.metadata else {},
                "url": f"https://{settings.azure_storage_account_name}.blob.core.windows.net/{settings.azure_storage_container_name}/{document_name}"
            }
            
            logger.info(f"Uploaded document: {document_name}")
            return document_data
            
        except Exception as e:
            logger.error(f"Failed to upload document to Azure Storage: {str(e)}")
            return {"error": f"Upload failed: {str(e)}"}
    
    async def get_storage_usage(self) -> Dict[str, Any]:
        """
        Calculate total storage usage in the container
        Returns storage metrics for the ingestion dashboard
        """
        if not self.blob_service_client:
            logger.warning("Azure Storage client not available, using fallback data")
            return {
                "title": "Azure Data Lake (ADLS)",
                "value": 24000000000,  # GB / 10
                "total": 24000000000,  # GB
                "icon": "/assets/icons/apps/ic-app-azure.svg"
            }
        
        try:
            # Get container client
            container_client = self.blob_service_client.get_container_client(
                settings.azure_storage_container_name
            )
            
            total_size = 0
            file_count = 0
            
            # List all blobs and calculate total size
            blobs = container_client.list_blobs()
            
            for blob in blobs:
                total_size += blob.size
                file_count += 1
            
            logger.info(f"Successfully calculated storage usage: {total_size} bytes across {file_count} files")
            
            return {
                "title": "Azure Data Lake (ADLS)",
                "value": total_size,
                "total": total_size,
                "icon": "/assets/icons/apps/ic-app-azure.svg"
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage usage: {str(e)}")
            # Return fallback data on error
            return {
                "title": "Azure Data Lake (ADLS)",
                "value": 24000000000,  # GB / 10
                "total": 24000000000,  # GB
                "icon": "/assets/icons/apps/ic-app-azure.svg"
            }

    async def delete_document(self, document_name: str) -> Dict[str, Any]:
        """
        Delete a document from Azure Blob Storage
        """
        try:
            if not self.blob_service_client:
                logger.warning("Blob service client not initialized")
                return {"error": "Storage service not available"}
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=settings.azure_storage_container_name,
                blob=document_name
            )
            
            # Delete blob
            blob_client.delete_blob()
            
            logger.info(f"Deleted document: {document_name}")
            return {"success": True, "message": f"Document {document_name} deleted successfully"}
            
        except Exception as e:
            logger.error(f"Failed to delete document from Azure Storage: {str(e)}")
            return {"error": f"Delete failed: {str(e)}"}
    
    def _get_fallback_documents(self) -> List[Dict[str, Any]]:
        """Get fallback documents when Azure Storage is not available"""
        return [
            {
                "id": "sample-document-1.pdf",
                "name": "sample-document-1.pdf",
                "path": "documents/sample-document-1.pdf",
                "size": 1024000,
                "contentType": "application/pdf",
                "lastModified": "2024-01-15T10:30:00Z",
                "created": "2024-01-10T09:00:00Z",
                "etag": "0x8D4BCC2E4835CD0",
                "metadata": {"category": "sample", "author": "system"},
                "url": "https://example.com/storage/documents/sample-document-1.pdf"
            },
            {
                "id": "sample-document-2.docx",
                "name": "sample-document-2.docx",
                "path": "documents/sample-document-2.docx",
                "size": 512000,
                "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "lastModified": "2024-01-14T15:45:00Z",
                "created": "2024-01-12T11:20:00Z",
                "etag": "0x8D4BCC2E4835CD1",
                "metadata": {"category": "sample", "author": "system"},
                "url": "https://example.com/storage/documents/sample-document-2.docx"
            }
        ]
    
    def _get_fallback_document(self, document_name: str) -> Dict[str, Any]:
        """Get fallback document when Azure Storage is not available"""
        return {
            "id": document_name,
            "name": document_name,
            "path": f"documents/{document_name}",
            "size": 1024000,
            "contentType": "application/pdf",
            "lastModified": "2024-01-15T10:30:00Z",
            "created": "2024-01-10T09:00:00Z",
            "etag": "0x8D4BCC2E4835CD0",
            "metadata": {"category": "sample", "author": "system"},
            "url": f"https://example.com/storage/documents/{document_name}",
            "error": "Using fallback data - Azure Storage not available"
        }


# Global service instance
_storage_service: Optional[AzureStorageService] = None


def get_storage_service() -> AzureStorageService:
    """Get global storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = AzureStorageService()
    return _storage_service


def check_azure_storage_health() -> Dict[str, Any]:
    """Check Azure Storage service health"""
    health = {
        "available": AZURE_STORAGE_AVAILABLE,
        "configured": bool(settings.azure_storage_connection_string or 
                          (settings.azure_storage_account_name and settings.azure_storage_account_key)),
        "container_name": settings.azure_storage_container_name,
        "account_name": settings.azure_storage_account_name
    }
    
    if _storage_service and _storage_service.blob_service_client:
        try:
            account_info = _storage_service.blob_service_client.get_account_information()
            health["account_info"] = {
                "sku": account_info.get("sku", "Unknown"),
                "kind": account_info.get("kind", "StorageV2")
            }
            health["status"] = "healthy"
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
    else:
        health["status"] = "not_initialized"
    
    return health
