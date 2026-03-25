"""
Documents API endpoints for serving Azure Storage documents
Real-time integration with Azure Blob Storage
"""

import logging
import re
import time
from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.services.azure_storage_service import get_storage_service
# from app.core.auth import get_current_user  # Temporarily commented for testing

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

# Mock data that matches the frontend structure
DOCUMENT_TYPES = ['PDF', 'DOCX', 'TXT', 'MD']
SECURITY_LEVELS = ['Low', 'Medium', 'High']
DOCUMENT_STATUSES = ['indexed', 'processing', 'failed', 'flagged']

# Configuration constants
DEFAULT_SESSION_TIMEOUT = 30  # minutes
DEFAULT_IDLE_TIMEOUT = 15      # minutes
DEFAULT_SUBSCRIBERS = 100
DEFAULT_VALIDITY_PERIOD = "30 days"

def handle_storage_error(error_response: Dict[str, Any]) -> HTTPException:
    """Standardized error handling for storage operations"""
    if "error" in error_response:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response["error"]
        )
    return None

def handle_not_found_error(resource_id: str) -> HTTPException:
    """Standardized 404 error handling"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document with ID '{resource_id}' not found"
    )

def sanitize_search_input(search_input: str) -> str:
    """
    Sanitize search input to prevent injection attacks and limit length
    """
    if not search_input:
        return ""
    
    # Remove potentially dangerous characters and patterns
    # This covers: < > " ' ; % & ( ) { } [ ] ` ~ ! @ # $ ^ * = + | \ 
    sanitized = re.sub(r'[<>"\'\;:%&\(\)\{\}\[\]`~!@#\$^\*=+\|\\]', '', search_input)
    
    # Remove common injection patterns
    sanitized = re.sub(r'(javascript:|data:|vbscript:|on\w+\s*=)', '', sanitized, flags=re.IGNORECASE)
    
    # Remove SQL injection patterns
    sanitized = re.sub(r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)', '', sanitized, flags=re.IGNORECASE)
    
    # Remove script tags and event handlers
    sanitized = re.sub(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
    
    # Limit length to prevent DoS attacks
    max_length = 100
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Strip whitespace and normalize
    sanitized = sanitized.strip()
    
    # Additional safety: ensure no control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
    
    return sanitized

def generate_mock_documents(count: int = 20) -> List[Dict[str, Any]]:
    """Generate mock documents matching the frontend structure"""
    documents = []
    for i in range(count):
        doc_id = f"doc-{i+1:03d}"
        doc_name = f"Document {i+1}"
        doc_type = DOCUMENT_TYPES[i % len(DOCUMENT_TYPES)]
        chunk_size = f"{512 + i * 256} tokens"
        last_synced = f"{i} hours ago"
        vector_dimensions = f"{768 + i * 256}d"
        security_level_number = (i % 3) + 1
        security_level = SECURITY_LEVELS[security_level_number - 1]
        status = DOCUMENT_STATUSES[i % len(DOCUMENT_STATUSES)]
        validity_period = f"{7 + i} days"
        features = f"Feature {i+1}, Feature {i+2}, Feature {i+3}"
        subscribers = [100, 200, 300, 400, 500][i % 5]
        description = f"This is document {i+1} with type {doc_type} and security level {security_level}"
        
        documents.append({
            "id": doc_id,
            "type": doc_type,
            "name": doc_name,
            "data_limit": chunk_size,
            "time_limit": last_synced,
            "rate_limit": vector_dimensions,
            "session_timeout": 30,  # number in minutes
            "idle_timeout": 15,     # number in minutes
            "price": security_level_number,
            "status": status,
            "validity_period": validity_period,
            "features": features,
            "subscribers": subscribers,
            "description": description,
            "created_at": f"2024-01-{(i % 28)+1:02d}T10:00:00Z",
            "updated_at": f"2024-01-{(i % 28)+1:02d}T{(i % 24):02d}:00:00Z"
        })
    
    return documents


@router.get("/")
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    type_filter: str = Query(None, alias="type"),
    search: str = Query(None),
    # current_user: dict = Depends(get_current_user),
    storage_service = Depends(get_storage_service)
) -> Dict[str, Any]:
    """
    Get documents from Azure Storage with optional filtering
    Real-time data from Azure Blob Storage
    """
    try:
        # Get real documents from Azure Storage
        azure_documents = await storage_service.list_documents(max_results=limit)
        
        # Convert Azure Storage documents to expected format
        converted_documents = []
        for doc in azure_documents:
            # Extract file extension for type with null safety
            name = doc.get("name", "")
            file_ext = name.split(".")[-1].upper() if "." in name else "Unknown"
            doc_type = file_ext if file_ext in DOCUMENT_TYPES else "Unknown"
            
            # Map content type to security level (simple heuristic)
            security_level = "Low"
            if any(keyword in name.lower() for keyword in ["confidential", "secret", "private"]):
                security_level = "High"
            elif any(keyword in name.lower() for keyword in ["internal", "restricted"]):
                security_level = "Medium"
            
            # Safe security level index lookup with fallback
            try:
                price = SECURITY_LEVELS.index(security_level) + 1
            except ValueError:
                logger.warning(f"Unknown security level '{security_level}', defaulting to Low")
                price = 1  # Default to Low security level
            
            converted_doc = {
                "id": doc["id"],
                "type": doc_type,
                "name": doc["name"],
                "data_limit": f"{doc['size']} bytes",
                "time_limit": doc["lastModified"],
                "rate_limit": f"{doc['size']}d",
                "session_timeout": DEFAULT_SESSION_TIMEOUT,
                "idle_timeout": DEFAULT_IDLE_TIMEOUT,
                "price": price,
                "status": "indexed",  # Assume indexed for now
                "validity_period": DEFAULT_VALIDITY_PERIOD,
                "features": f"Azure Storage, {doc_type}, {security_level}",
                "subscribers": DEFAULT_SUBSCRIBERS,  # Default value
                "description": f"Document stored in Azure Storage: {doc['name']}",
                "created_at": doc["created"],
                "updated_at": doc["lastModified"],
                "azure_metadata": {
                    "path": doc["path"],
                    "contentType": doc["contentType"],
                    "url": doc["url"],
                    "size": doc["size"],
                    "metadata": doc.get("metadata", {})
                }
            }
            converted_documents.append(converted_doc)
        
        # Apply filters
        filtered_documents = converted_documents
        
        if status and status != "all":
            filtered_documents = [doc for doc in filtered_documents if doc["status"] == status]
        
        if type_filter:
            # Handle comma-separated type filters
            type_filters = [t.strip() for t in type_filter.split(',') if t.strip()]
            filtered_documents = [doc for doc in filtered_documents if doc["type"] in type_filters]
        
        if search:
            # Input validation and sanitization
            search = sanitize_search_input(search)
            if search:
                search_lower = search.lower()
                filtered_documents = [doc for doc in filtered_documents 
                    if search_lower in doc["name"].lower() or search_lower in doc["description"].lower()]
        
        # Apply pagination
        total = len(filtered_documents)
        documents = filtered_documents[skip:skip + limit]
        
        logger.info(f"Retrieved {len(documents)} documents from Azure Storage (total: {total})")
        
        return {
            "documents": documents,
            "total": total,
            "skip": skip,
            "limit": limit,
            "filters": {
                "status": status,
                "type": type_filter,
                "search": search
            },
            "source": "azure_storage"
        }
        
    except Exception as e:
        logger.error(f"Failed to get documents from Azure Storage: {str(e)}")
        # Fallback to mock data if Azure Storage fails
        logger.info("Falling back to mock data")
        all_documents = generate_mock_documents(100)
        
        # Apply filters (same logic as before)
        filtered_documents = all_documents
        
        if status and status != "all":
            filtered_documents = [doc for doc in filtered_documents if doc["status"] == status]
        
        if type_filter:
            type_filters = [t.strip() for t in type_filter.split(',') if t.strip()]
            filtered_documents = [doc for doc in filtered_documents if doc["type"] in type_filters]
        
        if search:
            search = sanitize_search_input(search)
            if search:
                search_lower = search.lower()
                filtered_documents = [doc for doc in filtered_documents 
                    if search_lower in doc["name"].lower() or search_lower in doc["description"].lower()]
        
        total = len(filtered_documents)
        documents = filtered_documents[skip:skip + limit]
        
        return {
            "documents": documents,
            "total": total,
            "skip": skip,
            "limit": limit,
            "filters": {
                "status": status,
                "type": type_filter,
                "search": search
            },
            "source": "fallback_mock_data"
        }


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    # current_user: dict = Depends(get_current_user),
    storage_service = Depends(get_storage_service)
) -> Dict[str, Any]:
    """
    Get a specific document from Azure Storage
    Real-time data from Azure Blob Storage
    """
    try:
        # Get real document from Azure Storage
        document = await storage_service.get_document(document_id)
        
        if "error" in document:
            raise handle_not_found_error(document_id)
        
        # Convert to expected format
        name = document.get("name", "")
        file_ext = name.split(".")[-1].upper() if "." in name else "Unknown"
        doc_type = file_ext if file_ext in DOCUMENT_TYPES else "Unknown"
        
        # Map content type to security level
        security_level = "Low"
        if any(keyword in name.lower() for keyword in ["confidential", "secret", "private"]):
            security_level = "High"
        elif any(keyword in name.lower() for keyword in ["internal", "restricted"]):
            security_level = "Medium"
        
        # Safe security level index lookup with fallback
        try:
            price = SECURITY_LEVELS.index(security_level) + 1
        except ValueError:
            logger.warning(f"Unknown security level '{security_level}', defaulting to Low")
            price = 1  # Default to Low security level
        
        converted_doc = {
            "id": document["id"],
            "type": doc_type,
            "name": document["name"],
            "data_limit": f"{document['size']} bytes",
            "time_limit": document["lastModified"],
            "rate_limit": f"{document['size']}d",
            "session_timeout": DEFAULT_SESSION_TIMEOUT,
            "idle_timeout": DEFAULT_IDLE_TIMEOUT,
            "price": price,
            "status": "indexed",
            "validity_period": DEFAULT_VALIDITY_PERIOD,
            "features": f"Azure Storage, {doc_type}, {security_level}",
            "subscribers": DEFAULT_SUBSCRIBERS,
            "description": f"Document stored in Azure Storage: {document['name']}",
            "created_at": document["created"],
            "updated_at": document["lastModified"],
            "azure_metadata": {
                "path": document["path"],
                "contentType": document["contentType"],
                "url": document["url"],
                "size": document["size"],
                "metadata": document.get("metadata", {}),
                "downloadUrl": document.get("downloadUrl", document["url"])
            }
        }
        
        logger.info(f"Retrieved document: {document_id}")
        return converted_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    # current_user: dict = Depends(get_current_user),
    storage_service = Depends(get_storage_service)
) -> Dict[str, Any]:
    """
    Delete a document from Azure Storage
    Real-time integration with Azure Blob Storage
    """
    try:
        # Delete document from Azure Storage
        result = await storage_service.delete_document(document_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        logger.info(f"Deleted document: {document_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post("/{document_id}/reindex")
async def reindex_document(document_id: str) -> Dict[str, Any]:
    """
    Re-index a document in the vector store
    """
    try:
        documents = generate_mock_documents(100)
        document = next((doc for doc in documents if doc["id"] == document_id), None)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Simulate re-indexing
        logger.info(f"Re-indexing document: {document_id}")
        
        return {
            "message": f"Document {document_id} successfully re-indexed",
            "document_id": document_id,
            "reindexed_at": time.time(),
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to re-index document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-index document: {str(e)}"
        )


@router.get("/stats/overview")
async def get_document_stats(
    storage_service = Depends(get_storage_service)
) -> Dict[str, Any]:
    """
    Get document statistics overview from Azure Storage
    Real-time data from Azure Blob Storage
    """
    try:
        # Get real documents from Azure Storage
        azure_documents = await storage_service.list_documents(max_results=1000)
        
        # Convert to expected format for stats calculation
        converted_documents = []
        for doc in azure_documents:
            # Extract file extension for type
            file_ext = doc["name"].split(".")[-1].upper() if "." in doc["name"] else "Unknown"
            doc_type = file_ext if file_ext in DOCUMENT_TYPES else "Unknown"
            
            # Map content type to security level (simple heuristic)
            security_level = "Low"
            if any(keyword in doc["name"].lower() for keyword in ["confidential", "secret", "private"]):
                security_level = "High"
            elif any(keyword in doc["name"].lower() for keyword in ["internal", "restricted"]):
                security_level = "Medium"
            
            converted_doc = {
                "type": doc_type,
                "status": "indexed",  # Assume indexed for now
                "price": SECURITY_LEVELS.index(security_level) + 1,
                "subscribers": 100,  # Default value
                "size": doc["size"]
            }
            converted_documents.append(converted_doc)
        
        # Calculate statistics from real data
        total_documents = len(converted_documents)
        indexed_count = len([doc for doc in converted_documents if doc["status"] == "indexed"])
        processing_count = len([doc for doc in converted_documents if doc["status"] == "processing"])
        failed_count = len([doc for doc in converted_documents if doc["status"] == "failed"])
        flagged_count = len([doc for doc in converted_documents if doc["status"] == "flagged"])
        
        # Type distribution
        type_counts = {}
        for doc in converted_documents:
            doc_type = doc["type"]
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Security level distribution
        security_counts = {}
        for doc in converted_documents:
            security_level = SECURITY_LEVELS[doc["price"] - 1]
            security_counts[security_level] = security_counts.get(security_level, 0) + 1
        
        # Size statistics
        total_size = sum(doc["size"] for doc in converted_documents)
        avg_size = total_size / total_documents if total_documents > 0 else 0
        
        logger.info(f"Document statistics retrieved successfully from Azure Storage: {total_documents} documents")
        
        return {
            "total": total_documents,
            "by_status": {
                "indexed": indexed_count,
                "processing": processing_count,
                "failed": failed_count,
                "flagged": flagged_count
            },
            "by_type": type_counts,
            "by_security_level": security_counts,
            "total_subscribers": sum(doc["subscribers"] for doc in converted_documents),
            "storage_stats": {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_size_bytes": round(avg_size),
                "average_size_mb": round(avg_size / (1024 * 1024), 2)
            },
            "source": "azure_storage"
        }
        
    except Exception as e:
        logger.error(f"Failed to get document stats from Azure Storage: {str(e)}")
        # Fallback to mock data if Azure Storage fails
        logger.info("Falling back to mock data for statistics")
        documents = generate_mock_documents(100)
        
        total_documents = len(documents)
        indexed_count = len([doc for doc in documents if doc["status"] == "indexed"])
        processing_count = len([doc for doc in documents if doc["status"] == "processing"])
        failed_count = len([doc for doc in documents if doc["status"] == "failed"])
        flagged_count = len([doc for doc in documents if doc["status"] == "flagged"])
        
        type_counts = {}
        for doc in documents:
            doc_type = doc["type"]
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        security_counts = {}
        for doc in documents:
            security_level = SECURITY_LEVELS[doc["price"] - 1]
            security_counts[security_level] = security_counts.get(security_level, 0) + 1
        
        return {
            "total": total_documents,
            "by_status": {
                "indexed": indexed_count,
                "processing": processing_count,
                "failed": failed_count,
                "flagged": flagged_count
            },
            "by_type": type_counts,
            "by_security_level": security_counts,
            "total_subscribers": sum(doc["subscribers"] for doc in documents),
            "source": "fallback_mock_data"
        }


@router.get("/health")
async def documents_health() -> Dict[str, Any]:
    """Documents service health check"""
    from app.services.azure_storage_service import check_azure_storage_health
    
    storage_health = check_azure_storage_health()
    
    return {
        "status": "healthy" if storage_health.get("status") == "healthy" else "unhealthy",
        "service": "Documents API",
        "timestamp": time.time(),
        "endpoints": {
            "list": "/documents/",
            "detail": "/documents/{document_id}",
            "delete": "/documents/{document_id}",
            "reindex": "/documents/{document_id}/reindex",
            "stats": "/documents/stats/overview",
            "storage_health": "/documents/health/storage"
        },
        "storage_integration": storage_health,
        "data_source": "Azure Blob Storage with fallback to mock data"
    }


@router.get("/health/storage")
async def storage_health() -> Dict[str, Any]:
    """Azure Storage service health check"""
    from app.services.azure_storage_service import check_azure_storage_health
    
    health = check_azure_storage_health()
    return {
        "status": "healthy" if health.get("status") == "healthy" else "unhealthy",
        "service": "Azure Storage API",
        "timestamp": datetime.utcnow().timestamp(),
        "details": health
    }
