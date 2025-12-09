"""
Model definition for multi-head toxicity classification.
"""

import torch
import torch.nn as nn
from transformers import AutoModel

class MultiHeadToxicityModel(nn.Module):
    """
    Multi-head toxicity classification model.
    
    Uses a shared DistilBERT encoder with separate linear heads for each
    toxicity label. Each head performs binary classification.
    """
    
    def __init__(self, base_model_name: str, label_names: list):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        hidden_size = self.encoder.config.hidden_size

        self.dropout = nn.Dropout(0.1)

        # One linear head per label
        self.heads = nn.ModuleDict({
            name: nn.Linear(hidden_size, 1) for name in label_names
        })

        self.loss_fn = nn.BCEWithLogitsLoss()

    def forward(self, input_ids, attention_mask=None, labels=None):
        """
        Forward pass through the model.
        """
        # DistilBERT doesn't have pooler_output; use [CLS] token (index 0)
        enc_out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = enc_out.last_hidden_state  # (B, L, H)
        cls_repr = hidden_states[:, 0, :]          # (B, H)

        cls_repr = self.dropout(cls_repr)

        logits = {
            name: head(cls_repr).squeeze(-1) for name, head in self.heads.items()
        }

        loss = None
        if labels is not None:
            losses = []
            for name in self.heads.keys():
                # labels[name] is (B,)
                if name in labels:
                    losses.append(self.loss_fn(logits[name], labels[name]))
            loss = sum(losses) / len(losses) if losses else None

        return {"loss": loss, "logits": logits}