"""
FastAPI server for text classification inference using DistilBERT.
"""
import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

import torch
import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models
# ============================================================================

class PredictRequest(BaseModel):
    """Request model for prediction endpoint."""
    text: str = Field(
        ...,
        description="Text to classify",
        min_length=1,
        max_length=10000,
        json_schema_extra={"example": "This is a sample text for classification."}
    )
    
    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Text must not be empty or just whitespace')
        return v.strip()


class ClassScore(BaseModel):
    """Individual class score."""
    label: str = Field(..., description="Class label")
    score: float = Field(..., description="Confidence score (0-1)", ge=0.0, le=1.0)


class PredictResponse(BaseModel):
    """Response model for prediction endpoint."""
    predicted_label: str = Field(..., description="Predicted class label")
    confidence: float = Field(..., description="Confidence score for predicted label (0-1)", ge=0.0, le=1.0)
    scores: List[ClassScore] = Field(..., description="Scores for all classes")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_path: Optional[str] = Field(None, description="Path to loaded model")
    num_classes: Optional[int] = Field(None, description="Number of classes")
    classes: Optional[List[str]] = Field(None, description="List of class labels")


# ============================================================================
# Model Manager
# ============================================================================

class ModelManager:
    """Manages model loading and inference."""
    
    def __init__(self, model_path: str = "models/transformer/distilbert"):
        """
        Initialize model manager.
        
        Args:
            model_path: Path to saved model directory
        """
        self.model_path = Path(model_path)
        self.model = None
        self.tokenizer = None
        self.label_mappings = None
        self.device = None
        self.id2label = None
        self.label2id = None
        self.classes = None
        
    def load_model(self):
        """Load model, tokenizer, and label mappings."""
        logger.info("=" * 80)
        logger.info("Loading model and artifacts...")
        logger.info("=" * 80)
        
        # Check if model directory exists
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model directory not found: {self.model_path}. "
                "Please train the model first using: python -m src.models.transformer_training"
            )
        
        # Determine device
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info("Using CUDA (GPU)")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU")
        
        # Load label mappings
        labels_path = self.model_path / "labels.json"
        if not labels_path.exists():
            raise FileNotFoundError(f"Label mappings not found: {labels_path}")
        
        logger.info(f"Loading label mappings from: {labels_path}")
        with open(labels_path, 'r') as f:
            self.label_mappings = json.load(f)
        
        self.id2label = {int(k): v for k, v in self.label_mappings['id2label'].items()}
        self.label2id = self.label_mappings['label2id']
        self.classes = self.label_mappings['classes']
        
        logger.info(f"Number of classes: {len(self.classes)}")
        logger.info(f"Classes: {self.classes}")
        
        # Load tokenizer
        logger.info(f"Loading tokenizer from: {self.model_path}")
        self.tokenizer = DistilBertTokenizer.from_pretrained(str(self.model_path))
        logger.info("Tokenizer loaded successfully!")
        
        # Load model
        logger.info(f"Loading model from: {self.model_path}")
        self.model = DistilBertForSequenceClassification.from_pretrained(
            str(self.model_path)
        )
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        logger.info("Model loaded successfully!")
        
        logger.info("=" * 80)
        logger.info("Model loading complete!")
        logger.info("=" * 80)
    
    def predict(self, text: str) -> Dict:
        """
        Make prediction for input text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with prediction results
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Start timing
        start_time = time.time()
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
            # Get probabilities
            probs = torch.softmax(logits, dim=1)
            probs_np = probs.cpu().numpy()[0]
            
            # Get predicted class
            predicted_idx = torch.argmax(probs, dim=1).item()
            predicted_label = self.id2label[predicted_idx]
            confidence = float(probs_np[predicted_idx])
        
        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Prepare scores for all classes
        scores = [
            {
                "label": self.id2label[i],
                "score": float(probs_np[i])
            }
            for i in range(len(self.classes))
        ]
        
        # Sort scores by confidence (descending)
        scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        
        return {
            "predicted_label": predicted_label,
            "confidence": confidence,
            "scores": scores,
            "inference_time_ms": inference_time
        }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None and self.tokenizer is not None


# ============================================================================
# FastAPI Application
# ============================================================================

# Initialize model manager
model_manager = ModelManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    try:
        logger.info("Starting up FastAPI application...")
        model_manager.load_model()
        logger.info("Application startup complete!")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {str(e)}")
        logger.error("Application will start but predictions will fail.")
        logger.error("Please ensure the model is trained and saved in the correct location.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    logger.info("Application shutdown complete!")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Text Classification API",
    description="FastAPI server for text classification using DistilBERT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API server and model are healthy and ready"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status including model loading state
    """
    is_loaded = model_manager.is_loaded()
    
    return HealthResponse(
        status="ok" if is_loaded else "model_not_loaded",
        model_loaded=is_loaded,
        model_path=str(model_manager.model_path) if is_loaded else None,
        num_classes=len(model_manager.classes) if is_loaded else None,
        classes=model_manager.classes if is_loaded else None
    )


@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Predict Text Classification",
    description="Classify input text and return predicted label with confidence scores"
)
async def predict(request: PredictRequest):
    """
    Prediction endpoint.
    
    Args:
        request: Request containing text to classify
        
    Returns:
        Prediction results with label, confidence, and scores
        
    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    # Check if model is loaded
    if not model_manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please check server logs and ensure model is trained."
        )
    
    try:
        # Make prediction
        result = model_manager.predict(request.text)
        
        # Convert to response model
        return PredictResponse(
            predicted_label=result["predicted_label"],
            confidence=result["confidence"],
            scores=[ClassScore(**score) for score in result["scores"]],
            inference_time_ms=result["inference_time_ms"]
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get(
    "/",
    summary="Root Endpoint",
    description="Welcome message and API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Text Classification API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "model": "DistilBERT",
        "status": "running"
    }


# ============================================================================
# Main Entry Point (for testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server in development mode...")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
