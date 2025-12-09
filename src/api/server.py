"""
FastAPI server for text classification inference.
Supports multiple models: DistilBERT, Logistic Regression, Linear SVM.
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
import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sklearn.pipeline import Pipeline

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
    current_model: Optional[str] = Field(None, description="Currently active model")
    available_models: List[str] = Field(..., description="List of available models")
    model_path: Optional[str] = Field(None, description="Path to loaded model")
    num_classes: Optional[int] = Field(None, description="Number of classes")
    classes: Optional[List[str]] = Field(None, description="List of class labels")


# ============================================================================
# Model Manager
# ============================================================================

class ModelManager:
    """Manages multiple models and inference."""
    
    # Available models configuration
    AVAILABLE_MODELS = {
        "distilbert": {
            "type": "transformer",
            "path": "models/transformer/distilbert",
            "description": "DistilBERT transformer model (best accuracy)"
        },
        "logistic_regression": {
            "type": "baseline",
            "path": "models/baselines/logistic_regression_tfidf.joblib",
            "description": "Logistic Regression with TF-IDF (fast, interpretable)"
        },
        "linear_svm": {
            "type": "baseline",
            "path": "models/baselines/linear_svm_tfidf.joblib",
            "description": "Linear SVM with TF-IDF (fast, robust)"
        }
    }
    
    def __init__(self, default_model: str = None):
        """
        Initialize model manager.
        
        Args:
            default_model: Default model to load (distilbert, logistic_regression, or linear_svm)
        """
        # Determine default model from environment or parameter
        self.default_model = default_model or os.getenv("DEFAULT_MODEL", "distilbert")
        
        # Current model state
        self.current_model_name = None
        self.current_model_type = None
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.label_mappings = None
        self.device = None
        self.id2label = None
        self.label2id = None
        self.classes = None
        
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        available = []
        for model_name, config in self.AVAILABLE_MODELS.items():
            model_path = Path(config["path"])
            if model_path.exists():
                available.append(model_name)
        return available
    
    def load_model(self, model_name: str = None):
        """
        Load specified model or default model.
        
        Args:
            model_name: Name of model to load (distilbert, logistic_regression, linear_svm)
        """
        # Use default if not specified
        if model_name is None:
            model_name = self.default_model
        
        # Validate model name
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available models: {list(self.AVAILABLE_MODELS.keys())}"
            )
        
        model_config = self.AVAILABLE_MODELS[model_name]
        model_path = Path(model_config["path"])
        
        logger.info("=" * 80)
        logger.info(f"Loading model: {model_name}")
        logger.info(f"Type: {model_config['type']}")
        logger.info(f"Description: {model_config['description']}")
        logger.info("=" * 80)
        
        # Check if model exists
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {model_path}. "
                f"Please train the model first."
            )
        
        # Clear previous model
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        # Load based on model type
        if model_config["type"] == "transformer":
            self._load_transformer_model(model_path)
        elif model_config["type"] == "baseline":
            self._load_baseline_model(model_path)
        else:
            raise ValueError(f"Unknown model type: {model_config['type']}")
        
        # Set current model
        self.current_model_name = model_name
        self.current_model_type = model_config["type"]
        
        logger.info("=" * 80)
        logger.info(f"Model '{model_name}' loaded successfully!")
        logger.info("=" * 80)
    
    def _load_transformer_model(self, model_path: Path):
        """Load DistilBERT transformer model."""
        # Determine device
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info("Using CUDA (GPU)")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU")
        
        # Load label mappings
        labels_path = model_path / "labels.json"
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
        logger.info(f"Loading tokenizer from: {model_path}")
        self.tokenizer = DistilBertTokenizer.from_pretrained(str(model_path))
        logger.info("Tokenizer loaded successfully!")
        
        # Load model
        logger.info(f"Loading model from: {model_path}")
        self.model = DistilBertForSequenceClassification.from_pretrained(
            str(model_path)
        )
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        logger.info("Model loaded successfully!")
    
    def _load_baseline_model(self, model_path: Path):
        """Load baseline sklearn model (Logistic Regression or SVM)."""
        # Load pipeline
        logger.info(f"Loading sklearn pipeline from: {model_path}")
        self.pipeline = joblib.load(str(model_path))
        logger.info("Pipeline loaded successfully!")
        
        # For baseline models, we need to get classes from the classifier
        classifier = self.pipeline.named_steps['classifier']
        # Convert to strings to ensure Pydantic validation passes
        self.classes = [str(label) for label in classifier.classes_.tolist()]
        
        # Create label mappings
        self.id2label = {i: str(label) for i, label in enumerate(self.classes)}
        self.label2id = {str(label): i for i, label in enumerate(self.classes)}
        
        logger.info(f"Number of classes: {len(self.classes)}")
        logger.info(f"Classes: {self.classes}")
        
        # CPU only for sklearn models
        self.device = "cpu"
        logger.info("Using CPU (sklearn models)")
    
    def predict(self, text: str) -> Dict:
        """
        Make prediction for input text using current model.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Route to appropriate prediction method
        if self.current_model_type == "transformer":
            return self._predict_transformer(text)
        elif self.current_model_type == "baseline":
            return self._predict_baseline(text)
        else:
            raise RuntimeError(f"Unknown model type: {self.current_model_type}")
    
    def _predict_transformer(self, text: str) -> Dict:
        """Make prediction using transformer model."""
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
            "inference_time_ms": inference_time,
            "model": self.current_model_name
        }
    
    def _predict_baseline(self, text: str) -> Dict:
        """Make prediction using baseline sklearn model."""
        # Start timing
        start_time = time.time()
        
        # Make prediction
        predicted_label_raw = self.pipeline.predict([text])[0]
        # Convert to string to ensure consistency
        predicted_label = str(predicted_label_raw)
        
        # Get probabilities if available
        classifier = self.pipeline.named_steps['classifier']
        vectorizer = self.pipeline.named_steps['vectorizer']
        
        if hasattr(classifier, 'predict_proba'):
            # Logistic Regression has predict_proba
            probs_np = classifier.predict_proba(
                vectorizer.transform([text])
            )[0]
        elif hasattr(classifier, 'decision_function'):
            # SVM has decision_function
            decision = classifier.decision_function(
                vectorizer.transform([text])
            )[0]
            
            # Convert to pseudo-probabilities using softmax
            if decision.ndim == 0 or len(decision) == 1:
                # Binary classification
                probs_np = 1 / (1 + np.exp(-decision))
                probs_np = np.array([1 - probs_np, probs_np])
            else:
                # Multi-class: apply softmax
                exp_scores = np.exp(decision - np.max(decision))
                probs_np = exp_scores / exp_scores.sum()
        else:
            # Fallback: uniform probabilities
            probs_np = np.ones(len(self.classes)) / len(self.classes)
        
        # Get predicted class index and confidence
        predicted_idx = self.label2id[str(predicted_label)]
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
            "inference_time_ms": inference_time,
            "model": self.current_model_name
        }
    
    def is_loaded(self) -> bool:
        """Check if a model is loaded."""
        if self.current_model_type == "transformer":
            return self.model is not None and self.tokenizer is not None
        elif self.current_model_type == "baseline":
            return self.pipeline is not None
        return False


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
        logger.info(f"Available models: {model_manager.get_available_models()}")
        logger.info(f"Default model: {model_manager.default_model}")
        model_manager.load_model()  # Load default model
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
    description="FastAPI server for text classification with multiple models (DistilBERT, Logistic Regression, Linear SVM)",
    version="2.0.0",
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
        Health status including model loading state and available models
    """
    is_loaded = model_manager.is_loaded()
    available_models = model_manager.get_available_models()
    
    return HealthResponse(
        status="ok" if is_loaded else "model_not_loaded",
        model_loaded=is_loaded,
        current_model=model_manager.current_model_name if is_loaded else None,
        available_models=available_models,
        model_path=str(model_manager.AVAILABLE_MODELS.get(model_manager.current_model_name, {}).get("path", "")) if is_loaded else None,
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
    available_models = model_manager.get_available_models()
    current_model = model_manager.current_model_name if model_manager.is_loaded() else None
    
    return {
        "message": "Text Classification API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "models": "/models",
            "switch_model": "/models/switch",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "current_model": current_model,
        "available_models": available_models,
        "status": "running"
    }


@app.get(
    "/models",
    summary="List Models",
    description="Get list of available models and current model"
)
async def list_models():
    """
    List all available models.
    
    Returns:
        Dictionary with current model and available models
    """
    available_models = model_manager.get_available_models()
    current_model = model_manager.current_model_name if model_manager.is_loaded() else None
    
    models_info = {}
    for model_name in available_models:
        config = model_manager.AVAILABLE_MODELS[model_name]
        models_info[model_name] = {
            "type": config["type"],
            "description": config["description"],
            "path": config["path"],
            "is_current": model_name == current_model
        }
    
    return {
        "current_model": current_model,
        "available_models": list(available_models),
        "models": models_info
    }


class SwitchModelRequest(BaseModel):
    """Request model for switching models."""
    model_name: str = Field(
        ...,
        description="Name of model to switch to",
        json_schema_extra={"example": "distilbert"}
    )


@app.post(
    "/models/switch",
    summary="Switch Model",
    description="Switch to a different model"
)
async def switch_model(request: SwitchModelRequest):
    """
    Switch to a different model.
    
    Args:
        request: Request containing model name to switch to
        
    Returns:
        Success message with new model info
        
    Raises:
        HTTPException: If model switch fails
    """
    try:
        # Validate model name
        available_models = model_manager.get_available_models()
        if request.model_name not in available_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{request.model_name}' not available. Available models: {available_models}"
            )
        
        # Check if already using this model
        if model_manager.current_model_name == request.model_name:
            return {
                "message": f"Already using model '{request.model_name}'",
                "model": request.model_name
            }
        
        # Load new model
        logger.info(f"Switching to model: {request.model_name}")
        model_manager.load_model(request.model_name)
        
        return {
            "message": f"Successfully switched to model '{request.model_name}'",
            "model": request.model_name,
            "type": model_manager.current_model_type,
            "num_classes": len(model_manager.classes),
            "classes": model_manager.classes
        }
        
    except Exception as e:
        logger.error(f"Failed to switch model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to switch model: {str(e)}"
        )


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
