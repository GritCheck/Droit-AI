"""
Minimal FastAPI application for testing without Azure dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time

app = FastAPI(
    title="RAG Backend API (Minimal)",
    description="Minimal version for testing without Azure services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock models for testing
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    semantic_ranking: bool = True
    include_facets: bool = False

class SearchResult(BaseModel):
    query: str
    documents: List[Dict[str, Any]] = []
    total_count: int = 0
    search_time: float = 0.0

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    max_documents: int = 5
    include_follow_up: bool = False

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    message_id: str
    timestamp: float
    confidence_score: float = 0.0
    citations: List[Dict[str, Any]] = []
    safety_passed: bool = True
    generation_time: float = 0.0

@app.get("/")
async def root():
    return {"message": "RAG Backend API (Minimal) is running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "minimal (no Azure services)",
        "services": {
            "search": "/api/v1/search/health",
            "chat": "/api/v1/chat/health"
        }
    }

# Mock Search endpoints
@app.get("/api/v1/search/health")
async def search_health():
    return {
        "status": "healthy",
        "service": "mock-search",
        "features": {
            "obo_authentication": False,
            "hybrid_search": False,
            "security_filtering": False,
            "content_safety": False,
            "semantic_search": False,
            "faceted_search": False
        },
        "azure_services": {
            "ai_search": False,
            "content_safety": False,
            "openai": False
        },
        "note": "This is a mock endpoint for testing"
    }

@app.post("/api/v1/search/hybrid")
async def mock_hybrid_search(request: SearchRequest):
    """Mock hybrid search endpoint"""
    start_time = time.time()
    
    # Mock response
    mock_documents = [
        {
            "id": "doc1",
            "title": f"Sample document for: {request.query}",
            "content": f"This is mock content related to {request.query}",
            "score": 0.95,
            "source": "mock"
        }
    ]
    
    return SearchResult(
        query=request.query,
        documents=mock_documents,
        total_count=len(mock_documents),
        search_time=time.time() - start_time
    )

# Mock Chat endpoints
@app.get("/api/v1/chat/health")
async def chat_health():
    return {
        "status": "healthy",
        "openai_connected": False,
        "search_connected": False,
        "content_safety_connected": False,
        "features": {
            "obo_authentication": False,
            "grounded_answers": False,
            "citations": False,
            "content_safety": False,
            "conversation_history": False,
            "follow_up_questions": False
        },
        "note": "This is a mock endpoint for testing"
    }

@app.post("/api/v1/chat/ask")
async def mock_chat_ask(request: ChatRequest):
    """Mock chat endpoint"""
    start_time = time.time()
    
    # Generate mock response
    mock_answer = f"This is a mock response to your question: '{request.message}'. Azure services are not configured."
    
    return ChatResponse(
        answer=mock_answer,
        conversation_id=request.conversation_id or "mock-conversation-id",
        message_id="mock-message-id",
        timestamp=time.time(),
        confidence_score=0.8,
        citations=[],
        safety_passed=True,
        generation_time=time.time() - start_time
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
