"""
Transformer model training script using DistilBERT for text classification.

Supports:
- Advanced learning rate schedulers (linear, cosine, polynomial, constant)
- Early stopping based on validation metrics
- Mixed precision training (FP16)
- Cloud training mode with optimized settings
- Local vs Cloud configuration
"""
import os
import json
import logging
import time
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import yaml
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
    TrainerCallback,
    get_scheduler
)
from datasets import Dataset as HFDataset

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train DistilBERT transformer model for text classification"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config_transformer.yaml",
        help="Path to configuration YAML file"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["local", "cloud"],
        default="local",
        help="Training mode: 'local' for local training, 'cloud' for cloud training"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory for model artifacts"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Override number of training epochs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override training batch size"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=None,
        help="Override learning rate"
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Enable mixed precision training (FP16)"
    )
    parser.add_argument(
        "--no-early-stopping",
        action="store_true",
        help="Disable early stopping"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override random seed"
    )
    
    return parser.parse_args()


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    logger.info(f"Random seed set to: {seed}")


def load_config(config_path: str = "config/config_transformer.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Configuration loaded from: {config_path}")
    return config


def apply_cli_overrides(config: dict, args: argparse.Namespace) -> dict:
    """
    Apply command-line argument overrides to configuration.
    
    Args:
        config: Base configuration dictionary
        args: Parsed command-line arguments
        
    Returns:
        Updated configuration dictionary
    """
    # Apply mode-specific settings
    if args.mode == "cloud":
        logger.info("Applying cloud training mode settings...")
        # Cloud mode typically uses larger batches, more epochs, and enables optimizations
        if 'cloud_overrides' in config:
            cloud_config = config['cloud_overrides']
            # Apply cloud overrides
            for key, value in cloud_config.items():
                if key in config:
                    if isinstance(value, dict) and isinstance(config[key], dict):
                        config[key].update(value)
                    else:
                        config[key] = value
            logger.info("Cloud overrides applied from config file")
    
    # Apply CLI overrides (these take highest priority)
    if args.output_dir is not None:
        config['model_save_dir'] = args.output_dir
        logger.info(f"Output directory overridden: {args.output_dir}")
    
    if args.epochs is not None:
        config['training']['num_train_epochs'] = args.epochs
        logger.info(f"Epochs overridden: {args.epochs}")
    
    if args.batch_size is not None:
        config['training']['train_batch_size'] = args.batch_size
        config['training']['eval_batch_size'] = args.batch_size
        logger.info(f"Batch size overridden: {args.batch_size}")
    
    if args.learning_rate is not None:
        config['training']['learning_rate'] = args.learning_rate
        logger.info(f"Learning rate overridden: {args.learning_rate}")
    
    if args.fp16:
        config['training']['fp16'] = True
        logger.info("FP16 mixed precision enabled via CLI")
    
    if args.no_early_stopping:
        config['training']['early_stopping']['enabled'] = False
        logger.info("Early stopping disabled via CLI")
    
    if args.seed is not None:
        config['seed'] = args.seed
        logger.info(f"Random seed overridden: {args.seed}")
    
    return config


def load_data(config: dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load train, validation, and test datasets."""
    train_path = config['data']['train_path']
    val_path = config['data']['val_path']
    test_path = config['data']['test_path']
    
    logger.info(f"Loading training data from: {train_path}")
    train_df = pd.read_csv(train_path)
    
    logger.info(f"Loading validation data from: {val_path}")
    val_df = pd.read_csv(val_path)
    
    logger.info(f"Loading test data from: {test_path}")
    test_df = pd.read_csv(test_path)
    
    logger.info(f"Train samples: {len(train_df)}")
    logger.info(f"Validation samples: {len(val_df)}")
    logger.info(f"Test samples: {len(test_df)}")
    
    return train_df, val_df, test_df


def prepare_labels(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> Tuple[LabelEncoder, np.ndarray, np.ndarray, np.ndarray]:
    """
    Encode string labels to integers.
    
    Returns:
        label_encoder: Fitted LabelEncoder
        train_labels: Encoded training labels
        val_labels: Encoded validation labels
        test_labels: Encoded test labels
    """
    logger.info("Encoding labels...")
    
    label_encoder = LabelEncoder()
    train_labels = label_encoder.fit_transform(train_df['label'])
    val_labels = label_encoder.transform(val_df['label'])
    test_labels = label_encoder.transform(test_df['label'])
    
    logger.info(f"Number of classes: {len(label_encoder.classes_)}")
    logger.info(f"Classes: {label_encoder.classes_.tolist()}")
    
    return label_encoder, train_labels, val_labels, test_labels


def tokenize_data(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_labels: np.ndarray,
    val_labels: np.ndarray,
    test_labels: np.ndarray,
    tokenizer: DistilBertTokenizer,
    max_length: int
) -> Tuple[HFDataset, HFDataset, HFDataset]:
    """
    Tokenize text data and create HuggingFace datasets.
    
    Returns:
        train_dataset: Tokenized training dataset
        val_dataset: Tokenized validation dataset
        test_dataset: Tokenized test dataset
    """
    logger.info("Tokenizing data...")
    
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=max_length
        )
    
    # Create HuggingFace datasets
    train_dataset = HFDataset.from_dict({
        'text': train_df['text'].tolist(),
        'label': train_labels.tolist()
    })
    
    val_dataset = HFDataset.from_dict({
        'text': val_df['text'].tolist(),
        'label': val_labels.tolist()
    })
    
    test_dataset = HFDataset.from_dict({
        'text': test_df['text'].tolist(),
        'label': test_labels.tolist()
    })
    
    # Tokenize
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)
    
    # Set format for PyTorch
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    val_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    
    logger.info("Tokenization complete!")
    
    return train_dataset, val_dataset, test_dataset


def compute_metrics(eval_pred) -> Dict[str, float]:
    """
    Compute metrics for evaluation.
    
    Args:
        eval_pred: Tuple of (predictions, labels)
        
    Returns:
        Dictionary of metrics
    """
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    metrics = {
        'accuracy': accuracy_score(labels, predictions),
        'f1_macro': f1_score(labels, predictions, average='macro'),
        'f1_weighted': f1_score(labels, predictions, average='weighted'),
        'precision_macro': precision_score(labels, predictions, average='macro', zero_division=0),
        'recall_macro': recall_score(labels, predictions, average='macro', zero_division=0)
    }
    
    return metrics


class TimingCallback(TrainerCallback):
    """Callback to track training time."""
    
    def __init__(self):
        self.start_time = None
        self.total_time = 0
    
    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        logger.info("Training started...")
    
    def on_train_end(self, args, state, control, **kwargs):
        self.total_time = time.time() - self.start_time
        logger.info(f"Training completed in {self.total_time:.2f} seconds ({self.total_time/60:.2f} minutes)")


def train_model(
    train_dataset: HFDataset,
    val_dataset: HFDataset,
    model: DistilBertForSequenceClassification,
    config: dict,
    output_dir: str
) -> Tuple[Trainer, float]:
    """
    Train the transformer model with advanced optimizations.
    
    Supports:
    - Multiple learning rate schedulers (linear, cosine, polynomial, constant)
    - Early stopping based on validation metrics
    - Mixed precision training (FP16)
    - Gradient accumulation
    - Learning rate warmup
    
    Returns:
        trainer: Trained Trainer object
        training_time: Total training time in seconds
    """
    logger.info("Setting up training...")
    
    # Training arguments
    training_config = config['training']
    
    # Determine learning rate scheduler type
    lr_scheduler_config = training_config.get('lr_scheduler', {})
    lr_scheduler_type = lr_scheduler_config.get('type', 'linear')
    
    # Map scheduler types to transformers scheduler names
    scheduler_mapping = {
        'linear': 'linear',
        'cosine': 'cosine',
        'cosine_with_restarts': 'cosine_with_restarts',
        'polynomial': 'polynomial',
        'constant': 'constant',
        'constant_with_warmup': 'constant_with_warmup'
    }
    
    lr_scheduler_type_mapped = scheduler_mapping.get(lr_scheduler_type, 'linear')
    logger.info(f"Using learning rate scheduler: {lr_scheduler_type_mapped}")
    
    # Check FP16 support
    fp16_enabled = training_config.get('fp16', False)
    if fp16_enabled:
        if torch.cuda.is_available():
            logger.info("FP16 mixed precision training enabled")
        else:
            logger.warning("FP16 requested but CUDA not available, disabling FP16")
            fp16_enabled = False
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=training_config['num_train_epochs'],
        per_device_train_batch_size=training_config['train_batch_size'],
        per_device_eval_batch_size=training_config['eval_batch_size'],
        learning_rate=training_config['learning_rate'],
        weight_decay=training_config['weight_decay'],
        warmup_ratio=training_config['warmup_ratio'],
        warmup_steps=training_config.get('warmup_steps', 0),
        lr_scheduler_type=lr_scheduler_type_mapped,
        gradient_accumulation_steps=training_config['gradient_accumulation_steps'],
        max_grad_norm=training_config['max_grad_norm'],
        logging_steps=training_config['logging_steps'],
        eval_steps=training_config['eval_steps'],
        save_steps=training_config['save_steps'],
        save_total_limit=training_config['save_total_limit'],
        eval_strategy="steps",  # Changed from evaluation_strategy for transformers 4.57+
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model=training_config['early_stopping']['metric'],
        greater_is_better=(training_config['early_stopping']['mode'] == 'max'),
        fp16=fp16_enabled,
        fp16_opt_level=training_config.get('fp16_opt_level', 'O1'),
        logging_dir=f"{output_dir}/logs",
        report_to="none",  # Disable wandb/tensorboard for now
        seed=config['seed'],
        dataloader_num_workers=training_config.get('dataloader_num_workers', 0),
        dataloader_pin_memory=training_config.get('dataloader_pin_memory', True)
    )
    
    # Callbacks
    callbacks = []
    
    # Add early stopping if enabled
    if training_config['early_stopping']['enabled']:
        early_stopping = EarlyStoppingCallback(
            early_stopping_patience=training_config['early_stopping']['patience']
        )
        callbacks.append(early_stopping)
        logger.info(f"Early stopping enabled with patience: {training_config['early_stopping']['patience']}")
        logger.info(f"Monitoring metric: {training_config['early_stopping']['metric']} ({training_config['early_stopping']['mode']})")
    else:
        logger.info("Early stopping disabled")
    
    # Add timing callback
    timing_callback = TimingCallback()
    callbacks.append(timing_callback)
    
    # Log training configuration
    logger.info("=" * 60)
    logger.info("Training Configuration:")
    logger.info(f"  Epochs: {training_config['num_train_epochs']}")
    logger.info(f"  Train Batch Size: {training_config['train_batch_size']}")
    logger.info(f"  Eval Batch Size: {training_config['eval_batch_size']}")
    logger.info(f"  Learning Rate: {training_config['learning_rate']}")
    logger.info(f"  Weight Decay: {training_config['weight_decay']}")
    logger.info(f"  Warmup Ratio: {training_config['warmup_ratio']}")
    logger.info(f"  LR Scheduler: {lr_scheduler_type_mapped}")
    logger.info(f"  Gradient Accumulation Steps: {training_config['gradient_accumulation_steps']}")
    logger.info(f"  Max Grad Norm: {training_config['max_grad_norm']}")
    logger.info(f"  FP16: {fp16_enabled}")
    logger.info("=" * 60)
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=callbacks
    )
    
    # Train
    logger.info("Starting training...")
    trainer.train()
    
    training_time = timing_callback.total_time
    
    return trainer, training_time


def evaluate_model(
    trainer: Trainer,
    test_dataset: HFDataset,
    label_encoder: LabelEncoder
) -> Tuple[Dict[str, float], float]:
    """
    Evaluate the model on test set.
    
    Returns:
        metrics: Dictionary of evaluation metrics
        avg_inference_time: Average inference time per sample (ms)
    """
    logger.info("Evaluating model on test set...")
    
    # Evaluate
    eval_results = trainer.evaluate(test_dataset)
    
    # Measure inference time
    logger.info("Measuring inference time...")
    test_samples = test_dataset.select(range(min(100, len(test_dataset))))
    
    start_time = time.time()
    predictions = trainer.predict(test_samples)
    inference_time = time.time() - start_time
    
    avg_inference_time = (inference_time / len(test_samples)) * 1000  # Convert to ms
    
    logger.info(f"Average inference time: {avg_inference_time:.2f} ms per sample")
    
    # Get predictions for full test set
    predictions = trainer.predict(test_dataset)
    pred_labels = np.argmax(predictions.predictions, axis=1)
    true_labels = predictions.label_ids
    
    # Compute detailed metrics
    from src.models.evaluation import evaluate_model as eval_model_detailed
    
    # Convert labels to strings for classification report
    label_names = [str(label) for label in label_encoder.classes_]
    
    metrics = eval_model_detailed(
        y_true=true_labels,
        y_pred=pred_labels,
        y_pred_proba=torch.softmax(torch.tensor(predictions.predictions), dim=1).numpy(),
        labels=label_names,
        model_name="DistilBERT",
        detailed=True
    )
    
    return metrics, avg_inference_time


def save_model_and_artifacts(
    model: DistilBertForSequenceClassification,
    tokenizer: DistilBertTokenizer,
    label_encoder: LabelEncoder,
    output_dir: str,
    metrics: Dict[str, float],
    training_time: float,
    avg_inference_time: float
):
    """Save model, tokenizer, label mappings, and training info."""
    logger.info(f"Saving model and artifacts to: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model and tokenizer
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("Model and tokenizer saved!")
    
    # Save label mappings - convert numpy types to Python native types
    label2id = {str(label): int(idx) for idx, label in enumerate(label_encoder.classes_)}
    id2label = {str(idx): str(label) for idx, label in enumerate(label_encoder.classes_)}
    
    labels_path = os.path.join(output_dir, "labels.json")
    with open(labels_path, 'w') as f:
        json.dump({
            'label2id': label2id,
            'id2label': id2label,
            'classes': [str(label) for label in label_encoder.classes_.tolist()]
        }, f, indent=2)
    logger.info(f"Label mappings saved to: {labels_path}")
    
    # Save training info - convert all to Python native types
    training_info = {
        'metrics': {k: float(v) for k, v in metrics.items()},
        'training_time_seconds': float(training_time),
        'training_time_minutes': float(training_time / 60),
        'avg_inference_time_ms': float(avg_inference_time),
        'num_classes': int(len(label_encoder.classes_)),
        'classes': [str(label) for label in label_encoder.classes_.tolist()]
    }
    
    info_path = os.path.join(output_dir, "training_info.json")
    with open(info_path, 'w') as f:
        json.dump(training_info, f, indent=2)
    logger.info(f"Training info saved to: {info_path}")


def main():
    """Main training pipeline."""
    logger.info("=" * 80)
    logger.info("Starting Transformer Training Pipeline")
    logger.info("=" * 80)
    
    # Parse command-line arguments
    args = parse_args()
    logger.info(f"Training mode: {args.mode}")
    
    # Load configuration
    config = load_config(args.config)
    
    # Apply CLI overrides
    config = apply_cli_overrides(config, args)
    
    # Set random seed
    set_seed(config['seed'])
    
    # Check device
    device = config.get('device', 'cuda')
    if device == 'cuda' and not torch.cuda.is_available():
        logger.warning("CUDA not available, falling back to CPU")
        device = 'cpu'
    logger.info(f"Using device: {device}")
    
    # Load data
    train_df, val_df, test_df = load_data(config)
    
    # Prepare labels
    label_encoder, train_labels, val_labels, test_labels = prepare_labels(
        train_df, val_df, test_df
    )
    
    # Initialize tokenizer
    model_name = config['model']['name']
    logger.info(f"Loading tokenizer: {model_name}")
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    
    # Tokenize data
    max_length = config['model']['max_seq_length']
    train_dataset, val_dataset, test_dataset = tokenize_data(
        train_df, val_df, test_df,
        train_labels, val_labels, test_labels,
        tokenizer, max_length
    )
    
    # Initialize model
    num_labels = len(label_encoder.classes_)
    logger.info(f"Loading model: {model_name}")
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels
    )
    
    # Move model to device
    model.to(device)
    
    # Train model
    output_dir = config['model_save_dir']
    trainer, training_time = train_model(
        train_dataset, val_dataset, model, config, output_dir
    )
    
    # Evaluate model
    metrics, avg_inference_time = evaluate_model(
        trainer, test_dataset, label_encoder
    )
    
    # Save model and artifacts
    save_model_and_artifacts(
        model, tokenizer, label_encoder, output_dir,
        metrics, training_time, avg_inference_time
    )
    
    # Print summary
    logger.info("=" * 80)
    logger.info("Training Summary")
    logger.info("=" * 80)
    logger.info(f"Model: {model_name}")
    logger.info(f"Number of classes: {num_labels}")
    logger.info(f"Training time: {training_time:.2f}s ({training_time/60:.2f} min)")
    logger.info(f"Average inference time: {avg_inference_time:.2f} ms/sample")
    logger.info(f"Test Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"Test F1 (Macro): {metrics['f1_macro']:.4f}")
    logger.info(f"Test F1 (Weighted): {metrics['f1_weighted']:.4f}")
    logger.info(f"Model saved to: {output_dir}")
    logger.info("=" * 80)
    logger.info("Training pipeline completed successfully!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
