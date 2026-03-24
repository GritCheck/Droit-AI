"""
Pydantic models for chat requests and responses
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat request with message and search options"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    search_options: Optional[Dict[str, Any]] = Field(None, description="Search options")
    include_follow_up: bool = Field(True, description="Include follow-up questions")
    max_documents: int = Field(10, ge=1, le=20, description="Max documents to use")


class Citation(BaseModel):
    """Citation model for answer verification"""
    source_id: str
    title: str
    source_link: Optional[str] = None
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    relevance_score: float
    quote_snippet: str
    confidence: float


class ChatResponse(BaseModel):
    """Chat response with answer and citations"""
    answer: str
    citations: List[Citation]
    confidence_score: float
    conversation_id: str
    message_id: str
    timestamp: datetime
    follow_up_questions: List[str] = Field(default_factory=list)
    safety_passed: bool
    safety_reason: Optional[str] = None
    token_usage: Dict[str, int]
    generation_time: float
    model_name: str
    grounding_sources: List[str]


class ConversationHistory(BaseModel):
    """Conversation history for context"""
    conversation_id: str
    user_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageFeedback(BaseModel):
    """User feedback on chat responses"""
    message_id: str
    conversation_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_type: str = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, description="User comment")
    timestamp: datetime


class ChatAnalytics(BaseModel):
    """Chat analytics for monitoring"""
    conversation_id: str
    user_id: str
    message_count: int
    total_tokens: int
    average_confidence: float
    safety_violations: int
    session_duration: float
    timestamp: datetime


class DocumentSummary(BaseModel):
    """Document summary model"""
    document_id: str
    title: str
    summary: str
    key_points: List[str]
    confidence: float
    generated_at: datetime


class FollowUpQuestion(BaseModel):
    """Follow-up question model"""
    question: str
    relevance_score: float
    suggested_documents: List[str]
    category: Optional[str] = None


class ChatHealthCheck(BaseModel):
    """Chat service health check"""
    status: str
    openai_connected: bool
    search_connected: bool
    content_safety_connected: bool
    last_response_time: Optional[float] = None
    total_conversations: int = 0
    error_rate: float = 0.0
