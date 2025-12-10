# ============================================================================
# Dockerfile for Cloud NLP Classifier - FastAPI Inference Server
# ============================================================================
# This Dockerfile creates a production-ready container for the text 
# classification API with multiple models:
# - DistilBERT transformer model (best accuracy)
# - Toxicity Classifier multi-label model (6 toxicity categories)
# - Logistic Regression with TF-IDF (fast, interpretable)
# - Linear SVM with TF-IDF (fast, robust)
#
# Build: docker build -t cloud-nlp-classifier .
# Run:   docker run -p 8000:8000 cloud-nlp-classifier
# Run with specific model: docker run -p 8000:8000 -e DEFAULT_MODEL=logistic_regression cloud-nlp-classifier
# ============================================================================

# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEFAULT_MODEL=distilbert

# Install system dependencies required by PyTorch and transformers
# - build-essential: C compiler for some Python packages
# - curl: for health checks
# - git: sometimes needed by transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
# We exclude jupyter/ipykernel as they're not needed in production
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y jupyter ipykernel || true

# Copy source code
COPY src/ ./src/

# Copy configuration files
COPY config/ ./config/

# Copy all trained models
# Transformer model: DistilBERT (model.safetensors, config.json, tokenizer files, labels.json)
COPY models/transformer/distilbert/ ./models/transformer/distilbert/

# Toxicity classifier: Multi-label DistilBERT (model.safetensors, config.json, tokenizer files, labels.json)
COPY models/toxicity_multi_head/ ./models/toxicity_multi_head/

# Baseline models: Logistic Regression and Linear SVM (sklearn pipelines)
COPY models/baselines/*.joblib ./models/baselines/

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000 for FastAPI
EXPOSE 8000

# Health check to ensure the API is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI server with uvicorn
# - host 0.0.0.0: Listen on all interfaces (required for Docker)
# - port 8000: Default API port
# - workers 1: Single worker (can be increased for production)
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
