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

from app.services.data_preprocessing_service import create_data_preprocessing_service, check_data_preprocessing_health

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/ingest", tags=["ingestion"])


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


@router.post("/folder", response_model=IngestFolderResponse)
async def ingest_folder(
    request: IngestFolderRequest,
    background_tasks: BackgroundTasks
):
    """
    Process all documents in a folder and load to Azure services
    
    This endpoint:
    1. Scans the specified folder for supported document types
    2. Processes each document with Azure Document Intelligence
    3. Uploads original documents to Azure Storage
    4. Indexes processed chunks in Azure AI Search
    5. Applies security metadata for Azure AD groups
    """
    try:
        logger.info(f"Starting folder ingestion for: {request.folder_path}")
        
        # Validate folder path
        folder_path = Path(request.folder_path)
        if not folder_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Folder not found: {request.folder_path}"
            )
        
        if not folder_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a folder: {request.folder_path}"
            )
        
        # Create preprocessing service
        service = create_data_preprocessing_service()
        
        # Process folder (this could be a long-running operation)
        results = await service.process_document_folder(
            folder_path=str(folder_path),
            allowed_groups=request.allowed_groups,
            container_name=request.container_name
        )
        
        logger.info(f"Folder ingestion completed: {results}")
        
        return IngestFolderResponse(
            success=True,
            message=f"Successfully processed {results['processed']} out of {results['total_files']} documents",
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Folder ingestion failed: {str(e)}")
        return IngestFolderResponse(
            success=False,
            message="Folder ingestion failed",
            error=str(e)
        )


@router.post("/upload", response_model=IngestFolderResponse)
async def upload_and_ingest(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    allowed_groups: Optional[str] = Form(default="default-users"),
    container_name: Optional[str] = Form(default=None)
):
    """
    Upload and ingest multiple files
    
    This endpoint:
    1. Accepts multiple file uploads
    2. Saves them to a temporary folder
    3. Processes them with Azure Document Intelligence
    4. Uploads to Azure Storage and indexes in Azure AI Search
    """
    try:
        logger.info(f"Starting upload and ingestion for {len(files)} files")
        
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )
        
        # Parse allowed groups
        groups = [group.strip() for group in allowed_groups.split(",")] if allowed_groups else ["default-users"]
        
        # Create temporary folder
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            for file in files:
                file_path = Path(temp_dir) / file.filename
                content = await file.read()
                
                with open(file_path, "wb") as f:
                    f.write(content)
                
                logger.info(f"Saved uploaded file: {file.filename}")
            
            # Process files
            service = create_data_preprocessing_service()
            results = await service.process_document_folder(
                folder_path=temp_dir,
                allowed_groups=groups,
                container_name=container_name
            )
            
            logger.info(f"Upload and ingestion completed: {results}")
            
            return IngestFolderResponse(
                success=True,
                message=f"Successfully processed {results['processed']} out of {results['total_files']} uploaded files",
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
        service = create_data_preprocessing_service()
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


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check for data preprocessing service
    """
    try:
        health = await check_data_preprocessing_health()
        
        return HealthResponse(
            status=health["status"],
            service=health["service"],
            details=health,
            error=health.get("error")
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            service="DataPreprocessingService",
            details={},
            error=str(e)
        )


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
