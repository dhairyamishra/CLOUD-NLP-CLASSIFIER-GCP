"""
Model Manager for Streamlit UI.

Handles loading and caching of all models (baselines and transformer).
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
import streamlit as st
import joblib
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    AutoConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and caching of all classification models."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize ModelManager.
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        if project_root is None:
            # Auto-detect project root (assuming we're in src/ui/utils)
            self.project_root = Path(__file__).parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.models_dir = self.project_root / "models"
        self.baseline_dir = self.models_dir / "baselines"
        self.transformer_dir = self.models_dir / "transformer" / "distilbert"
        
        # Device detection
        self.device = self._detect_device()
        logger.info(f"Using device: {self.device}")
    
    def _detect_device(self) -> str:
        """Detect available device (GPU/CPU)."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    @st.cache_resource
    def load_baseline_models(_self) -> Dict[str, Any]:
        """
        Load baseline models (Logistic Regression and Linear SVM).
        
        Returns:
            Dictionary with model names as keys and model objects as values.
        """
        models = {}
        
        try:
            # Load Logistic Regression
            logreg_path = _self.baseline_dir / "logistic_regression_tfidf.joblib"
            if logreg_path.exists():
                models['logreg'] = joblib.load(logreg_path)
                logger.info("✅ Loaded Logistic Regression model")
            else:
                logger.warning(f"⚠️ Logistic Regression model not found at {logreg_path}")
        except Exception as e:
            logger.error(f"❌ Error loading Logistic Regression: {e}")
        
        try:
            # Load Linear SVM
            svm_path = _self.baseline_dir / "linear_svm_tfidf.joblib"
            if svm_path.exists():
                models['svm'] = joblib.load(svm_path)
                logger.info("✅ Loaded Linear SVM model")
            else:
                logger.warning(f"⚠️ Linear SVM model not found at {svm_path}")
        except Exception as e:
            logger.error(f"❌ Error loading Linear SVM: {e}")
        
        return models
    
    @st.cache_resource
    def load_transformer_model(_self) -> Optional[Dict[str, Any]]:
        """
        Load transformer model (DistilBERT).
        
        Returns:
            Dictionary with model, tokenizer, and label mappings, or None if failed.
        """
        try:
            if not _self.transformer_dir.exists():
                logger.warning(f"⚠️ Transformer directory not found at {_self.transformer_dir}")
                return None
            
            # Load model
            model = AutoModelForSequenceClassification.from_pretrained(
                str(_self.transformer_dir)
            )
            model.to(_self.device)
            model.eval()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                str(_self.transformer_dir)
            )
            
            # Load label mappings
            labels_path = _self.transformer_dir / "labels.json"
            if labels_path.exists():
                with open(labels_path, 'r') as f:
                    label_data = json.load(f)
                    id2label = label_data.get('id2label', {})
                    # Convert string keys to int
                    id2label = {int(k): v for k, v in id2label.items()}
            else:
                # Fallback to model config
                config = AutoConfig.from_pretrained(str(_self.transformer_dir))
                id2label = config.id2label
            
            logger.info("✅ Loaded DistilBERT transformer model")
            
            return {
                'model': model,
                'tokenizer': tokenizer,
                'id2label': id2label,
                'device': _self.device
            }
        
        except Exception as e:
            logger.error(f"❌ Error loading transformer model: {e}")
            return None
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available models.
        
        Returns:
            Dictionary with model info including type, status, and metadata.
        """
        models_info = {}
        
        # Check baseline models
        baseline_models = self.load_baseline_models()
        
        if 'logreg' in baseline_models:
            models_info['Logistic Regression (Baseline)'] = {
                'key': 'logreg',
                'type': 'baseline',
                'status': 'loaded',
                'accuracy': '~82%',
                'f1_score': '~0.80',
                'inference_speed': '<10ms',
                'description': 'TF-IDF + Logistic Regression'
            }
        
        if 'svm' in baseline_models:
            models_info['Linear SVM (Baseline)'] = {
                'key': 'svm',
                'type': 'baseline',
                'status': 'loaded',
                'accuracy': '~83%',
                'f1_score': '~0.81',
                'inference_speed': '<10ms',
                'description': 'TF-IDF + Linear SVM'
            }
        
        # Check transformer model
        transformer = self.load_transformer_model()
        if transformer is not None:
            models_info['DistilBERT (Transformer)'] = {
                'key': 'distilbert',
                'type': 'transformer',
                'status': 'loaded',
                'accuracy': '~92%',
                'f1_score': '~0.91',
                'inference_speed': '~50ms (GPU) / ~500ms (CPU)',
                'description': 'Fine-tuned DistilBERT'
            }
        
        return models_info
    
    def get_model_metadata(self, model_key: str) -> Dict[str, Any]:
        """
        Get metadata for a specific model.
        
        Args:
            model_key: Key identifying the model (logreg, svm, distilbert)
        
        Returns:
            Dictionary with model metadata.
        """
        all_models = self.get_available_models()
        
        for model_name, info in all_models.items():
            if info['key'] == model_key:
                return info
        
        return {}


# Singleton instance
_model_manager_instance = None


def get_model_manager() -> ModelManager:
    """
    Get or create the ModelManager singleton instance.
    
    Returns:
        ModelManager instance.
    """
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager()
    return _model_manager_instance
