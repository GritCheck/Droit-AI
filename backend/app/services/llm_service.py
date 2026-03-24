"""
LLM Service for Answer & Cite Orchestrator
Implements responsible AI with grounding, citations, and safety
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import json
import re
from datetime import datetime

from openai import AsyncAzureOpenAI
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential

from app.core.config import get_settings
from app.models.search import DocumentMetadata, SearchResult
from app.services.content_safety_service import ContentSafetyService

logger = logging.getLogger(__name__)

@dataclass
class Citation:
    """Structured citation for answer verification"""
    source_id: str
    title: str
    source_link: Optional[str]
    page_number: Optional[int]
    chunk_id: Optional[str]
    relevance_score: float
    quote_snippet: str
    confidence: float

@dataclass
class GeneratedAnswer:
    """LLM-generated answer with citations and metadata"""
    answer: str
    citations: List[Citation]
    confidence_score: float
    grounding_sources: List[str]
    safety_passed: bool
    safety_reason: Optional[str]
    token_usage: Dict[str, int]
    generation_time: float
    model_name: str
    metadata: Dict[str, Any]

class LLMOrchestrator:
    """
    Enterprise-grade LLM orchestrator with:
    - Strict grounding to prevent hallucinations
    - Rich citation generation
    - Final safety pass on output
    - Token usage tracking
    - Performance monitoring
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.content_safety = ContentSafetyService()
        self._openai_client = None
        self._system_prompt = self._load_system_prompt()
        self._citation_prompt = self._load_citation_prompt()
        
    async def __aenter__(self):
        """Initialize Azure OpenAI client"""
        try:
            self._openai_client = AsyncAzureOpenAI(
                api_key=self.settings.azure_openai_api_key,
                api_version="2024-02-15-preview",
                azure_endpoint=self.settings.azure_openai_endpoint
            )
            logger.info("Azure OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self._openai_client:
            await self._openai_client.close()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt for strict grounding"""
        return """You are a helpful AI assistant for enterprise document search. 

CRITICAL RULES:
1. ONLY use information from the provided documents. Do NOT use any external knowledge.
2. If the documents don't contain the answer, say "I cannot find information about this in the provided documents."
3. Cite your sources using the format [Source X] where X matches the document number.
4. Be precise and factual. Do not speculate or hallucinate.
5. If documents contradict each other, acknowledge the contradiction and cite both sources.
6. Keep answers concise but comprehensive. Aim for 2-4 paragraphs maximum.

RESPONSE FORMAT:
- Start with a direct answer to the user's question
- Include citations in the format [Source X]
- End with a "Sources:" section listing all referenced documents

Example:
"Based on the provided documents, the policy requires approval from department heads [Source 1, Source 3]. The process typically takes 3-5 business days [Source 2].

Sources:
- Source 1: Employee Handbook, page 15
- Source 2: Approval Process Guidelines, page 8
- Source 3: Department Policies, page 22"
"""

    def _load_citation_prompt(self) -> str:
        """Load prompt for generating structured citations"""
        return """Extract precise citations from the answer and map them to the provided documents.

For each citation in the answer, provide:
1. Document number from [Source X] format
2. Exact quote or paraphrased content
3. Relevance score (0.0-1.0)
4. Page number if available

Return as JSON array of citations.

Example:
[
  {
    "source_number": 1,
    "quote": "approval from department heads",
    "relevance_score": 0.9,
    "page_number": 15
  }
]"""

    async def generate_answer(
        self,
        query: str,
        search_result: SearchResult,
        user_context: Dict[str, Any]
    ) -> GeneratedAnswer:
        """
        Generate grounded answer with citations and safety checks
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Prepare context with documents
            context = self._prepare_context(search_result.documents)
            
            # Step 2: Generate grounded answer
            answer, token_usage = await self._generate_grounded_answer(
                query, context, search_result.documents
            )
            
            # Step 3: Extract and structure citations
            citations = await self._extract_citations(
                answer, search_result.documents
            )
            
            # Step 4: Final safety pass on generated answer
            safety_result = await self._final_safety_check(answer, user_context)
            
            # Step 5: Calculate confidence score
            confidence = self._calculate_confidence(
                answer, citations, safety_result, search_result
            )
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            return GeneratedAnswer(
                answer=answer,
                citations=citations,
                confidence_score=confidence,
                grounding_sources=[doc.id for doc in search_result.documents],
                safety_passed=safety_result.is_safe,
                safety_reason=safety_result.reason,
                token_usage=token_usage,
                generation_time=generation_time,
                model_name=self.settings.azure_openai_deployment_name,
                metadata={
                    "query": query,
                    "document_count": len(search_result.documents),
                    "user_department": user_context.get("department"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            raise
    
    def _prepare_context(self, documents: List[DocumentMetadata]) -> str:
        """Prepare context documents for LLM"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_part = f"""
Source {i}:
Title: {doc.title}
Content: {doc.content}
Source Link: {doc.url or 'N/A'}
Page: {doc.metadata.get('page_number', 'N/A')}
Relevance Score: {doc.score:.3f}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    async def _generate_grounded_answer(
        self,
        query: str,
        context: str,
        documents: List[DocumentMetadata]
    ) -> Tuple[str, Dict[str, int]]:
        """Generate answer strictly grounded in provided documents"""
        try:
            messages = [
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": f"""Question: {query}

Documents:
{context}

Please answer the question using only the information from these documents. Cite your sources appropriately."""
                }
            ]
            
            response = await self._openai_client.chat.completions.create(
                model=self.settings.azure_openai_deployment_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.1,  # Low temperature for factual responses
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            answer = response.choices[0].message.content
            
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return answer, token_usage
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    async def _extract_citations(
        self,
        answer: str,
        documents: List[DocumentMetadata]
    ) -> List[Citation]:
        """Extract and structure citations from the answer"""
        citations = []
        
        # Find all citation references [Source X]
        citation_pattern = r'\[Source (\d+)\]'
        matches = re.findall(citation_pattern, answer)
        
        for source_num in set(matches):  # Remove duplicates
            try:
                doc_index = int(source_num) - 1
                if 0 <= doc_index < len(documents):
                    doc = documents[doc_index]
                    
                    # Extract relevant quote from answer
                    quote = self._extract_quote_for_source(answer, source_num)
                    
                    citation = Citation(
                        source_id=doc.id,
                        title=doc.title,
                        source_link=doc.url,
                        page_number=doc.metadata.get('page_number'),
                        chunk_id=doc.metadata.get('chunk_id'),
                        relevance_score=doc.score,
                        quote_snippet=quote,
                        confidence=min(doc.score, 0.9)  # Cap at 0.9 for safety
                    )
                    citations.append(citation)
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to extract citation for source {source_num}: {str(e)}")
                continue
        
        return citations
    
    def _extract_quote_for_source(self, answer: str, source_num: str) -> str:
        """Extract the relevant quote around a citation"""
        citation_marker = f"[Source {source_num}]"
        
        # Find position of citation
        pos = answer.find(citation_marker)
        if pos == -1:
            return ""
        
        # Extract context around citation (50 chars before and after)
        start = max(0, pos - 50)
        end = min(len(answer), pos + len(citation_marker) + 50)
        
        context = answer[start:end].strip()
        
        # Clean up the quote
        context = re.sub(r'\s+', ' ', context)
        return context[:200]  # Limit length
    
    async def _final_safety_check(
        self,
        answer: str,
        user_context: Dict[str, Any]
    ) -> Any:
        """Final safety pass on generated answer"""
        try:
            safety_result = await self.content_safety.analyze_text(
                answer,
                department=user_context.get("department")
            )
            return safety_result
        except Exception as e:
            logger.error(f"Final safety check failed: {str(e)}")
            # Fail safe - block if safety check fails
            return type('SafetyResult', (), {
                'is_safe': False,
                'reason': f'Safety check failed: {str(e)}'
            })()
    
    def _calculate_confidence(
        self,
        answer: str,
        citations: List[Citation],
        safety_result: Any,
        search_result: SearchResult
    ) -> float:
        """Calculate overall confidence score"""
        confidence_factors = []
        
        # Document relevance factor
        if search_result.documents:
            avg_relevance = sum(doc.score for doc in search_result.documents) / len(search_result.documents)
            confidence_factors.append(avg_relevance)
        
        # Citation coverage factor
        if citations:
            citation_coverage = len(citations) / max(1, len(search_result.documents))
            confidence_factors.append(citation_coverage)
        
        # Safety factor
        safety_factor = 1.0 if safety_result.is_safe else 0.0
        confidence_factors.append(safety_factor)
        
        # Answer quality factor (length and structure)
        if len(answer) > 100 and "[Source" in answer:
            quality_factor = 0.8
        else:
            quality_factor = 0.4
        confidence_factors.append(quality_factor)
        
        # Calculate weighted average
        weights = [0.3, 0.2, 0.3, 0.2]  # Relevance, citations, safety, quality
        confidence = sum(w * f for w, f in zip(weights, confidence_factors))
        
        return round(confidence, 3)
    
    async def generate_follow_up_questions(
        self,
        original_query: str,
        answer: str,
        documents: List[DocumentMetadata]
    ) -> List[str]:
        """Generate relevant follow-up questions"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Generate 3-5 relevant follow-up questions based on the original query and the provided answer. 
                    Questions should help the user explore the topic more deeply using the available documents.
                    Return only the questions, one per line."""
                },
                {
                    "role": "user",
                    "content": f"""Original Question: {original_query}
                    
Answer: {answer}

Available Documents: {[doc.title for doc in documents[:5]]}

Generate follow-up questions:"""
                }
            ]
            
            response = await self._openai_client.chat.completions.create(
                model=self.settings.azure_openai_deployment_name,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            questions_text = response.choices[0].message.content.strip()
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            return questions[:5]  # Limit to 5 questions
            
        except Exception as e:
            logger.error(f"Failed to generate follow-up questions: {str(e)}")
            return []
    
    async def summarize_document(
        self,
        document: DocumentMetadata,
        max_length: int = 300
    ) -> str:
        """Generate a concise summary of a document"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"Summarize the following document in no more than {max_length} characters. Focus on the key points and main findings."
                },
                {
                    "role": "user",
                    "content": f"Title: {document.title}\n\nContent: {document.content}"
                }
            ]
            
            response = await self._openai_client.chat.completions.create(
                model=self.settings.azure_openai_deployment_name,
                messages=messages,
                max_tokens=max_length // 4,  # Approximate token count
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize document: {str(e)}")
            return document.content[:max_length] + "..." if len(document.content) > max_length else document.content
