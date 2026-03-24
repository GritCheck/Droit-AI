"""
Documents API endpoints for serving document registry data
"""

import logging
import re
import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

# Mock data that matches the frontend structure
DOCUMENT_TYPES = ['PDF', 'DOCX', 'TXT', 'MD']
SECURITY_LEVELS = ['Low', 'Medium', 'High']
DOCUMENT_STATUSES = ['indexed', 'processing', 'failed', 'flagged']

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
    search: str = Query(None)
) -> Dict[str, Any]:
    """
    Get documents with optional filtering
    """
    try:
        # Generate mock documents
        all_documents = generate_mock_documents(100)
        
        # Apply filters
        filtered_documents = all_documents
        
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
        
        logger.info(f"Retrieved {len(documents)} documents (total: {total})")
        
        return {
            "documents": documents,
            "total": total,
            "skip": skip,
            "limit": limit,
            "filters": {
                "status": status,
                "type": type_filter,
                "search": search
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(document_id: str) -> Dict[str, Any]:
    """
    Get a specific document by ID
    """
    try:
        documents = generate_mock_documents(100)
        document = next((doc for doc in documents if doc["id"] == document_id), None)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        logger.info(f"Retrieved document: {document_id}")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str) -> Dict[str, Any]:
    """
    Delete a document from the vector index
    """
    try:
        # In a real implementation, this would delete from Azure AI Search
        documents = generate_mock_documents(100)
        document = next((doc for doc in documents if doc["id"] == document_id), None)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Simulate deletion
        logger.info(f"Deleted document from vector index: {document_id}")
        
        return {
            "message": f"Document {document_id} successfully removed from vector index",
            "document_id": document_id,
            "deleted_at": time.time()
        }
        
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
async def get_document_stats() -> Dict[str, Any]:
    """
    Get document statistics overview
    """
    try:
        documents = generate_mock_documents(100)
        
        # Calculate statistics
        total_documents = len(documents)
        indexed_count = len([doc for doc in documents if doc["status"] == "indexed"])
        processing_count = len([doc for doc in documents if doc["status"] == "processing"])
        failed_count = len([doc for doc in documents if doc["status"] == "failed"])
        flagged_count = len([doc for doc in documents if doc["status"] == "flagged"])
        
        # Type distribution
        type_counts = {}
        for doc in documents:
            doc_type = doc["type"]
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Security level distribution
        security_counts = {}
        for doc in documents:
            security_level = SECURITY_LEVELS[doc["price"] - 1]
            security_counts[security_level] = security_counts.get(security_level, 0) + 1
        
        logger.info("Document statistics retrieved successfully")
        
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
            "total_subscribers": sum(doc["subscribers"] for doc in documents)
        }
        
    except Exception as e:
        logger.error(f"Failed to get document stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document statistics: {str(e)}"
        )


@router.get("/health")
async def documents_health() -> Dict[str, Any]:
    """Documents service health check"""
    return {
        "status": "healthy",
        "service": "Documents API",
        "timestamp": time.time(),
        "endpoints": {
            "list": "/documents/",
            "detail": "/documents/{document_id}",
            "delete": "/documents/{document_id}",
            "reindex": "/documents/{document_id}/reindex",
            "stats": "/documents/stats/overview"
        },
        "vector_store": "Azure AI Search",
        "total_documents": 100
    }
