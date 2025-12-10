"""
Inference Handler for Streamlit UI.

Handles predictions for all model types (baselines and transformer).
"""

import time
import re
import logging
from typing import Dict, Any, Optional
import numpy as np
import torch
from torch.nn.functional import softmax

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InferenceHandler:
    """Handles inference for all model types."""
    
    def __init__(self, model_manager):
        """
        Initialize InferenceHandler.
        
        Args:
            model_manager: ModelManager instance with loaded models.
        """
        self.model_manager = model_manager
        self.baseline_models = model_manager.load_baseline_models()
        self.transformer = model_manager.load_transformer_model()
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for inference.
        
        Args:
            text: Input text to preprocess.
        
        Returns:
            Preprocessed text.
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # For baseline models, convert to lowercase
        # (Transformer tokenizer handles this)
        return text
    
    def validate_input(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate input text.
        
        Args:
            text: Input text to validate.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        if not text or len(text.strip()) == 0:
            return False, "Please enter some text to analyze."
        
        if len(text.strip()) < 3:
            return False, "Text is too short. Please enter at least 3 characters."
        
        if len(text) > 5000:
            return False, "Text is too long. Please limit to 5000 characters."
        
        return True, None
    
    def predict_baseline(self, text: str, model_key: str) -> Dict[str, Any]:
        """
        Run inference using a baseline model.
        
        Args:
            text: Input text to classify.
            model_key: Key identifying the model (logreg or svm).
        
        Returns:
            Dictionary with prediction results.
        """
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(text)
            if not is_valid:
                return {'error': error_msg}
            
            # Get model
            if model_key not in self.baseline_models:
                return {'error': f"Model '{model_key}' not found."}
            
            model = self.baseline_models[model_key]
            
            # Preprocess
            processed_text = self.preprocess_text(text).lower()
            
            # Measure inference time
            start_time = time.time()
            
            # Predict
            prediction = model.predict([processed_text])[0]
            
            # Get probabilities if available
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba([processed_text])[0]
            else:
                # For SVM without probability
                probabilities = None
            
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Convert numeric labels to readable format
            # Assuming 0 = non-hate, 1 = hate (common for hate speech datasets)
            label_map = {0: 'Non-Hate Speech', 1: 'Hate Speech'}
            readable_label = label_map.get(int(prediction), str(prediction))
            
            # Format results
            result = {
                'label': readable_label,
                'confidence': float(max(probabilities)) if probabilities is not None else 1.0,
                'inference_time_ms': round(inference_time, 2),
                'model_type': 'baseline',
                'model_name': model_key
            }
            
            # Add probability scores if available
            if probabilities is not None:
                # Get class labels from model and map to readable names
                if hasattr(model, 'classes_'):
                    classes = model.classes_
                    result['probabilities'] = {
                        label_map.get(int(cls), str(cls)): float(prob) 
                        for cls, prob in zip(classes, probabilities)
                    }
                else:
                    result['probabilities'] = {
                        label_map.get(i, f'class_{i}'): float(prob) 
                        for i, prob in enumerate(probabilities)
                    }
            
            return result
        
        except Exception as e:
            logger.error(f"Error in baseline prediction: {e}")
            return {'error': f"Prediction failed: {str(e)}"}
    
    def predict_transformer(self, text: str) -> Dict[str, Any]:
        """
        Run inference using the transformer model.
        
        Args:
            text: Input text to classify.
        
        Returns:
            Dictionary with prediction results.
        """
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(text)
            if not is_valid:
                return {'error': error_msg}
            
            # Check if transformer is loaded
            if self.transformer is None:
                return {'error': "Transformer model not loaded."}
            
            model = self.transformer['model']
            tokenizer = self.transformer['tokenizer']
            id2label = self.transformer['id2label']
            device = self.transformer['device']
            
            # Preprocess
            processed_text = self.preprocess_text(text)
            
            # Measure inference time
            start_time = time.time()
            
            # Tokenize
            inputs = tokenizer(
                processed_text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = softmax(logits, dim=-1)
            
            # Get prediction
            predicted_class_id = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][predicted_class_id].item()
            
            # Get label from id2label mapping
            predicted_label = id2label.get(predicted_class_id, f"class_{predicted_class_id}")
            
            # Convert numeric labels to readable format
            label_map = {0: 'Non-Hate Speech', 1: 'Hate Speech', '0': 'Non-Hate Speech', '1': 'Hate Speech'}
            readable_label = label_map.get(predicted_label, label_map.get(predicted_class_id, predicted_label))
            
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Format results
            result = {
                'label': readable_label,
                'confidence': float(confidence),
                'inference_time_ms': round(inference_time, 2),
                'model_type': 'transformer',
                'model_name': 'distilbert'
            }
            
            # Add all class probabilities with readable labels
            probabilities = {}
            for class_id, prob in enumerate(probs[0].cpu().numpy()):
                label = id2label.get(class_id, f"class_{class_id}")
                readable = label_map.get(label, label_map.get(class_id, label))
                probabilities[readable] = float(prob)
            
            result['probabilities'] = probabilities
            
            return result
        
        except Exception as e:
            logger.error(f"Error in transformer prediction: {e}")
            return {'error': f"Prediction failed: {str(e)}"}
    
    def predict_toxicity(self, text: str, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Run inference using the toxicity model (multi-label).
        
        Args:
            text: Input text to classify.
            threshold: Threshold for flagging toxicity categories.
        
        Returns:
            Dictionary with toxicity scores for all categories.
        """
        try:
            # Load model
            toxicity_data = self.model_manager.load_toxicity_model()
            if toxicity_data is None:
                return {'error': "Toxicity model not loaded"}
            
            model = toxicity_data['model']
            tokenizer = toxicity_data['tokenizer']
            labels = toxicity_data['labels']
            device = toxicity_data['device']
            
            # Tokenize
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            )
            
            # Move to device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                
                # Apply sigmoid for multi-label
                probs = torch.sigmoid(logits).cpu().numpy()[0]
            
            # Create results
            toxicity_scores = []
            flagged_categories = []
            
            for i, label in enumerate(labels):
                score = float(probs[i])
                is_flagged = score > threshold
                
                toxicity_scores.append({
                    'category': label,
                    'score': score,
                    'flagged': is_flagged
                })
                
                if is_flagged:
                    flagged_categories.append(label)
            
            is_toxic = len(flagged_categories) > 0
            
            return {
                'is_toxic': is_toxic,
                'toxicity_scores': toxicity_scores,
                'flagged_categories': flagged_categories,
                'model_type': 'toxicity'
            }
            
        except Exception as e:
            logger.error(f"Error in toxicity prediction: {e}")
            return {'error': f"Prediction failed: {str(e)}"}
    
    def predict(self, text: str, model_key: str) -> Dict[str, Any]:
        """
        Run inference using the specified model.
        
        Args:
            text: Input text to classify.
            model_key: Key identifying the model (logreg, svm, distilbert, or toxicity).
        
        Returns:
            Dictionary with prediction results.
        """
        if model_key in ['logreg', 'svm']:
            return self.predict_baseline(text, model_key)
        elif model_key == 'distilbert':
            return self.predict_transformer(text)
        elif model_key == 'toxicity':
            return self.predict_toxicity(text)
        else:
            return {'error': f"Unknown model key: {model_key}"}
