import asyncio
import logging
import time
from typing import Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI, AsyncAzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from opencensus.ext.azure.log_exporter import AzureLogHandler
from app.core.config import get_settings
from app.core.embedder import LegalEmbedder


logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Application Insights if available
if settings.application_insights_connection_string:
    logger.addHandler(AzureLogHandler(connection_string=settings.application_insights_connection_string))
    logger.setLevel(logging.INFO)


class LegalRagService:
    def __init__(self):
        # Validate configuration
        if not settings.azure_search_endpoint:
            raise ValueError("AZURE_SEARCH_ENDPOINT not configured")
        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not configured")
            
        # Clients initialized with Managed Identity (DefaultAzureCredential)
        self.embedder = LegalEmbedder()
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_key)
        )
        self.openai_client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-08-01-preview",
            api_key=settings.azure_openai_api_key
        )
        self.async_openai_client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-08-01-preview",
            api_key=settings.azure_openai_api_key
        )

    def _validate_query(self, question: str, document_filter: Optional[str] = None):
        """Validate input parameters"""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        if len(question) > 1000:  # Prevent overly long queries
            raise ValueError("Question too long (max 1000 characters)")
            
        if document_filter and len(document_filter) > 200:
            raise ValueError("Document filter too long (max 200 characters)")

    def _calculate_groundedness_score(self, citations: list, answer: str) -> float:
        """Calculate how well answer is grounded in citations"""
        if not citations:
            return 0.0
        
        # Simple heuristic: check if answer mentions source documents
        cited_sources = {citation.get("source", "") for citation in citations if citation.get("source")}
        mentioned_sources = []
        
        for source in cited_sources:
            if source and source.lower() in answer.lower():
                mentioned_sources.append(source)
        
        return len(mentioned_sources) / len(cited_sources) if cited_sources else 0.0
    
    def _calculate_citation_accuracy(self, citations: list) -> Dict[str, int]:
        """Calculate citation accuracy metrics"""
        if not citations:
            return {"total": 0, "valid": 0, "invalid": 0}
        
        valid_citations = 0
        for citation in citations:
            # Check if citation has required fields
            if (citation.get("source") and 
                citation.get("page") is not None and 
                citation.get("clause")):
                valid_citations += 1
        
        return {
            "total": len(citations),
            "valid": valid_citations,
            "invalid": len(citations) - valid_citations
        }

    def _safe_get_field(self, doc: dict, field: str, default: Any = None) -> Any:
        """Safely get field from document with fallback"""
        return doc.get(field, default)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def answer_query(self, question: str, document_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the RAG flow: Embed -> Search -> Augment -> Generate
        """
        start_time = time.time()
        self._validate_query(question, document_filter)
        
        try:
            # 1. Generate Query Vector
            query_vector = await self.embedder.embed_text(question)

            # 2. Perform Hybrid Search with Semantic Reranking
            from azure.search.documents.models import VectorizedQuery
            filter_query = f"document_name eq '{document_filter}'" if document_filter else None
            
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=settings.search_top_k,
                fields="content_vector"
            )
            
            results = self.search_client.search(
                search_text=question,
                vector_queries=[vector_query],
                filter=filter_query,
                query_type="semantic",
                semantic_configuration_name=settings.search_semantic_config,
                query_caption="extractive",
                select=["content", "document_name", "page_number", "clause_type"],
                top=10
            )
            
            # 3. Context Construction & Citation Mapping
            context_parts = []
            citations = []
            
            # Convert results to list to avoid iterator exhaustion
            results_list = list(results)

            duration = time.time() - start_time
            properties = {
                'custom_dimensions': {
                    'tokens_used': getattr(results, 'usage', {}).get('total_tokens', 0),
                    'latency_ms': duration * 1000,
                    'document_id': document_filter,
                    'has_citations': len(results_list) > 0
                }
            }
            logger.info("LegalQueryProcessed", extra=properties)
            
            if not results_list:
                return {
                    "answer": "I could not find relevant information in the contract database to answer your question.",
                    "citations": [],
                    "data_points_analyzed": 0
                }
            
            MAX_CONTENT_PER_DOC = 1500
            MAX_CONTEXT_CHARS = 12000
            
            for doc in results_list:
                # Debug: Log all available fields
                logger.info(f"Search result fields: {list(doc.keys())}")
                
                # Safe field access with validation - try multiple possible field names
                content = (self._safe_get_field(doc, "content") or 
                          self._safe_get_field(doc, "merged_content") or 
                          self._safe_get_field(doc, "text") or "")
                
                document_name = (self._safe_get_field(doc, "document_name") or 
                               self._safe_get_field(doc, "metadata_storage_name") or
                               self._safe_get_field(doc, "file_name") or
                               self._safe_get_field(doc, "filename") or
                               self._safe_get_field(doc, "title") or
                               "Unknown Document")
                
                page_number = (self._safe_get_field(doc, "page_number") or 
                             self._safe_get_field(doc, "page") or
                             self._safe_get_field(doc, "metadata_storage_path") or
                             "0")
                
                clause_type = (self._safe_get_field(doc, "clause_type") or 
                             self._safe_get_field(doc, "clause") or
                             self._safe_get_field(doc, "category") or
                             self._safe_get_field(doc, "type") or
                             "General")
                
                if not content or not content.strip():
                    continue  # Skip empty content
                    
                # Truncate content per document
                content = content[:MAX_CONTENT_PER_DOC]
                    
                source = f"{document_name or 'Unknown Document'} (Page {page_number or 0})"
                context_parts.append(f"SOURCE: {source}\nCLAUSE TYPE: {clause_type or 'Unknown'}\nCONTENT: {content}")
                citations.append({
                    "source": document_name or "Unknown Source",
                    "page": page_number or 0,
                    "clause": clause_type or "Unknown Clause"
                })

            if not context_parts:
                return {
                    "answer": "I found search results but no meaningful content to analyze for your question.",
                    "citations": [],
                    "data_points_analyzed": 0
                }

            context_text = "\n\n---\n\n".join(context_parts)

            # Truncate overall context to prevent token limit exceeded
            if len(context_text) > MAX_CONTEXT_CHARS:
                context_text = context_text[:MAX_CONTEXT_CHARS] + "\n\n[Context truncated for length]"

            # 4. Prompt Engineering for Legal Accuracy
            system_message = (
                "You are DroitAI, a specialized legal AI assistant. Analyze CUAD contract data. "
                "Base answers ONLY on provided context. If answer is not in context, say you do not know. "
                "Always cite maximum of 4 sources using this format: [Source: DOCUMENT_NAME, Page: PAGE_NUMBER, Clause: CLAUSE_TYPE]. "
                "Include citations immediately after information they support, not just at the end."
            )
            
            user_message = (
                f"Question: {question}\n\n"
                f"Context from Contracts:\n{context_text}"
            )

            # 5. Generation
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.openai_client.chat.completions.create(
                    model=settings.azure_openai_chat_deployment,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0, # Keep temperature at 0 for legal factuality
                    max_tokens=settings.openai_max_tokens
                )
            )

            if not response.choices or len(response.choices) == 0:
                raise RuntimeError("No response generated from OpenAI")

            answer = response.choices[0].message.content
            
            # Calculate business metrics
            groundedness_score = self._calculate_groundedness_score(citations, answer)
            citation_accuracy = self._calculate_citation_accuracy(citations)
            
            # Send comprehensive metrics to Azure
            duration = time.time() - start_time
            properties = {
                'custom_dimensions': {
                    'tokens_used': getattr(response.usage, 'total_tokens', 0),
                    'latency_ms': duration * 1000,
                    'document_id': document_filter,
                    'has_citations': len(citations) > 0,
                    'groundedness_score': groundedness_score,
                    'citation_accuracy_total': citation_accuracy['total'],
                    'citation_accuracy_valid': citation_accuracy['valid'],
                    'citation_accuracy_invalid': citation_accuracy['invalid'],
                    'data_points_analyzed': len(citations),
                    'search_results_count': len(results_list)
                }
            }
            logger.info("LegalQueryProcessed", extra=properties)

            return {
                "answer": answer,
                "citations": citations,
                "data_points_analyzed": len(citations),
                "groundedness_score": groundedness_score,
                "citation_accuracy": citation_accuracy,
                "latency_ms": duration * 1000,
                "tokens_used": getattr(response.usage, 'total_tokens', 0)
            }
            
        except Exception as e:
            # Log error metrics
            duration = time.time() - start_time
            error_properties = {
                'custom_dimensions': {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'latency_ms': duration * 1000,
                    'document_id': document_filter,
                    'has_citations': False,
                    'data_points_analyzed': 0,
                    'success': False
                }
            }
            logger.error("LegalQueryFailed", extra=error_properties)
            
            logger.error(f"Error in RAG service: {str(e)}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "citations": [],
                "data_points_analyzed": 0,
                "groundedness_score": 0.0,
                "citation_accuracy": {"total": 0, "valid": 0, "invalid": 0},
                "latency_ms": duration * 1000,
                "tokens_used": 0,
                "success": False
            }

    async def answer_query_stream(self, question: str, document_filter: Optional[str] = None):
        """
        Streaming version of answer_query that yields tokens as they arrive from Azure OpenAI
        """
        start_time = time.time()
        self._validate_query(question, document_filter)
        
        try:
            # 1. Generate Query Vector
            query_vector = await self.embedder.embed_text(question)

            # 2. Perform Hybrid Search with Semantic Reranking
            from azure.search.documents.models import VectorizedQuery
            filter_query = f"document_name eq '{document_filter}'" if document_filter else None
            
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=settings.search_top_k,
                fields="content_vector"
            )
            
            results = self.search_client.search(
                search_text=question,
                vector_queries=[vector_query],
                filter=filter_query,
                query_type="semantic",
                semantic_configuration_name=settings.search_semantic_config,
                query_caption="extractive",
                select=["content", "document_name", "page_number", "clause_type"],
                top=10
            )
            
            # 3. Context Construction & Citation Mapping
            context_parts = []
            citations = []
            
            # Convert results to list to avoid iterator exhaustion
            results_list = list(results)

            if not results_list:
                yield {"type": "error", "content": "I could not find relevant information in the contract database to answer your question."}
                return
            
            MAX_CONTENT_PER_DOC = 1500
            MAX_CONTEXT_CHARS = 12000
            
            for doc in results_list:
                # Debug: Log all available fields
                logger.info(f"Search result fields: {list(doc.keys())}")
                
                # Safe field access with validation - try multiple possible field names
                content = (self._safe_get_field(doc, "content") or 
                          self._safe_get_field(doc, "merged_content") or 
                          self._safe_get_field(doc, "text") or "")
                
                document_name = (self._safe_get_field(doc, "document_name") or 
                               self._safe_get_field(doc, "metadata_storage_name") or
                               self._safe_get_field(doc, "file_name") or
                               self._safe_get_field(doc, "filename") or
                               self._safe_get_field(doc, "title") or
                               "Unknown Document")
                
                page_number = (self._safe_get_field(doc, "page_number") or 
                             self._safe_get_field(doc, "page") or
                             self._safe_get_field(doc, "metadata_storage_path") or
                             "0")
                
                clause_type = (self._safe_get_field(doc, "clause_type") or 
                             self._safe_get_field(doc, "clause") or
                             self._safe_get_field(doc, "category") or
                             self._safe_get_field(doc, "type") or
                             "General")
                
                if not content or not content.strip():
                    continue  # Skip empty content
                    
                # Truncate content per document
                content = content[:MAX_CONTENT_PER_DOC]
                    
                source = f"{document_name or 'Unknown Document'} (Page {page_number or 0})"
                context_parts.append(f"SOURCE: {source}\nCLAUSE TYPE: {clause_type or 'Unknown'}\nCONTENT: {content}")
                citations.append({
                    "source": document_name or "Unknown Source",
                    "page": page_number or 0,
                    "clause": clause_type or "Unknown Clause"
                })

            if not context_parts:
                yield {"type": "error", "content": "I found search results but no meaningful content to analyze for your question."}
                return

            context_text = "\n\n---\n\n".join(context_parts)

            # Truncate overall context to prevent token limit exceeded
            if len(context_text) > MAX_CONTEXT_CHARS:
                context_text = context_text[:MAX_CONTEXT_CHARS] + "\n\n[Context truncated for length]"

            # 4. Prompt Engineering for Legal Accuracy
            system_message = (
                "You are DroitAI, a specialized legal AI assistant. Analyze CUAD contract data. "
                "Base answers ONLY on provided context. If answer is not in context, say you do not know. "
                "Always cite sources using this format: [Source: DOCUMENT_NAME, Page: PAGE_NUMBER, Clause: CLAUSE_TYPE]. "
                "Include citations immediately after information they support, not just at the end."
            )
            
            user_message = (
                f"Question: {question}\n\n"
                f"Context from Contracts:\n{context_text}"
            )

            # 5. Streaming Generation
            stream = await self.async_openai_client.chat.completions.create(
                model=settings.azure_openai_chat_deployment,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0, # Keep temperature at 0 for legal factuality
                max_tokens=settings.openai_max_tokens,
                stream=True
            )

            full_answer = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield {"type": "token", "content": content}

            # 6. Send final result with citations
            duration = time.time() - start_time
            final_result = {
                "answer": full_answer,
                "citations": citations,
                "data_points_analyzed": len(citations),
                "latency_ms": duration * 1000,
                "success": True
            }
            
            yield {"type": "complete", "result": final_result}
            
        except Exception as e:
            import traceback
            duration = time.time() - start_time
            error_properties = {
                'custom_dimensions': {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'latency_ms': duration * 1000,
                    'document_id': document_filter,
                    'has_citations': False,
                    'data_points_analyzed': 0,
                    'success': False
                }
            }
            logger.error(f"LegalQueryStreamFailed full trace: {traceback.format_exc()}", extra=error_properties)
            
            yield {"type": "error", "content": f"I encountered an error while processing your question: {str(e)}"}
