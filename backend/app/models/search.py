"""
Pydantic models for search requests and responses
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SearchRequest(BaseModel):
    """Search request with hybrid search capabilities"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    query_embedding: Optional[List[float]] = Field(None, description="Query embedding for vector search")
    top_k: int = Field(10, ge=1, le=50, description="Number of results to return")
    skip: int = Field(0, ge=0, le=1000, description="Number of results to skip")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")
    pure_vector: bool = Field(False, description="Use only vector search (no text)")
    include_facets: bool = Field(True, description="Include faceted search results")
    semantic_ranking: bool = Field(True, description="Use semantic ranking")


class DocumentMetadata(BaseModel):
    """Document metadata with security and governance information"""
    id: str
    title: str
    content: str
    url: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    security_clearance: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    score: float = 0.0
    captions: List[Dict[str, Any]] = Field(default_factory=list)
    is_safe_content: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SearchResult(BaseModel):
    """Search result with governance information"""
    documents: List[DocumentMetadata]
    total_count: int
    query: str
    search_time: float
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = None
    safety_filtered: bool = False
    safety_reason: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class SearchSuggestionRequest(BaseModel):
    """Request for search suggestions"""
    query: str = Field(..., min_length=1, max_length=100)
    top: int = Field(5, ge=1, le=10)


class SearchSuggestionResponse(BaseModel):
    """Search suggestions response"""
    suggestions: List[str]
    query: str


class FacetedSearchRequest(BaseModel):
    """Request for faceted search results"""
    filters: Optional[Dict[str, Any]] = None


class FacetedSearchResponse(BaseModel):
    """Faceted search results"""
    facets: Dict[str, List[Dict[str, Any]]]
    available_filters: Dict[str, List[str]]


class SearchAnalytics(BaseModel):
    """Search analytics for monitoring"""
    query: str
    user_id: str
    result_count: int
    search_time: float
    timestamp: datetime
    filters_used: List[str]
    clicked_documents: List[str] = Field(default_factory=list)


class SearchHealthCheck(BaseModel):
    """Search service health check"""
    status: str
    search_client_connected: bool
    azure_services_connected: bool
    last_search_time: Optional[float] = None
    total_searches: int = 0
    error_rate: float = 0.0
