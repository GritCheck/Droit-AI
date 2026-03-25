"""
Enhanced Search API endpoints with OBO authentication and governance
Supports user folders, metadata filtering, and hierarchical search
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import asyncio
import time
from pydantic import BaseModel, Field
from pathlib import Path

from app.models.search import (
    SearchRequest, 
    SearchResult, 
    SearchSuggestionRequest,
    SearchSuggestionResponse,
    FacetedSearchRequest,
    FacetedSearchResponse
)
from app.services.search_service import GovernedSearchService, UserContext
from app.core.auth import verify_obo_token, get_user_from_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])
security = HTTPBearer()

settings = get_settings()


# Enhanced search models for user folders and metadata
class EnhancedSearchRequest(SearchRequest):
    """Enhanced search request with user folder and metadata filtering"""
    user_folders: Optional[List[str]] = Field(default=None, description="Specific user folders to search within")
    include_root_files: Optional[bool] = Field(default=True, description="Include files not in user folders")
    group_filter: Optional[List[str]] = Field(default=None, description="Filter by specific group IDs")
    file_types: Optional[List[str]] = Field(default=None, description="Filter by file types (pdf, docx, etc.)")
    date_range: Optional[Dict[str, str]] = Field(default=None, description="Date range filter (start_date, end_date)")


class UserFolderSearchResponse(BaseModel):
    """Response model for user folder-specific search"""
    success: bool
    query: str
    user_folders: Dict[str, SearchResult]
    total_results: int
    search_time: float
    user_context: Dict[str, Any]


class DocumentSourceResponse(BaseModel):
    """Response model for document source analysis"""
    success: bool
    sources: Dict[str, Any]
    user_folders: Dict[str, int]
    root_files: int
    total_documents: int


@router.post("/hybrid", response_model=SearchResult)
async def hybrid_search(
    request: SearchRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """
    Hybrid search combining semantic and keyword search
    Implements OBO authentication and security filtering
    """
    start_time = time.time()
    
    try:
        # Extract and validate OBO token
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Perform governed search
        result = await search_service.hybrid_search(request, user_context)
        
        # Calculate search time
        result.search_time = time.time() - start_time
        
        # Log search for analytics
        logger.info(f"Search completed for user {user_context.user_id}: "
                   f"{result.total_count} results in {result.search_time:.2f}s")
        
        return result
        
    except ValueError as e:
        # Authentication/authorization error
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    request: SearchSuggestionRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """Get search suggestions with security filtering"""
    try:
        # Validate OBO token
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Get suggestions
        suggestions = await search_service.get_search_suggestions(
            request.query, 
            user_context
        )
        
        return SearchSuggestionResponse(
            suggestions=suggestions,
            query=request.query
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Suggestions failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Suggestions failed: {str(e)}"
        )


@router.get("/facets", response_model=FacetedSearchResponse)
async def get_faceted_search(
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """Get faceted search results for filtering UI"""
    try:
        # Validate OBO token
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Get faceted results
        facets = await search_service.get_faceted_results(user_context)
        
        # Convert to available filters
        available_filters = {}
        for facet_name, facet_values in facets.items():
            available_filters[facet_name] = [
                str(value.get('value', '')) for value in facet_values[:10]
            ]
        
        return FacetedSearchResponse(
            facets=facets,
            available_filters=available_filters
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Faceted search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Faceted search failed: {str(e)}"
        )


@router.get("/health")
async def search_health():
    """Search service health check"""
    return {
        "status": "healthy",
        "service": "governed-search",
        "features": {
            "obo_authentication": True,
            "hybrid_search": True,
            "security_filtering": True,
            "content_safety": True,
            "semantic_search": True,
            "faceted_search": True
        },
        "azure_services": {
            "ai_search": bool(settings.azure_search_endpoint),
            "content_safety": bool(settings.azure_content_safety_endpoint),
            "openai": bool(settings.azure_openai_endpoint)
        }
    }


@router.post("/enhanced", response_model=SearchResult)
async def enhanced_hybrid_search(
    request: EnhancedSearchRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """
    Enhanced hybrid search with user folder and metadata filtering
    Supports hierarchical search across user folders and specific metadata filtering
    """
    start_time = time.time()
    
    try:
        # Extract and validate OBO token
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Validate enhanced search parameters
        if request.user_folders and len(request.user_folders) > 10:
            raise ValueError("Too many user folders specified (max 10)")
        
        if request.file_types and len(request.file_types) > 10:
            raise ValueError("Too many file types specified (max 10)")
        
        if request.top_k and (request.top_k < 1 or request.top_k > 100):
            raise ValueError("top_k must be between 1 and 100")
        
        # Build enhanced security filter with user folders and metadata
        enhanced_filter = _build_enhanced_security_filter(user_context, request)
        
        # Create modified search request with enhanced filter
        modified_request = SearchRequest(
            query=request.query,
            top_k=request.top_k,
            query_embedding=request.query_embedding,
            pure_vector=request.pure_vector,
            filters=enhanced_filter
        )
        
        # Perform governed search
        result = await search_service.hybrid_search(modified_request, user_context)
        
        # Apply post-search filtering if needed
        if request.user_folders or request.file_types:
            result = _apply_post_search_filters(result, request)
        
        # Calculate search time
        result.search_time = time.time() - start_time
        
        # Log enhanced search for analytics
        logger.info(f"Enhanced search completed for user {user_context.user_id}: "
                   f"{result.total_count} results in {result.search_time:.2f}s "
                   f"(folders: {request.user_folders}, file_types: {request.file_types})")
        
        return result
        
    except ValueError as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Enhanced search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced search failed: {str(e)}"
        )


@router.post("/user-folders", response_model=UserFolderSearchResponse)
async def search_user_folders(
    request: EnhancedSearchRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """
    Search across specific user folders with individual results per folder
    Returns organized results by user folder for better navigation
    """
    start_time = time.time()
    
    try:
        # Extract and validate OBO token
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Get user folders to search (or all accessible folders)
        target_folders = request.user_folders or await _get_accessible_user_folders(user_context)
        
        folder_results = {}
        total_results = 0
        
        # Search each folder separately
        for folder in target_folders:
            folder_filter = f"user_folder eq '{folder}'"
            
            # Create folder-specific search request
            folder_request = SearchRequest(
                query=request.query,
                top_k=request.top_k,
                query_embedding=request.query_embedding,
                pure_vector=request.pure_vector,
                filters=folder_filter
            )
            
            try:
                folder_result = await search_service.hybrid_search(folder_request, user_context)
                folder_results[folder] = folder_result
                total_results += folder_result.total_count
                
            except Exception as e:
                logger.warning(f"Failed to search folder {folder}: {str(e)}")
                folder_results[folder] = SearchResult(
                    documents=[],
                    total_count=0,
                    query=request.query,
                    search_time=0,
                    error=f"Folder search failed: {str(e)}"
                )
        
        search_time = time.time() - start_time
        
        return UserFolderSearchResponse(
            success=True,
            query=request.query,
            user_folders=folder_results,
            total_results=total_results,
            search_time=search_time,
            user_context={
                "user_id": user_context.user_id,
                "display_name": user_context.display_name,
                "group_count": len(user_context.group_ids),
                "searched_folders": target_folders
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"User folder search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User folder search failed: {str(e)}"
        )


@router.get("/document-sources", response_model=DocumentSourceResponse)
async def get_document_sources(
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """
    Get available document sources and user folders for the current user
    Helps build search UI with available filtering options
    """
    try:
        # Extract and validate OBO token
        access_token = credentials.credentials
        await search_service.extract_user_context(access_token)  # Validate but don't store
        
        # Get document sources from storage
        from app.services.azure_storage_service import get_storage_service
        storage_service = get_storage_service()
        
        documents = await storage_service.list_documents(max_results=1000)
        
        # Analyze document sources
        user_folders = {}
        root_files = 0
        file_types = {}
        
        for doc in documents:
            path = doc.get("path", doc.get("name", ""))
            
            if "/" in path:
                # User folder file
                folder, filename = path.split("/", 1)
                user_folders[folder] = user_folders.get(folder, 0) + 1
                
                # Count file types
                file_ext = Path(filename).suffix.lower()
                file_types[file_ext] = file_types.get(file_ext, 0) + 1
            else:
                # Root level file
                root_files += 1
                file_ext = Path(path).suffix.lower()
                file_types[file_ext] = file_types.get(file_ext, 0) + 1
        
        return DocumentSourceResponse(
            success=True,
            sources={
                "user_folders": user_folders,
                "root_files": root_files,
                "file_types": file_types,
                "total_documents": len(documents)
            },
            user_folders=user_folders,
            root_files=root_files,
            total_documents=len(documents)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Document sources analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document sources analysis failed: {str(e)}"
        )


@router.get("/user-context")
async def get_user_context(
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService)
):
    """Get current user's security context (for debugging)"""
    try:
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        return {
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "display_name": user_context.display_name,
            "department": user_context.department,
            "role": user_context.role,
            "security_clearance": user_context.security_clearance,
            "group_count": len(user_context.group_ids),
            "accessible_clearance_levels": search_service._get_allowed_clearance_levels(
                user_context.security_clearance
            )
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


# Helper functions for enhanced search
def _build_enhanced_security_filter(user_context: UserContext, request: EnhancedSearchRequest) -> str:
    """Build enhanced security filter with user folders and metadata"""
    filters = []
    
    # Base security filter from existing implementation
    if user_context.security_clearance:
        clearance_levels = ['public', 'internal', 'confidential']  # Simplified for now
        filters.append(f"security_clearance in ({', '.join([f'{level}' for level in clearance_levels])})")
    
    # Group-based filtering
    if user_context.group_ids:
        group_filters = [f"allowed_groups/any(g: g eq '{group_id}')" 
                       for group_id in user_context.group_ids[:10]]
        if group_filters:
            filters.append(f"({' or '.join(group_filters)})")
    
    # User folder filtering
    if request.user_folders:
        folder_filters = [f"user_folder eq '{folder}'" for folder in request.user_folders]
        filters.append(f"({' or '.join(folder_filters)})")
    elif not request.include_root_files:
        filters.append("user_folder ne null")
    
    # File type filtering
    if request.file_types:
        type_filters = [f"file_type eq '{file_type}'" for file_type in request.file_types]
        filters.append(f"({' or '.join(type_filters)})")
    
    # Date range filtering
    if request.date_range:
        date_parts = []
        if request.date_range.get("start_date"):
            date_parts.append(f"ingestion_timestamp ge {request.date_range['start_date']}")
        if request.date_range.get("end_date"):
            date_parts.append(f"ingestion_timestamp le {request.date_range['end_date']}")
        if date_parts:
            filters.append(f"({' and '.join(date_parts)})")
    
    # Group filter for specific groups
    if request.group_filter:
        group_filter_parts = [f"group_ids/any(g: g eq '{group}')" for group in request.group_filter]
        filters.append(f"({' or '.join(group_filter_parts)})")
    
    return " and ".join(filters) if filters else ""


def _apply_post_search_filters(result: SearchResult, request: EnhancedSearchRequest) -> SearchResult:
    """Apply additional filtering after search if needed"""
    if not request.user_folders and not request.file_types:
        return result
    
    filtered_documents = []
    
    for doc in result.documents:
        # Check user folder filter
        doc_folder = getattr(doc.metadata, 'user_folder', None) if hasattr(doc, 'metadata') else None
        if request.user_folders and doc_folder not in request.user_folders:
            continue
        
        # Check file type filter
        doc_type = getattr(doc.metadata, 'file_type', None) if hasattr(doc, 'metadata') else None
        if request.file_types and doc_type not in request.file_types:
            continue
        
        filtered_documents.append(doc)
    
    result.documents = filtered_documents
    result.total_count = len(filtered_documents)
    
    return result


async def _get_accessible_user_folders(user_context: UserContext) -> List[str]:
    """Get list of user folders accessible to the current user"""
    try:
        from app.services.azure_storage_service import get_storage_service
        storage_service = get_storage_service()
        
        documents = await storage_service.list_documents(max_results=1000)
        
        # Extract unique user folders
        user_folders = set()
        for doc in documents:
            path = doc.get("path", doc.get("name", ""))
            if "/" in path:
                folder, _ = path.split("/", 1)
                user_folders.add(folder)
        
        # For now, return all folders (in production, filter by user permissions)
        return list(user_folders)
        
    except Exception as e:
        logger.error(f"Failed to get accessible user folders: {str(e)}")
        return []
