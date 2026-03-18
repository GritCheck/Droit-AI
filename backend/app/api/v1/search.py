"""
Search API endpoints with OBO authentication and governance
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import asyncio
import time

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
