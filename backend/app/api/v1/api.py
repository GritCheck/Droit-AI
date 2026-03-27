from fastapi import APIRouter
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as documents_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
