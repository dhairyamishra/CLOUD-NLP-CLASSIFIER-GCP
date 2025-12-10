"""
Multi-Head Toxicity Classification Model.
Uses a shared DistilBERT encoder with independent classification heads for each toxicity category.
"""
import torch
import torch.nn as nn
from transformers import DistilBertModel, DistilBertConfig
from typing import Dict, List, Optional


class MultiHeadToxicityModel(nn.Module):
    """
    Multi-head toxicity classification model.
    
    Architecture:
        Input Text → DistilBERT Encoder → [CLS] Token → Dropout → 6 Linear Heads → 6 Toxicity Predictions
    
    Args:
        model_name: Name or path of pretrained DistilBERT model
        labels: List of toxicity category labels
        dropout_rate: Dropout probability for regularization
    """
    
    def __init__(
        self, 
        model_name: str = "distilbert-base-uncased",
        labels: Optional[List[str]] = None,
        dropout_rate: float = 0.1
    ):
        super().__init__()
        
        # Default labels if not provided
        if labels is None:
            labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
        
        self.labels = labels
        self.num_labels = len(labels)
        
        # Load DistilBERT encoder
        self.encoder = DistilBertModel.from_pretrained(model_name)
        self.hidden_size = self.encoder.config.hidden_size  # 768 for distilbert-base
        
        # Dropout for regularization
        self.dropout = nn.Dropout(dropout_rate)
        
        # Create independent classification heads for each label
        self.heads = nn.ModuleDict({
            label: nn.Linear(self.hidden_size, 1)
            for label in labels
        })
        
        # Loss function (Binary Cross-Entropy with Logits)
        self.loss_fn = nn.BCEWithLogitsLoss()
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the model.
        
        Args:
            input_ids: Token IDs (batch_size, seq_length)
            attention_mask: Attention mask (batch_size, seq_length)
            labels: Ground truth labels (batch_size, num_labels), optional
        
        Returns:
            Dictionary containing:
                - logits: Dict of logits for each label
                - loss: Total loss (if labels provided)
        """
        # Get encoder outputs
        encoder_outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Extract [CLS] token representation (first token)
        cls_output = encoder_outputs.last_hidden_state[:, 0, :]  # (batch_size, hidden_size)
        
        # Apply dropout
        cls_output = self.dropout(cls_output)
        
        # Pass through each classification head
        logits = {}
        for label, head in self.heads.items():
            logits[label] = head(cls_output).squeeze(-1)  # (batch_size,)
        
        # Prepare output
        output = {"logits": logits}
        
        # Calculate loss if labels provided
        if labels is not None:
            losses = []
            for i, label in enumerate(self.labels):
                label_logits = logits[label]
                label_targets = labels[:, i]
                loss = self.loss_fn(label_logits, label_targets)
                losses.append(loss)
            
            # Average loss across all heads
            total_loss = torch.stack(losses).mean()
            output["loss"] = total_loss
        
        return output
    
    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        threshold: float = 0.5
    ) -> Dict[str, torch.Tensor]:
        """
        Make predictions with probability scores.
        
        Args:
            input_ids: Token IDs (batch_size, seq_length)
            attention_mask: Attention mask (batch_size, seq_length)
            threshold: Probability threshold for binary classification
        
        Returns:
            Dictionary containing:
                - probabilities: Dict of probabilities for each label
                - predictions: Dict of binary predictions for each label
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(input_ids, attention_mask)
            logits = outputs["logits"]
            
            # Apply sigmoid to get probabilities
            probabilities = {
                label: torch.sigmoid(logit)
                for label, logit in logits.items()
            }
            
            # Apply threshold for binary predictions
            predictions = {
                label: (prob > threshold).float()
                for label, prob in probabilities.items()
            }
        
        return {
            "probabilities": probabilities,
            "predictions": predictions
        }
    
    def get_config(self) -> Dict:
        """Get model configuration."""
        return {
            "model_type": "MultiHeadToxicityModel",
            "encoder": self.encoder.config.name_or_path,
            "hidden_size": self.hidden_size,
            "num_labels": self.num_labels,
            "labels": self.labels,
            "dropout_rate": self.dropout.p
        }
