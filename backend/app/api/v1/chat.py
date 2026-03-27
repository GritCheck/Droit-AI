from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
import json
import asyncio

from app.services.rag_service import LegalRagService
from app.core.auth import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    document_id: Optional[str] = None

class Citation(BaseModel):
    source: str = "Unknown Source"
    page: int = 0
    clause: str = "Unknown Clause"

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    data_points_analyzed: int

@router.post("/query", response_model=ChatResponse)
async def ask_legal_question(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submits a query to the Legal RAG engine.
    Requires Entra ID authentication.
    """
    try:
        rag_service = LegalRagService()
        result = await rag_service.answer_query(
            question=request.message,
            document_filter=request.document_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Engine Error: {str(e)}")

@router.post("/query-stream")
async def ask_legal_question_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Streaming version of the RAG query endpoint using real Azure OpenAI streaming.
    """
    async def generate_stream():
        try:
            rag_service = LegalRagService()
            
            async for chunk in rag_service.answer_query_stream(
                question=request.message,
                document_filter=request.document_id
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")