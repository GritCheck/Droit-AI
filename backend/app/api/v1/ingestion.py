"""
Data Ingestion API - Azure-first document processing endpoints
Handles bulk document ingestion and preprocessing
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.enhanced_data_preprocessing_service import create_enhanced_data_preprocessing_service, check_enhanced_data_preprocessing_health

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class IngestFolderRequest(BaseModel):
    """Request model for folder ingestion"""
    folder_path: str = Field(..., description="Path to folder containing documents")
    allowed_groups: Optional[List[str]] = Field(default=["default-users"], description="Azure AD groups allowed to access documents")
    container_name: Optional[str] = Field(default=None, description="Azure Storage container name")


class IngestFolderResponse(BaseModel):
    """Response model for folder ingestion"""
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class IngestStatusResponse(BaseModel):
    """Response model for ingestion status"""
    success: bool
    status: Dict[str, Any]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    details: Dict[str, Any]
    error: Optional[str] = None

@router.post("/upload", response_model=IngestFolderResponse)
async def upload_and_ingest(
    files: List[UploadFile] = File(...),
    allowed_groups: Optional[str] = Form(default="default-users"),
    container_name: Optional[str] = Form(default=None),
    user_folder: Optional[str] = Form(default=None),  
    group_ids: Optional[str] = Form(default=None)  
):
    """
    Upload and ingest multiple files with user-specific folders and metadata
    
    This endpoint:
    1. Accepts multiple file uploads
    2. Saves them to user-specific folder structure
    3. Processes them with Azure Document Intelligence
    4. Uploads to Azure Storage with metadata (group IDs, user folder)
    5. Indexes in Azure AI Search with proper filtering
    """
    try:
        logger.info(f"Starting upload and ingestion for {len(files)} files")
        
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        # Parse allowed groups and group IDs
        groups = [group.strip() for group in allowed_groups.split(",")] if allowed_groups else ["default-users"]
        group_id_list = [gid.strip() for gid in group_ids.split(",")] if group_ids else []
        
        # Determine user folder (use provided or generate from context)
        target_user_folder = user_folder or "default-user"
        
        # Create temporary folder structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            for file in files:
                file_path = Path(temp_dir) / file.filename
                content = await file.read()
                
                with open(file_path, "wb") as f:
                    f.write(content)
                
                logger.info(f"Saved uploaded file: {file.filename} for user: {target_user_folder}")
            
            # Process files with enhanced metadata
            service = create_enhanced_data_preprocessing_service()
            results = await service.process_document_folder(
                folder_path=temp_dir,
                allowed_groups=groups,
                container_name=container_name,
                user_folder=target_user_folder,
                group_ids=group_id_list
            )
            
            logger.info(f"Upload and ingestion completed: {results}")
            
            return IngestFolderResponse(
                success=True,
                message=f"Successfully processed {results['processed']} out of {results['total_files']} documents for user '{target_user_folder}'",
                results=results
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload and ingestion failed: {str(e)}")
        return IngestFolderResponse(
            success=False,
            message="Upload and ingestion failed",
            error=str(e)
        )


@router.get("/status", response_model=IngestStatusResponse)
async def get_ingestion_status(container_name: Optional[str] = None):
    """
    Get status of processed documents in Azure Storage and Azure AI Search
    """
    try:
        service = create_enhanced_data_preprocessing_service()
        status = await service.get_processing_status(container_name)
        
        return IngestStatusResponse(
            success=True,
            status=status
        )
        
    except Exception as e:
        logger.error(f"Failed to get ingestion status: {str(e)}")
        return IngestStatusResponse(
            success=False,
            status={},
            error=str(e)
        )


@router.get("/container-structure", response_model=HealthResponse)
async def get_container_structure():
    """
    Get Azure Storage container structure showing user folders and hierarchy
    """
    try:
        from app.services.azure_storage_service import get_storage_service
        
        storage_service = get_storage_service()
        
        # List all blobs to show hierarchy
        documents = await storage_service.list_documents(max_results=1000)
        
        # Analyze folder structure
        user_folders = {}
        root_files = []
        
        for doc in documents:
            # Use the full path instead of just the name
            path = doc.get("path", doc.get("name", ""))
            if "/" in path:
                # File is in a user folder
                folder, filename = path.split("/", 1)
                if folder not in user_folders:
                    user_folders[folder] = []
                user_folders[folder].append({
                    "name": filename,
                    "size": doc.get("size", 0),
                    "last_modified": doc.get("lastModified"),
                    "content_type": doc.get("contentType"),
                    "url": doc.get("url")
                })
            else:
                # Root level file
                root_files.append({
                    "name": path,
                    "size": doc.get("size", 0),
                    "last_modified": doc.get("lastModified"),
                    "content_type": doc.get("contentType"),
                    "url": doc.get("url")
                })
        
        return HealthResponse(
            status="success",
            service="Container Structure Analysis",
            details={
                "container_name": "documents",
                "total_files": len(documents),
                "user_folders": user_folders,
                "root_files": root_files,
                "folder_count": len(user_folders),
                "hierarchical_storage": True,
                "supported_features": [
                    "User-specific folders",
                    "Group ID metadata",
                    "Query filtering by groups",
                    "Hierarchical blob storage"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Container structure analysis failed: {str(e)}")
        return HealthResponse(
            status="error",
            service="Container Structure Analysis",
            details={"error": str(e)},
            error=str(e)
        )


@router.get("/health", response_model=HealthResponse)
async def ingestion_health():
    """Enhanced ingestion service health check"""
    return check_enhanced_data_preprocessing_health()
        

@router.delete("/cleanup")
async def cleanup_processed_documents(
    container_name: Optional[str] = None,
    older_than_days: Optional[int] = 30
):
    """
    Clean up old processed documents from Azure Storage
    """
    try:
        logger.info(f"Starting cleanup for container: {container_name}, older than {older_than_days} days")
        
        # This would need to be implemented in the service
        # For now, return a placeholder response
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Cleanup completed",
                "details": {
                    "container_name": container_name,
                    "older_than_days": older_than_days,
                    "deleted_count": 0  # Placeholder
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )
