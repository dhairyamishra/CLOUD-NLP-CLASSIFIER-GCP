"""
FastAPI server for text classification inference using DistilBERT.
Supports both standard single-label classification and multi-head toxicity classification.
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
from transformers import AutoTokenizer, DistilBertForSequenceClassification, AutoModel

from src.models.multi_head_model import MultiHeadToxicityModel

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
    text: str = Field(..., description="Text to classify", min_length=1)

class BatchTextRequest(BaseModel):
    texts: List[str]

class ExplainRequest(BaseModel):
    text: str
    focus_label: Optional[str] = None
    top_k: int = 10

class ClassScore(BaseModel):
    """Individual class score."""
    label: str
    score: float

class PredictResponse(BaseModel):
    """Response model for prediction endpoint."""
    predicted_label: str
    confidence: float
    scores: List[ClassScore]
    inference_time_ms: float

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    model_loaded: bool
    model_path: Optional[str] = None
    num_classes: Optional[int] = None
    classes: Optional[List[str]] = None

# ============================================================================
# Model Manager
# ============================================================================

class ModelManager:
    """Manages model loading and inference for Toxicity Model."""
    
    def __init__(self, model_dir: str = "models/toxicity_multi_head"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.tokenizer = None
        self.device = None
        self.labels = []
        self.threshold = 0.5
        
    def load_model(self):
        """Load model, tokenizer, and labels."""
        logger.info("=" * 80)
        logger.info("Loading Toxicity Model...")
        logger.info("=" * 80)
        
        if not self.model_dir.exists():
             logger.warning(f"Model directory {self.model_dir} not found. Model will not be loaded.")
             return

        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        # Load labels
        labels_path = self.model_dir / "labels.json"
        if labels_path.exists():
            with open(labels_path, 'r') as f:
                data = json.load(f)
                self.labels = data.get("labels", [])
        else:
            # Fallback defaults if file missing (should be created by trainer)
            self.labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
            logger.warning(f"labels.json not found, using defaults: {self.labels}")

        # Tokenizer
        logger.info(f"Loading tokenizer from {self.model_dir}")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))

        # Model
        logger.info("Initializing MultiHeadToxicityModel...")
        # We need the base model name to init structure; 
        # usually saved in config or we assume distilbert-base-uncased if not passing it explicitly from saved config.
        # But tokenizer is loaded from local, so we can guess base model or just use string.
        base_model = "distilbert-base-uncased" 
        self.model = MultiHeadToxicityModel(base_model, self.labels)
        
        weights_path = self.model_dir / "model_weights.pt"
        if weights_path.exists():
            state_dict = torch.load(weights_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model weights loaded successfully!")
        else:
            logger.error(f"Weights file not found at {weights_path}")
            self.model = None

    def is_loaded(self) -> bool:
        return self.model is not None and self.tokenizer is not None

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")

        enc = self.tokenizer(
            texts, padding=True, truncation=True, max_length=256, return_tensors="pt"
        )
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs["logits"]

        results = []
        batch_size = len(texts)
        for i in range(batch_size):
            per_label = {}
            max_prob = 0.0
            max_label = None

            for name in self.labels:
                logit = logits[name][i]
                prob = torch.sigmoid(logit).item()
                is_pred = prob >= self.threshold
                per_label[name] = {"probability": prob, "predicted": is_pred}

                if prob > max_prob:
                    max_prob = prob
                    max_label = name
            
            # If nothing exceeds threshold, pick max? Or say 'clean'?
            # nlp-on-cloud logic:
            results.append({
                "labels": per_label,
                "primary_type": max_label if max_prob >= self.threshold else "clean",
                "primary_probability": max_prob,
                "any_toxic": bool(max_prob >= self.threshold)
            })
        return results

    def explain(self, text: str, focus_label: Optional[str] = None, top_k: int = 10) -> Dict:
        if not self.is_loaded():
             raise RuntimeError("Model not loaded")

        enc = self.tokenizer(text, padding="max_length", truncation=True, max_length=256, return_tensors="pt")
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)

        with torch.no_grad():
            # Access encoder directly
            enc_out = self.model.encoder(input_ids=input_ids, attention_mask=attention_mask)
            last_hidden_state = enc_out.last_hidden_state # (1, L, H)
            cls_repr = last_hidden_state[:, 0, :]
            cls_repr = self.model.dropout(cls_repr)
            
            probs = {}
            for name in self.labels:
                logit = self.model.heads[name](cls_repr).squeeze(-1)
                probs[name] = float(torch.sigmoid(logit).item())
        
        if focus_label is None:
            focus_label = max(probs.items(), key=lambda x: x[1])[0]

        # Token importance (L2 norm)
        token_reprs = last_hidden_state.squeeze(0) # (L, H)
        token_importances = torch.norm(token_reprs, dim=-1) # (L,)

        tokens = self.tokenizer.convert_ids_to_tokens(input_ids.squeeze(0).cpu().tolist())
        token_info = []
        for idx, (tok, imp) in enumerate(zip(tokens, token_importances.tolist())):
            if tok in self.tokenizer.all_special_tokens: 
                continue
            token_info.append({"position": idx, "token": tok, "importance": imp})
        
        token_info.sort(key=lambda x: x["importance"], reverse=True)
        return {
            "text": text,
            "focus_label": focus_label,
            "probabilities": probs,
            "tokens": token_info[:top_k]
        }

# ============================================================================
# FastAPI Application
# ============================================================================

model_manager = ModelManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        model_manager.load_model()
    except Exception as e:
        logger.error(f"Startup error: {e}")
    yield
    # Shutdown

app = FastAPI(
    title="Toxicity Classification API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/v1/health")
def health_check():
    is_loaded = model_manager.is_loaded()
    return {
        "status": "ok",
        "model_loaded": is_loaded,
        "labels": model_manager.labels
    }

@app.post("/api/v1/classify/single")
def classify_single(req: PredictRequest):
    if not model_manager.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    results = model_manager.predict_batch([req.text])
    return results[0]

@app.post("/api/v1/classify/batch")
def classify_batch(req: BatchTextRequest):
    if not model_manager.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    results = model_manager.predict_batch(req.texts)
    return {"results": results}

@app.post("/api/v1/explain")
def explain(req: ExplainRequest):
    if not model_manager.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    return model_manager.explain(req.text, req.focus_label, req.top_k)

# For backward compatibility / standard endpoints
@app.post("/predict")
def predict_standard(req: PredictRequest):
    """Alias for classify_single but formatted slightly differently if needed."""
    return classify_single(req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
