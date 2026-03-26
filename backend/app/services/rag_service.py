import asyncio
import logging
from typing import Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.embedder import LegalEmbedder

logger = logging.getLogger(__name__)
settings = get_settings()

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
            credential=DefaultAzureCredential()
        )
        self.openai_client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-02-15-preview",
            azure_ad_token_provider=DefaultAzureCredential().get_token
        )

    def _validate_query(self, question: str, document_filter: Optional[str] = None):
        """Validate input parameters"""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        if len(question) > 1000:  # Prevent overly long queries
            raise ValueError("Question too long (max 1000 characters)")
            
        if document_filter and len(document_filter) > 200:
            raise ValueError("Document filter too long (max 200 characters)")

    def _safe_get_field(self, doc: dict, field: str, default: Any = None) -> Any:
        """Safely get field from document with fallback"""
        return doc.get(field, default)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def answer_query(self, question: str, document_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the RAG flow: Embed -> Search -> Augment -> Generate
        """
        self._validate_query(question, document_filter)
        
        try:
            # 1. Generate Query Vector
            query_vector = await self.embedder.embed_text(question)

            # 2. Perform Hybrid Search with Semantic Reranking
            filter_query = f"document_name eq '{document_filter}'" if document_filter else None
            
            results = self.search_client.search(
                search_text=question,
                vector_queries=[{
                    "vector": query_vector,
                    "fields": "content_vector",
                    "k": settings.search_top_k
                }],
                filter=filter_query,
                query_type="semantic",
                semantic_configuration_name=settings.search_semantic_config,
                query_caption="extractive",
                select=["content", "document_name", "page_number", "clause_type"]
            )

            # 3. Context Construction & Citation Mapping
            context_parts = []
            citations = []
            
            # Convert results to list to avoid iterator exhaustion
            results_list = list(results)
            
            if not results_list:
                return {
                    "answer": "I could not find relevant information in the contract database to answer your question.",
                    "citations": [],
                    "data_points_analyzed": 0
                }
            
            for doc in results_list:
                # Safe field access with validation
                content = self._safe_get_field(doc, "content")
                document_name = self._safe_get_field(doc, "document_name", "Unknown")
                page_number = self._safe_get_field(doc, "page_number", 0)
                clause_type = self._safe_get_field(doc, "clause_type", "Uncategorized")
                
                if not content or not content.strip():
                    continue  # Skip empty content
                    
                source = f"{document_name} (Page {page_number})"
                context_parts.append(f"SOURCE: {source}\nCLAUSE TYPE: {clause_type}\nCONTENT: {content}")
                citations.append({
                    "source": document_name,
                    "page": page_number,
                    "clause": clause_type
                })

            if not context_parts:
                return {
                    "answer": "I found search results but no meaningful content to analyze for your question.",
                    "citations": [],
                    "data_points_analyzed": 0
                }

            context_text = "\n\n---\n\n".join(context_parts)

            # 4. Prompt Engineering for Legal Accuracy
            system_message = (
                "You are DroitAI, a specialized legal AI assistant. Your task is to analyze CUAD contract data. "
                "Base your answers ONLY on the provided context. If the answer is not in the context, say you do not know. "
                "Always cite the source document and page number in your response."
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

            return {
                "answer": response.choices[0].message.content,
                "citations": citations,
                "data_points_analyzed": len(citations)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG service: {str(e)}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "citations": [],
                "data_points_analyzed": 0
            }
