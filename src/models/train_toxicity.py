"""
Training script for toxicity classification using DistilBertForSequenceClassification.
Compatible with CLOUD-NLP-CLASSIFIER-GCP server's ModelManager.
"""
import os
import argparse
import random
import json
import yaml
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, DistilBertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Train Toxicity Model")
    parser.add_argument("--config", type=str, default="config/config_toxicity.yaml", help="Path to config file")
    parser.add_argument("--epochs", type=int, default=None, help="Override epochs")
    return parser.parse_args()

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

class JigsawToxicityDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, label_columns: List[str], max_length: int = 256):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.label_columns = label_columns
        self.max_length = max_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # Handle cases where column might be 'comment_text' or 'text'
        text = str(row.get("comment_text", row.get("text", "")))

        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        item = {k: v.squeeze(0) for k, v in enc.items()}

        # Create a single float tensor for labels (Multi-label classification)
        labels = []
        for col in self.label_columns:
            val = row[col] if col in row else 0.0
            labels.append(float(val))
        
        item["labels"] = torch.tensor(labels, dtype=torch.float)

        return item

def train_one_epoch(model, dataloader, optimizer, epoch_idx, step_losses, global_step, device, plot_interval):
    model.train()
    running_loss = 0.0
    n_batches = 0

    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()
        
        # DistilBertForSequenceClassification will use BCEWithLogitsLoss if labels are float and problem_type is multi_label
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        n_batches += 1
        global_step += 1

        if global_step % plot_interval == 0:
            current_avg_loss = running_loss / n_batches
            step_losses.append((global_step, current_avg_loss))

        if n_batches % 100 == 0:
            logger.info(f"Epoch {epoch_idx} | Step {n_batches}/{len(dataloader)} | Global Step {global_step} | Loss: {running_loss / n_batches:.4f}")

    avg_loss = running_loss / max(n_batches, 1)
    logger.info(f"Epoch {epoch_idx} finished. Avg training loss: {avg_loss:.4f}")
    return avg_loss, global_step

@torch.no_grad()
def evaluate(model, dataloader, device, label_columns, threshold=0.5):
    model.eval()
    all_losses = []
    
    # Store predictions and targets for metrics
    all_preds = []
    all_targets = []

    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        all_losses.append(loss.item())
        
        logits = outputs.logits
        probs = torch.sigmoid(logits)
        preds = (probs > threshold).float()
        
        all_preds.append(preds.cpu().numpy())
        all_targets.append(labels.cpu().numpy())

    avg_loss = float(np.mean(all_losses))
    
    all_preds = np.vstack(all_preds)
    all_targets = np.vstack(all_targets)
    
    # Calculate per-class accuracy
    metrics = {}
    for i, label in enumerate(label_columns):
        acc = accuracy_score(all_targets[:, i], all_preds[:, i])
        metrics[label] = {"accuracy": acc}
    
    # Calculate global metrics
    micro_f1 = f1_score(all_targets, all_preds, average='micro', zero_division=0)
    macro_f1 = f1_score(all_targets, all_preds, average='macro', zero_division=0)
    metrics["_global"] = {"micro_f1": micro_f1, "macro_f1": macro_f1}

    return avg_loss, metrics

def plot_training_loss(step_losses, save_path):
    if not step_losses:
        return
    steps, losses = zip(*step_losses)
    plt.figure(figsize=(10, 6))
    plt.plot(steps, losses, 'b-', linewidth=2, marker='o', markersize=4)
    plt.xlabel('Training Step')
    plt.ylabel('Average Loss')
    plt.title('Training Loss Over Steps')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Loss plot saved to {save_path}")

def main():
    args = parse_args()
    config = load_config(args.config)
    
    # Overrides
    if args.epochs:
        config['training']['num_train_epochs'] = args.epochs

    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() and config.get('device') == 'cuda' else "cpu")
    logger.info(f"Using device: {device}")

    # Load Data
    train_path = config['data']['train_path']
    try:
        # Check if file exists
        if not os.path.exists(train_path):
             logger.error(f"Training data not found at {train_path}")
             return

        df_all = pd.read_csv(train_path)
        
        # Check against label columns
        label_cols = config['model']['labels']
        missing = [c for c in label_cols if c not in df_all.columns]
        if missing:
             logger.error(f"Missing label columns in {train_path}: {missing}")
             return
             
    except Exception as e:
        logger.error(f"Failed to load data from {train_path}: {e}")
        return

    # Basic split
    train_df, val_df = train_test_split(df_all, test_size=0.1, random_state=42)
    logger.info(f"Train size: {len(train_df)}, Val size: {len(val_df)}")

    # Tokenizer & ID Mappings
    model_name = config['model']['name']
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    max_len = config['model']['max_seq_length']
    
    # Prepare label mappings for the model config
    id2label = {str(i): label for i, label in enumerate(label_cols)}
    label2id = {label: i for i, label in enumerate(label_cols)}

    train_dataset = JigsawToxicityDataset(train_df, tokenizer, label_cols, max_len)
    val_dataset = JigsawToxicityDataset(val_df, tokenizer, label_cols, max_len)

    train_loader = DataLoader(
        train_dataset, 
        batch_size=config['training']['train_batch_size'], 
        shuffle=True
    )
    val_loader = DataLoader(
        val_dataset, 
        batch_size=config['training']['eval_batch_size'], 
        shuffle=False
    )

    # Model Initialization (Standard Hugging Face)
    logger.info(f"Initializing standard DistilBertForSequenceClassification with {len(label_cols)} labels")
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label_cols),
        problem_type="multi_label_classification",
        id2label=id2label,
        label2id=label2id
    )
    model.to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(config['training']['learning_rate']))

    best_val_loss = float("inf")
    save_dir = config['model_save_dir']
    os.makedirs(save_dir, exist_ok=True)
    
    step_losses = []
    global_step = 0
    plot_interval = config['training'].get('plot_step_interval', 500)

    num_epochs = config['training']['num_train_epochs']
    
    for epoch in range(1, num_epochs + 1):
        train_loss, global_step = train_one_epoch(
            model, train_loader, optimizer, epoch, step_losses, global_step, device, plot_interval
        )
        val_loss, metrics = evaluate(model, val_loader, device, label_cols, config['training'].get('threshold', 0.5))

        logger.info(f"Validation loss: {val_loss:.4f}")
        logger.info(f"  Macros | F1: {metrics['_global']['macro_f1']:.4f}")
        for name in label_cols:
             if name in metrics:
                logger.info(f"  {name:14s} | acc: {metrics[name]['accuracy']:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            # Save standard Hugging Face model
            # This saves config.json (with id2label) and pytorch_model.bin/model.safetensors
            model.save_pretrained(save_dir)
            tokenizer.save_pretrained(save_dir)
            
            # Save labels.json for server compatibility (ModelManager.load_transformer_model expects this)
            labels_data = {
                "id2label": id2label,
                "label2id": label2id,
                "classes": label_cols
            }
            with open(os.path.join(save_dir, "labels.json"), 'w') as f:
                json.dump(labels_data, f, indent=2)
                
            logger.info(f"Saved best model and compatibility artifacts to {save_dir}")

    # Plot
    if step_losses:
        plot_path = config.get('output_plot_path', 'training_loss_plot.png')
        plot_training_loss(step_losses, plot_path)

if __name__ == "__main__":
    main()