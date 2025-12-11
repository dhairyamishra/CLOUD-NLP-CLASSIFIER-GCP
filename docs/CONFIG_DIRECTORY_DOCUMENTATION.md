# Config Directory Documentation

## Overview

The `config/` directory contains YAML configuration files that control all training hyperparameters, model settings, data paths, and evaluation metrics for the three model types in this project: **Baseline Models** (TF-IDF + classical ML), **Transformer Models** (DistilBERT), and **Toxicity Models** (multi-label DistilBERT).

**Purpose**: Centralize all training configurations to enable reproducible experiments, easy hyperparameter tuning, and environment-specific optimizations (local vs cloud, quick vs full-scale training).

---

## Directory Structure

```
config/
├── __init__.py                          # Empty Python package marker
├── config_baselines.yaml                # TF-IDF + Logistic Regression/Linear SVM
├── config_toxicity.yaml                 # Multi-label toxicity classifier (6 heads)
├── config_transformer.yaml              # DistilBERT local training (full-scale)
├── config_transformer_cloud.yaml        # DistilBERT cloud/GPU training
└── config_transformer_fullscale.yaml    # DistilBERT intensive training (max performance)
```

---

## Configuration Files

### 1. `config_baselines.yaml`

**Purpose**: Configure TF-IDF vectorization and classical ML models (Logistic Regression, Linear SVM).

**Key Sections**:

#### Vectorizer Settings
- **Type**: `tfidf` (TF-IDF weighting)
- **Max Features**: 10,000 (vocabulary size)
- **N-gram Range**: [1, 3] (unigrams, bigrams, trigrams)
- **Min/Max DF**: 2 / 0.95 (document frequency thresholds)
- **Normalization**: L2 norm
- **Sublinear TF**: Enabled (1 + log(tf) scaling)

#### Logistic Regression
- **Regularization (C)**: 1.0 (inverse strength)
- **Solver**: SAGA (supports L1/L2/elastic-net)
- **Penalty**: L2 (Ridge regularization)
- **Max Iterations**: 1000
- **Class Weight**: Balanced (handles imbalance)
- **Parallelization**: All CPU cores (`n_jobs=-1`)
- **Hyperparameter Grid**: C ∈ [0.1, 0.5, 1.0, 2.0, 5.0, 10.0], penalty ∈ [L1, L2]

#### Linear SVM
- **Regularization (C)**: 1.0
- **Loss**: Squared hinge
- **Penalty**: L2
- **Max Iterations**: 2000
- **Dual Formulation**: True (recommended for n_samples < n_features)
- **Hyperparameter Grid**: C ∈ [0.1, 0.5, 1.0, 2.0, 5.0, 10.0], loss ∈ [hinge, squared_hinge]

#### Evaluation Metrics
- Accuracy, F1 (macro/weighted), Precision (macro), Recall (macro)
- Confusion matrix and classification report saved

**Output**: Models saved to `models/baselines/`

---

### 2. `config_toxicity.yaml`

**Purpose**: Configure multi-label toxicity detection model with 6 independent binary classifiers.

**Key Sections**:

#### Model Settings
- **Base Model**: `distilbert-base-uncased`
- **Max Sequence Length**: 256 tokens
- **Labels**: 6 toxicity categories
  - toxic
  - severe_toxic
  - obscene
  - threat
  - insult
  - identity_hate

#### Training Hyperparameters
- **Batch Size**: 16 (train/eval)
- **Learning Rate**: 2e-5
- **Epochs**: 3
- **Threshold**: 0.5 (binary classification cutoff)
- **Plot Interval**: Every 500 steps

#### Data Paths
- Train: `data/toxicity/train.csv`
- Test: `data/toxicity/test.csv`
- Test Labels: `data/toxicity/test_labels.csv`

**Output**: Model saved to `models/toxicity_multi_head/`, training loss plot generated

---

### 3. `config_transformer.yaml`

**Purpose**: Full-scale local DistilBERT training with comprehensive early stopping and advanced optimization.

**Key Sections**:

#### Model Settings
- **Base Model**: `distilbert-base-uncased`
- **Max Sequence Length**: 256 tokens
- **Dropout**: 0.1 (model + attention)
- **Num Labels**: Auto-detected from dataset

#### Training Hyperparameters
- **Batch Size**: 32 (train), 64 (eval)
- **Learning Rate**: 3e-5
- **Epochs**: 15 (with early stopping)
- **Weight Decay**: 0.01 (L2 regularization)
- **Warmup Ratio**: 0.15 (15% of total steps)
- **Gradient Accumulation**: 2 steps (effective batch = 64)
- **Max Grad Norm**: 1.0 (gradient clipping)

#### Optimization
- **FP16**: Disabled by default (enable for GPU with Tensor Cores)
- **Optimizer**: AdamW (PyTorch implementation)
- **Adam Betas**: (0.9, 0.999)
- **Epsilon**: 1e-8

#### DataLoader
- **Num Workers**: 0 (Windows fix to avoid multiprocessing hangs; use 2-4 on Linux/Mac)
- **Pin Memory**: True (speeds up CPU→GPU transfer)

#### Early Stopping
- **Enabled**: True
- **Patience**: 5 evaluation cycles
- **Metric**: `eval_f1_macro`
- **Mode**: Maximize
- **Min Delta**: 0.001 (minimum improvement threshold)
- **Restore Best Weights**: True

#### Learning Rate Scheduler
- **Type**: `cosine_with_restarts`
- **Num Cycles**: 3 (restarts for exploration)

#### Logging & Checkpointing
- **Logging Steps**: 25
- **Eval Steps**: 100
- **Save Steps**: 100
- **Save Total Limit**: 5 checkpoints
- **Load Best Model at End**: True
- **Metric for Best Model**: `f1_macro`

**Output**: Model saved to `models/transformer/distilbert/`

**Expected Performance**: 90-93% accuracy, 0.88-0.91 F1 score

---

### 4. `config_transformer_cloud.yaml`

**Purpose**: Optimized for GCP GPU VMs (e.g., n1-standard-4 with T4/V100).

**Key Differences from Local Config**:

#### Training Hyperparameters
- **Batch Size**: 64 (train), 128 (eval) — larger for GPU
- **Epochs**: 10
- **FP16**: Enabled (mixed precision for faster training)
- **Gradient Accumulation**: 2 (effective batch = 128)
- **DataLoader Workers**: 4 (parallel data loading)

#### Learning Rate Scheduler
- **Type**: `cosine` (smoother convergence)

#### Logging & Checkpointing
- **Logging Steps**: 20
- **Save Total Limit**: 3 checkpoints (save storage)

#### Cloud Overrides Section
- Provides explicit overrides when `--mode=cloud` CLI flag is used
- Automatically applies cloud-optimized settings

**Output**: Model saved to `models/transformer/distilbert_cloud/`

**Expected Performance**: 90-93% accuracy in 15-25 min on V100, ~$0.80 cost

---

### 5. `config_transformer_fullscale.yaml`

**Purpose**: Intensive training for maximum performance (research/production).

**Key Differences from Standard Config**:

#### Model Settings
- **Max Sequence Length**: 512 tokens (full context)
- **Dropout**: 0.15 (higher regularization)

#### Training Hyperparameters
- **Batch Size**: 16 (train), 32 (eval) — smaller for longer sequences
- **Learning Rate**: 2e-5 (lower for stability)
- **Epochs**: 25 (with patient early stopping)
- **Weight Decay**: 0.02 (higher L2)
- **Warmup Ratio**: 0.2 (20% warmup)
- **Gradient Accumulation**: 4 (effective batch = 64)
- **FP16 Opt Level**: O2 (aggressive mixed precision)
- **Label Smoothing**: 0.1 (better generalization)

#### Early Stopping
- **Patience**: 8 cycles (very patient)
- **Min Delta**: 0.0005 (fine-grained improvements)

#### Learning Rate Scheduler
- **Type**: `cosine_with_restarts`
- **Num Cycles**: 5 (more exploration)

#### Logging & Checkpointing
- **Logging Steps**: 10 (very frequent)
- **Eval Steps**: 50
- **Save Steps**: 50
- **Save Total Limit**: 10 checkpoints

**Output**: Model saved to `models/transformer/distilbert_fullscale/`

**Expected Performance**: 92-95% accuracy, 0.90-0.93 F1 score

**Training Time**: 2-4 hours (GPU), 10-20 hours (CPU)

**Recommended Hardware**: NVIDIA RTX 3060+ (12GB+ VRAM), 8+ CPU cores, 16GB+ RAM

---

## Configuration Usage Patterns

### Loading Configurations

All training scripts use YAML configs via Python's `yaml` library:

```python
import yaml

with open('config/config_transformer.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access nested values
batch_size = config['training']['train_batch_size']
model_name = config['model']['name']
```

### CLI Overrides

Transformer training supports CLI overrides:

```bash
# Use cloud config
python -m src.models.transformer_training \
    --config config/config_transformer_cloud.yaml \
    --mode cloud \
    --fp16

# Override specific parameters
python -m src.models.transformer_training \
    --epochs 5 \
    --batch-size 32 \
    --learning-rate 3e-5
```

### Environment-Specific Selection

**Local Training** (CPU/single GPU):
- Use `config_transformer.yaml`
- Smaller batches, fewer epochs
- Disable FP16 if no Tensor Cores

**Cloud Training** (GCP GPU VM):
- Use `config_transformer_cloud.yaml`
- Larger batches, FP16 enabled
- Parallel data loading

**Intensive Training** (Research/Production):
- Use `config_transformer_fullscale.yaml`
- Maximum sequence length, patient early stopping
- Label smoothing, multiple LR restarts

---

## Key Design Decisions

### 1. Separation by Model Type
Each model family (baselines, transformer, toxicity) has dedicated configs to avoid parameter conflicts and improve clarity.

### 2. Environment-Specific Configs
Separate local/cloud/fullscale configs optimize for hardware constraints and training budgets without manual parameter tuning.

### 3. Comprehensive Early Stopping
All transformer configs include early stopping to prevent overfitting and reduce training time (critical for cloud costs).

### 4. Hyperparameter Grids
Baseline configs include `param_grid` sections for optional grid search, enabling automated hyperparameter tuning.

### 5. Windows Compatibility
`dataloader_num_workers: 0` in local configs prevents multiprocessing hangs on Windows (common PyTorch issue).

### 6. Reproducibility
All configs include `seed: 42` for deterministic training results.

---

## Configuration Parameters Reference

### Common Parameters Across All Configs

| Parameter | Purpose | Typical Values |
|-----------|---------|----------------|
| `train_batch_size` | Training batch size | 16-64 |
| `eval_batch_size` | Evaluation batch size | 32-128 |
| `learning_rate` | Optimizer learning rate | 2e-5 to 5e-5 |
| `num_train_epochs` | Maximum training epochs | 3-25 |
| `seed` | Random seed | 42 |
| `device` | Compute device | cuda/cpu/mps |

### Transformer-Specific Parameters

| Parameter | Purpose | Typical Values |
|-----------|---------|----------------|
| `max_seq_length` | Max tokens per input | 128-512 |
| `warmup_ratio` | Warmup steps as % of total | 0.1-0.2 |
| `gradient_accumulation_steps` | Accumulate gradients | 1-4 |
| `fp16` | Mixed precision training | true/false |
| `early_stopping.patience` | Epochs before stopping | 3-8 |
| `lr_scheduler.type` | LR schedule strategy | linear/cosine/cosine_with_restarts |

### Baseline-Specific Parameters

| Parameter | Purpose | Typical Values |
|-----------|---------|----------------|
| `max_features` | TF-IDF vocabulary size | 5000-10000 |
| `ngram_range` | N-gram range | [1,2] or [1,3] |
| `C` | Regularization strength | 0.1-10.0 |
| `penalty` | Regularization type | l1/l2 |
| `solver` | Optimization algorithm | saga/lbfgs |

---

## Integration with Training Scripts

### Baseline Models (`src/models/baselines.py`)
Reads `config_baselines.yaml` to configure:
- TF-IDF vectorizer parameters
- Logistic Regression hyperparameters
- Linear SVM hyperparameters
- Optional grid search ranges

### Transformer Models (`src/models/transformer_training.py`)
Reads transformer configs to configure:
- HuggingFace `TrainingArguments`
- Early stopping callback
- LR scheduler selection
- Data loading and preprocessing

### Toxicity Models (`src/models/toxicity_training.py`)
Reads `config_toxicity.yaml` to configure:
- Multi-label model architecture
- Training loop hyperparameters
- Loss plotting intervals

---

## Best Practices

### 1. Start with Standard Configs
Use `config_transformer.yaml` or `config_baselines.yaml` as starting points before customizing.

### 2. Test Locally Before Cloud
Validate configs with 1-2 epochs locally to catch errors before expensive cloud training.

### 3. Monitor Early Stopping
Check early stopping logs to ensure patience values are appropriate (not stopping too early/late).

### 4. Use FP16 on Compatible GPUs
Enable `fp16: true` for NVIDIA GPUs with Tensor Cores (RTX series, T4, V100, A100) for 2-3x speedup.

### 5. Adjust Batch Size for Memory
If OOM errors occur, reduce `train_batch_size` and increase `gradient_accumulation_steps` to maintain effective batch size.

### 6. Save Checkpoints Strategically
Balance `save_steps` and `save_total_limit` to avoid excessive disk usage while preserving best models.

---

## Troubleshooting

### Issue: Training Hangs on Windows
**Solution**: Set `dataloader_num_workers: 0` in config (already default in local configs).

### Issue: Out of Memory (OOM)
**Solution**: Reduce `train_batch_size`, `max_seq_length`, or enable `gradient_accumulation_steps`.

### Issue: Early Stopping Too Aggressive
**Solution**: Increase `early_stopping.patience` or decrease `early_stopping.min_delta`.

### Issue: Training Too Slow
**Solution**: Enable `fp16: true`, increase `train_batch_size`, or use cloud config with GPU.

### Issue: Poor Model Performance
**Solution**: Try fullscale config with longer sequences, more epochs, and label smoothing.

---

## Summary

The `config/` directory provides a robust, environment-aware configuration system that:
- Separates concerns by model type (baselines, transformer, toxicity)
- Optimizes for deployment context (local, cloud, intensive)
- Enables reproducible experiments via seed control
- Supports CLI overrides for quick experimentation
- Includes comprehensive early stopping and optimization strategies

All training scripts in `src/models/` rely on these configs, making hyperparameter tuning and environment adaptation straightforward without code changes.
