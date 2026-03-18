"""
Chat API endpoints with Answer & Cite orchestrator
"""

import logging
import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.chat import (
    ChatRequest, 
    ChatResponse, 
    MessageFeedback,
    ChatHealthCheck
)
from app.models.search import SearchRequest
from app.services.search_service import GovernedSearchService
from app.services.llm_service import LLMOrchestrator
from app.services.history_service import HistoryService
from app.core.config import get_settings
from app.utils.sanitizer import sanitize_input
from app.utils.logging import log_error, log_security_event, log_performance, OperationTimer, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()

settings = get_settings()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService),
    llm_service: LLMOrchestrator = Depends(LLMOrchestrator),
    history_service: HistoryService = Depends(HistoryService)
):
    """
    Ask a question with Answer & Cite orchestration
    Implements full RAG pipeline with safety and citations
    """
    start_time = time.time()
    
    with OperationTimer("chat_ask", request=request):
        try:
            # Extract and validate OBO token
            access_token = credentials.credentials
            user_context = await search_service.extract_user_context(access_token)
            
            # Log authentication success
            log_security_event(
                event_type="authentication_success",
                message=f"User authenticated successfully: {user_context.user_id}",
                request=request,
                user_context={"user_id": user_context.user_id, "tenant_id": user_context.tenant_id}
            )
            
            # Sanitize user input
            sanitized_message = sanitize_input(request.message, "search_query")
            if not sanitized_message:
                log_error(
                    message="Message sanitization resulted in empty content",
                    request=request,
                    user_context={"user_id": user_context.user_id},
                    severity=ErrorSeverity.MEDIUM,
                    category=ErrorCategory.VALIDATION,
                    original_message_length=len(request.message)
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Message cannot be empty after sanitization"
                )
            
            # Generate conversation/message IDs
            conversation_id = request.conversation_id or str(uuid.uuid4())
            message_id = str(uuid.uuid4())
            
            # Step 1: Search for relevant documents
            with OperationTimer("search_documents", request=request):
                search_request = SearchRequest(
                    query=sanitized_message,
                    top_k=request.max_documents,
                    semantic_ranking=True,
                    include_facets=False
                )
                
                search_result = await search_service.hybrid_search(search_request, user_context)
            
            if not search_result.documents:
                log_error(
                    message="No search results found for user query",
                    request=request,
                    user_context={"user_id": user_context.user_id},
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.BUSINESS_LOGIC,
                    query=sanitized_message,
                    search_time=search_result.search_time
                )
                return ChatResponse(
                    answer="I cannot find information about this topic in the available documents. Please try rephrasing your question or contact support if you need specific information.",
                    citations=[],
                    confidence_score=0.0,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    timestamp=time.time(),
                    follow_up_questions=[],
                    safety_passed=True,
                    token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    generation_time=time.time() - start_time,
                    model_used=settings.azure_openai_deployment_name,
                    grounding_sources=[]
                )
            
            # Step 2: Generate grounded answer with citations
            with OperationTimer("generate_answer", request=request):
                generated_answer = await llm_service.generate_answer(
                    sanitized_message,
                    search_result,
                    user_context
                )
            
            # Step 3: Generate follow-up questions if requested
            follow_up_questions = []
            if request.include_follow_up:
                with OperationTimer("generate_follow_up", request=request):
                    follow_up_questions = await llm_service.generate_follow_up_questions(
                        sanitized_message,
                        generated_answer.answer,
                        search_result.documents
                    )
            
            # Step 4: Store conversation history
            with OperationTimer("store_history", request=request):
                await history_service.store_message(
                    conversation_id=conversation_id,
                    user_id=user_context.user_id,
                    message=sanitized_message,
                    response=generated_answer.answer,
                    citations=[c.__dict__ for c in generated_answer.citations],
                    metadata={
                        "confidence_score": generated_answer.confidence_score,
                        "safety_passed": generated_answer.safety_passed,
                        "token_usage": generated_answer.token_usage,
                        "model_used": generated_answer.model_used
                    }
                )
            
            # Step 5: Build response
            response = ChatResponse(
                answer=generated_answer.answer,
                citations=[
                    {
                        "source_id": c.source_id,
                        "title": c.title,
                        "source_link": c.source_link,
                        "page_number": c.page_number,
                        "chunk_id": c.chunk_id,
                        "relevance_score": c.relevance_score,
                        "quote_snippet": c.quote_snippet,
                        "confidence": c.confidence
                    }
                    for c in generated_answer.citations
                ],
                confidence_score=generated_answer.confidence_score,
                conversation_id=conversation_id,
                message_id=message_id,
                timestamp=time.time(),
                follow_up_questions=follow_up_questions,
                safety_passed=generated_answer.safety_passed,
                safety_reason=generated_answer.safety_reason,
                token_usage=generated_answer.token_usage,
                generation_time=generated_answer.generation_time,
                model_used=generated_answer.model_used,
                grounding_sources=generated_answer.grounding_sources
            )
            
            # Log successful interaction
            log_performance(
                operation="chat_completed",
                duration=time.time() - start_time,
                request=request,
                confidence_score=response.confidence_score,
                citations_count=len(response.citations),
                safety_passed=response.safety_passed
            )
            
            logger.info(f"Chat completed for user {user_context.user_id}: "
                       f"confidence={response.confidence_score:.2f}, "
                       f"citations={len(response.citations)}, "
                       f"safety={response.safety_passed}")
            
            return response
            
        except ValueError as e:
            # Authentication/authorization error
            log_security_event(
                event_type="authentication_failed",
                message=f"Authentication failed: {str(e)}",
                request=request,
                error=str(e)
            )
            logger.warning(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}"
            )
        except Exception as e:
            # Log unexpected error
            log_error(
                message="Chat request failed with unexpected error",
                exception=e,
                request=request,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SYSTEM,
                operation="chat_ask"
            )
            logger.error(f"Chat request failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat request failed: {str(e)}"
            )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService),
    history_service: HistoryService = Depends(HistoryService)
):
    """Get conversation history"""
    try:
        # Validate user
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Get conversation
        conversation = await history_service.get_conversation(
            conversation_id, 
            user_context.user_id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return conversation
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.get("/conversations")
async def list_conversations(
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService),
    history_service: HistoryService = Depends(HistoryService),
    limit: int = 10,
    offset: int = 0
):
    """List user's conversations"""
    try:
        # Validate user
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Get conversations
        conversations = await history_service.list_user_conversations(
            user_context.user_id,
            limit=limit,
            offset=offset
        )
        
        return {"conversations": conversations, "total": len(conversations)}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to list conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.post("/feedback")
async def submit_feedback(
    feedback: MessageFeedback,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService),
    history_service: HistoryService = Depends(HistoryService)
):
    """Submit feedback on chat response"""
    try:
        # Validate user
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Verify feedback is for user's own message
        if feedback.user_id != user_context.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot submit feedback for other users"
            )
        
        # Store feedback
        await history_service.store_feedback(feedback.__dict__)
        
        logger.info(f"Feedback submitted: rating={feedback.rating}, "
                   f"type={feedback.feedback_type}, message_id={feedback.message_id}")
        
        return {"status": "success", "message": "Feedback submitted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to submit feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    search_service: GovernedSearchService = Depends(GovernedSearchService),
    history_service: HistoryService = Depends(HistoryService)
):
    """Delete conversation"""
    try:
        # Validate user
        access_token = credentials.credentials
        user_context = await search_service.extract_user_context(access_token)
        
        # Delete conversation
        success = await history_service.delete_conversation(
            conversation_id,
            user_context.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"status": "success", "message": "Conversation deleted"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.get("/health", response_model=ChatHealthCheck)
async def chat_health():
    """Chat service health check"""
    return ChatHealthCheck(
        status="healthy",
        openai_connected=bool(settings.azure_openai_endpoint),
        search_connected=bool(settings.azure_search_endpoint),
        content_safety_connected=bool(settings.azure_content_safety_endpoint),
        features={
            "obo_authentication": True,
            "grounded_answers": True,
            "citations": True,
            "content_safety": True,
            "conversation_history": True,
            "follow_up_questions": True
        }
    )
