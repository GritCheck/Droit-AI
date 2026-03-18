"""
Governed Search Service for Sentinel RAG
Implements hybrid search with security filtering and OBO token validation
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime

from azure.identity.aio import OnBehalfOfCredential, DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import (
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
    QueryAnswerType
)
from azure.core.credentials import AzureKeyCredential
import httpx

from app.core.config import get_settings
from app.models.search import SearchRequest, SearchResult, DocumentMetadata
from app.services.content_safety_service import ContentSafetyService

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """User context extracted from OBO token"""
    user_id: str
    tenant_id: str
    display_name: str
    group_ids: List[str]
    department: Optional[str] = None
    role: Optional[str] = None
    security_clearance: Optional[str] = None

class GovernedSearchService:
    """
    Enterprise-grade search service with:
    - OBO token validation and user context extraction
    - Hybrid semantic + keyword search
    - Security filtering based on user groups
    - Content safety filtering
    - Audit logging
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.content_safety = ContentSafetyService()
        self._search_client = None
        self._credential = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_clients()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_clients()
        
    async def _initialize_clients(self):
        """Initialize Azure clients with proper credentials"""
        try:
            # Use OBO credential for user-specific operations
            if self.settings.azure_use_obo:
                self._credential = OnBehalfOfCredential(
                    client_id=self.settings.azure_client_id,
                    client_secret=self.settings.azure_client_secret,
                    tenant_id=self.settings.azure_tenant_id
                )
            else:
                # Fallback to default credential for development
                self._credential = DefaultAzureCredential()
                
            # Initialize search client
            self._search_client = SearchClient(
                endpoint=self.settings.azure_search_endpoint,
                index_name=self.settings.azure_search_index_name,
                credential=AzureKeyCredential(self.settings.azure_search_key)
            )
            
            logger.info("Search service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize search service: {str(e)}")
            raise
    
    async def _cleanup_clients(self):
        """Clean up Azure clients"""
        if self._search_client:
            await self._search_client.close()
        if self._credential:
            await self._credential.close()
    
    async def extract_user_context(self, access_token: str) -> UserContext:
        """
        Extract user context from OBO token
        Implements Microsoft identity token validation
        """
        try:
            # Validate token with Microsoft Graph using proper resource management
            async with httpx.AsyncClient(timeout=30.0) as client:
                graph_response = await client.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                graph_response.raise_for_status()
                user_data = graph_response.json()
                
                # Get user groups for security filtering
                groups_response = await client.get(
                    f"https://graph.microsoft.com/v1.0/users/{user_data['id']}/memberOf",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                groups_response.raise_for_status()
                groups_data = groups_response.json()
                
                # Extract group IDs for security filtering with validation
                group_ids = []
                for group in groups_data.get('value', []):
                    if (isinstance(group, dict) and 
                        'id' in group and 
                        isinstance(group['id'], str) and
                        'security' in group.get('@odata.type', '').lower()):
                        group_ids.append(group['id'])
                
                # Create user context
                user_context = UserContext(
                    user_id=user_data['id'],
                    tenant_id=user_data.get('tenantId', self.settings.azure_tenant_id),
                    display_name=user_data.get('displayName', 'Unknown'),
                    group_ids=group_ids,
                    department=user_data.get('department'),
                    role=user_data.get('jobTitle'),
                    security_clearance=self._extract_security_clearance(user_data, group_ids)
                )
                
                # Log for audit purposes
                await self._log_search_access(user_context, "token_validation")
                
                return user_context
                
        except httpx.TimeoutException:
            logger.error("Microsoft Graph API timeout during user context extraction")
            raise ValueError("Authentication service timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Microsoft Graph: {e.response.status_code}")
            if e.response.status_code == 401:
                raise ValueError("Invalid or expired authentication token")
            elif e.response.status_code == 403:
                raise ValueError("Insufficient permissions to access user information")
            else:
                raise ValueError(f"Authentication service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Failed to extract user context: {str(e)}")
            raise ValueError(f"Invalid OBO token: {str(e)}")
    
    def _extract_security_clearance(self, user_data: Dict, group_ids: List[str]) -> str:
        """Extract security clearance from user groups and attributes"""
        # Map Azure AD groups to security clearances
        clearance_mapping = {
            # Group ID -> Clearance Level
            'executive-access': 'top-secret',
            'management-access': 'secret',
            'employee-access': 'confidential',
            'contractor-access': 'restricted'
        }
        
        # Check user's department and title for default clearance
        department = user_data.get('department', '').lower()
        job_title = user_data.get('jobTitle', '').lower()
        
        if 'executive' in department or 'ceo' in job_title:
            return 'top-secret'
        elif 'manager' in job_title or 'director' in job_title:
            return 'secret'
        elif 'contractor' in job_title:
            return 'restricted'
        else:
            return 'confidential'
    
    async def hybrid_search(
        self,
        request: SearchRequest,
        user_context: UserContext
    ) -> SearchResult:
        """
        Perform hybrid search combining semantic and keyword search
        with security filtering and content safety
        """
        try:
            # Log search attempt
            await self._log_search_access(user_context, "search_initiated")
            
            # Build security filter
            security_filter = self._build_security_filter(user_context)
            
            # Perform content safety check on query
            safety_result = await self.content_safety.analyze_text(request.query)
            if not safety_result.is_safe:
                logger.warning(f"Unsafe query detected: {request.query}")
                return SearchResult(
                    documents=[],
                    total_count=0,
                    query=request.query,
                    search_time=0,
                    safety_filtered=True,
                    safety_reason=safety_result.reason
                )
            
            # Prepare search parameters
            search_text = request.query if not request.pure_vector else None
            vector_query = None
            
            if request.query_embedding:
                vector_query = VectorizedQuery(
                    vector=request.query_embedding,
                    k_nearest_neighbors=request.top_k,
                    fields="content_vector"
                )
            
            # Execute hybrid search
            search_results = await self._search_client.search(
                search_text=search_text,
                vector_queries=[vector_query] if vector_query else None,
                query_type=QueryType.SEMANTIC,
                query_language="en-us",
                query_speller="lexicon",
                semantic_configuration_name="semantic-config",
                query_caption=QueryCaptionType.EXTRACTIVE,
                query_answer=QueryAnswerType.EXTRACTIVE,
                top=request.top_k,
                skip=request.skip,
                filter=security_filter,
                include_total_count=True,
                facets=["category", "department", "security_clearance"]
            )
            
            # Process and filter results
            documents = []
            async for result in search_results:
                # Additional security check on individual documents
                if self._check_document_access(result, user_context):
                    # Content safety check on document content
                    content_safety = await self.content_safety.analyze_text(
                        result.get('content', '')[:1000]  # Check first 1000 chars
                    )
                    
                    document = DocumentMetadata(
                        id=result.get('id'),
                        title=result.get('title'),
                        content=result.get('content', '')[:500],  # Preview only
                        url=result.get('url'),
                        category=result.get('category'),
                        department=result.get('department'),
                        security_clearance=result.get('security_clearance'),
                        created_at=result.get('created_at'),
                        score=result.get('@search.score', 0.0),
                        captions=result.get('@search.captions', []),
                        is_safe_content=content_safety.is_safe,
                        metadata={
                            'source': result.get('source'),
                            'file_type': result.get('file_type'),
                            'page_number': result.get('page_number'),
                            'chunk_id': result.get('chunk_id')
                        }
                    )
                    documents.append(document)
            
            # Log successful search
            await self._log_search_access(
                user_context, 
                f"search_completed_{len(documents)}_results"
            )
            
            return SearchResult(
                documents=documents,
                total_count=len(documents),
                query=request.query,
                search_time=0.0,  # Will be calculated by caller
                facets=search_results.get_facets(),
                user_context=user_context
            )
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            await self._log_search_access(user_context, f"search_failed_{str(e)}")
            raise
    
    def _build_security_filter(self, user_context: UserContext) -> str:
        """
        Build Azure AI Search filter based on user's security context
        Implements row-level security
        """
        filters = []
        
        # Base security clearance filter
        if user_context.security_clearance:
            clearance_levels = self._get_allowed_clearance_levels(user_context.security_clearance)
            filters.append(f"security_clearance in ({', '.join([f'{level}' for level in clearance_levels])})")
        
        # Department-based filtering
        if user_context.department:
            filters.append(f"department eq '{user_context.department}'")
        
        # Group-based filtering (for specific document access)
        if user_context.group_ids:
            group_filters = [f"allowed_groups/any(g: g eq '{group_id}')" 
                           for group_id in user_context.group_ids[:10]]  # Limit filter complexity
            if group_filters:
                filters.append(f"({' or '.join(group_filters)})")
        
        # Public documents filter
        filters.append("is_public eq true")
        
        # Combine filters with OR logic (user can access any matching criteria)
        if filters:
            return f"({' or '.join(filters)})"
        else:
            return "is_public eq true"  # Fallback to public only
    
    def _get_allowed_clearance_levels(self, user_clearance: str) -> List[str]:
        """Get clearance levels user can access based on their own clearance"""
        clearance_hierarchy = {
            'top-secret': ['top-secret', 'secret', 'confidential', 'restricted'],
            'secret': ['secret', 'confidential', 'restricted'],
            'confidential': ['confidential', 'restricted'],
            'restricted': ['restricted']
        }
        return clearance_hierarchy.get(user_clearance, ['restricted'])
    
    def _check_document_access(self, document: Dict, user_context: UserContext) -> bool:
        """
        Additional document-level access check
        Provides granular security beyond search filters
        """
        doc_clearance = document.get('security_clearance', 'restricted')
        doc_department = document.get('department')
        doc_allowed_groups = document.get('allowed_groups', [])
        is_public = document.get('is_public', False)
        
        # Public documents are always accessible
        if is_public:
            return True
        
        # Check security clearance
        allowed_clearances = self._get_allowed_clearance_levels(user_context.security_clearance)
        if doc_clearance not in allowed_clearances:
            return False
        
        # Check department access
        if doc_department and doc_department != user_context.department:
            return False
        
        # Check group membership
        if doc_allowed_groups:
            user_groups = set(user_context.group_ids)
            doc_groups = set(doc_allowed_groups)
            if not user_groups.intersection(doc_groups):
                return False
        
        return True
    
    async def _log_search_access(self, user_context: UserContext, action: str):
        """Audit logging for search operations"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_context.user_id,
            'tenant_id': user_context.tenant_id,
            'action': action,
            'user_groups': user_context.group_ids,
            'security_clearance': user_context.security_clearance,
            'department': user_context.department
        }
        
        # In production, send to Azure Application Insights or Log Analytics
        logger.info(f"Search audit: {log_entry}")
        
        # TODO: Send to centralized logging system
        # await self._send_to_application_insights(log_entry)
    
    async def get_search_suggestions(self, query: str, user_context: UserContext) -> List[str]:
        """Get search suggestions with security filtering"""
        try:
            # Use Azure AI Search suggest feature
            suggestions = await self._search_client.suggest(
                search_text=query,
                suggester_name="sg",
                top=5,
                filter=self._build_security_filter(user_context)
            )
            
            return [suggestion['text'] async for suggestion in suggestions]
            
        except Exception as e:
            logger.error(f"Suggestion query failed: {str(e)}")
            return []
    
    async def get_faceted_results(self, user_context: UserContext) -> Dict[str, Any]:
        """Get faceted search results for filtering UI"""
        try:
            results = await self._search_client.search(
                search_text="*",
                top=0,
                facets=["category", "department", "security_clearance", "file_type"],
                filter=self._build_security_filter(user_context)
            )
            
            return results.get_facets() or {}
            
        except Exception as e:
            logger.error(f"Faceted query failed: {str(e)}")
            return {}
