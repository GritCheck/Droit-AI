# Multi-stage Dockerfile for FastAPI RAG Backend
# Supports Azure Document Intelligence and Docling local parsing

# Stage 1: Build stage with dependencies
FROM python:3.11-slim as builder

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for document processing and AI models
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential libraries for AI/ML models
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # PDF processing
    poppler-utils \
    # OCR support
    tesseract-ocr \
    tesseract-ocr-eng \
    # Build tools for Python packages
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    # Docling model cache directory
    DOCLING_CACHE_DIR=/app/cache/models \
    # Azure CLI configuration
    AZURE_CONFIG_DIR=/app/.azure

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime libraries for AI models
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    # PDF processing
    poppler-utils \
    # OCR support
    tesseract-ocr \
    tesseract-ocr-eng \
    # Network utilities for Azure connectivity
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security and compliance
RUN groupadd -r raguser && \
    useradd -r -g raguser -d /app -s /bin/bash raguser

# Create application directory structure
RUN mkdir -p /app /app/cache /app/cache/models /app/data /app/.azure && \
    chown -R raguser:raguser /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=raguser:raguser . /app

# Set working directory
WORKDIR /app

# Create cache directories with proper permissions
RUN mkdir -p /app/cache/models /app/cache/documents /app/logs && \
    chown -R raguser:raguser /app/cache /app/logs

# Switch to non-root user
USER raguser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default entrypoint with production configuration
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Allow command override for development
CMD []
