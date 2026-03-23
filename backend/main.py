"""
FastAPI Main Application - Droit AI Backend
Enterprise-grade RAG with OBO authentication and governed search
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import get_settings
from app.api.v1 import chat, search, ingestion
from app.middleware.rate_limiter import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting DroitAI Backend...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Local parsing enabled: {settings.enable_local_parsing}")
    logger.info(f"Azure Document Intelligence enabled: {settings.enable_azure_doc_intelligence}")
    logger.info(f"Content safety enabled: {settings.enable_content_safety}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DroitAI Backend...")


# Create FastAPI app
app = FastAPI(
    title="DroitAI API",
    description="Enterprise-grade RAG system with OBO authentication and governed search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=settings.allowed_methods_list,
    allow_headers=settings.allowed_headers_list,
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header for monitoring"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoints
@app.get("/health")
async def health_check():
    """Main health check endpoint"""
    return {
        "status": "healthy",
        "service": "DroitAI Backend",
        "version": "1.0.0",
        "timestamp": time.time(),
        "features": {
            "obo_authentication": True,
            "governed_search": True,
            "content_safety": settings.enable_content_safety,
            "local_parsing": settings.enable_local_parsing,
            "azure_document_intelligence": settings.enable_azure_doc_intelligence,
            "dual_pathway_ingestion": True
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DroitAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource was not found: {request.url.path}",
            "timestamp": time.time()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": time.time()
        }
    )


# Development server startup
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
