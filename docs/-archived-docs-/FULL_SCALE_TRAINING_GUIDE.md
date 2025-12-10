# Full-Scale Model Training Guide

## Overview

This guide covers comprehensive training for all available models in the CLOUD-NLP-CLASSIFIER-GCP project with detailed configurations, early stopping, and performance optimization.

## Table of Contents

1. [Models Overview](#models-overview)
2. [Configuration Details](#configuration-details)
3. [Training Scripts](#training-scripts)
4. [Usage Instructions](#usage-instructions)
5. [Expected Performance](#expected-performance)
6. [Troubleshooting](#troubleshooting)

---

## Models Overview

### 1. Baseline Models (Classical ML)

**Models Trained:**
- **Logistic Regression** - Linear classifier with L1/L2 regularization
- **Linear SVM** - Support Vector Machine with linear kernel

**Key Features:**
- TF-IDF vectorization with 10,000 features
- N-grams: unigrams, bigrams, and trigrams (1-3)
- Balanced class weights for handling imbalance
- Multi-core CPU parallelization
- Convergence monitoring with verbose output

**Training Time:**
- CPU: 5-15 minutes
- Memory: ~2-4 GB

### 2. DistilBERT Transformer (Standard Configuration)

**Model:** `distilbert-base-uncased`

**Key Features:**
- Sequence length: 256 tokens
- Training epochs: 15 (with early stopping)
- Early stopping patience: 5 evaluation cycles
- Learning rate scheduler: Cosine with restarts (3 cycles)
- Gradient accumulation: 2 steps (effective batch size: 64)
- Dropout: 0.1 for regularization

**Training Time:**
- GPU (RTX 3060+): 30-60 minutes
- CPU: 4-8 hours
- Memory: ~6-8 GB (GPU), ~8-12 GB (CPU)

### 3. DistilBERT Transformer (Intensive Full-Scale)

**Model:** `distilbert-base-uncased`

**Key Features:**
- Sequence length: 512 tokens (maximum context)
- Training epochs: 25 (with early stopping)
- Early stopping patience: 8 evaluation cycles (very patient)
- Learning rate scheduler: Cosine with restarts (5 cycles)
- Gradient accumulation: 4 steps (effective batch size: 64)
- Dropout: 0.15 for better regularization
- Mixed precision (FP16 O2) for GPU acceleration
- Label smoothing: 0.1 for better generalization

**Training Time:**
- GPU (RTX 3060+): 2-4 hours
- GPU (T4/V100): 1-2 hours
- CPU: 10-20 hours
- Memory: ~10-14 GB (GPU), ~16-24 GB (CPU)

---

## Configuration Details

### Baseline Models Configuration

**File:** `config/config_baselines.yaml`

```yaml
# Vectorizer settings
vectorizer:
  type: "tfidf"
  max_features: 10000  # Rich vocabulary
  ngram_range: [1, 3]  # Unigrams, bigrams, trigrams
  min_df: 2
  max_df: 0.95
  sublinear_tf: true
  use_idf: true
  smooth_idf: true
  norm: "l2"

# Logistic Regression
logistic_regression:
  C: 1.0
  max_iter: 1000
  solver: "saga"
  penalty: "l2"
  class_weight: "balanced"
  n_jobs: -1
  verbose: 1

# Linear SVM
linear_svm:
  C: 1.0
  max_iter: 2000
  loss: "squared_hinge"
  penalty: "l2"
  class_weight: "balanced"
  verbose: 1
```

### Transformer Standard Configuration

**File:** `config/config_transformer.yaml`

```yaml
# Model settings
model:
  name: "distilbert-base-uncased"
  max_seq_length: 256
  dropout: 0.1
  attention_dropout: 0.1

# Training
training:
  train_batch_size: 32
  eval_batch_size: 64
  learning_rate: 3.0e-5
  num_train_epochs: 15
  warmup_ratio: 0.15
  gradient_accumulation_steps: 2
  
  # Early stopping
  early_stopping:
    enabled: true
    patience: 5
    metric: "eval_f1_macro"
    mode: "max"
    min_delta: 0.001
    restore_best_weights: true
  
  # LR scheduler
  lr_scheduler:
    type: "cosine_with_restarts"
    num_cycles: 3
  
  # Checkpointing
  eval_steps: 100
  save_steps: 100
  save_total_limit: 5
  load_best_model_at_end: true
```

### Transformer Intensive Configuration

**File:** `config/config_transformer_fullscale.yaml`

```yaml
# Model settings
model:
  name: "distilbert-base-uncased"
  max_seq_length: 512  # Maximum context
  dropout: 0.15
  attention_dropout: 0.15

# Training
training:
  train_batch_size: 16  # Smaller for longer sequences
  eval_batch_size: 32
  learning_rate: 2.0e-5
  num_train_epochs: 25
  warmup_ratio: 0.2
  gradient_accumulation_steps: 4
  
  # Optimization
  fp16: true
  fp16_opt_level: "O2"
  
  # Early stopping
  early_stopping:
    enabled: true
    patience: 8  # Very patient
    metric: "eval_f1_macro"
    mode: "max"
    min_delta: 0.0005
    restore_best_weights: true
  
  # LR scheduler
  lr_scheduler:
    type: "cosine_with_restarts"
    num_cycles: 5
  
  # Checkpointing
  eval_steps: 50
  save_steps: 50
  save_total_limit: 10
  load_best_model_at_end: true
  
  # Advanced
  label_smoothing_factor: 0.1
```

---

## Training Scripts

### Master Training Script (All Models)

**Python Script:** `train_all_models.py`

Trains all models sequentially with comprehensive logging and error handling.

**Features:**
- Prerequisite checking (data files, configs)
- Sequential model training
- Real-time progress monitoring
- Duration tracking for each model
- JSON training report generation
- Colored terminal output
- Graceful interrupt handling

**PowerShell Script:** `scripts/train_all_models.ps1`

Windows-optimized version with PowerShell-specific features.

**Features:**
- All Python script features
- PowerShell color output
- `-SkipConfirmation` flag for automation
- `-ContinueOnFailure` flag for resilience
- Custom log file support

---

## Usage Instructions

### Option 1: Train All Models (Recommended)

#### Windows (PowerShell):

```powershell
# Interactive mode (with confirmation)
.\scripts\train_all_models.ps1

# Automated mode (skip confirmation)
.\scripts\train_all_models.ps1 -SkipConfirmation

# Continue on failure
.\scripts\train_all_models.ps1 -ContinueOnFailure

# Custom log file
.\scripts\train_all_models.ps1 -LogFile "my_training.log"
```

#### Linux/Mac/Windows (Python):

```bash
# Interactive mode
python train_all_models.py

# Direct execution (Unix)
chmod +x train_all_models.py
./train_all_models.py
```

### Option 2: Train Individual Models

#### Baseline Models Only:

```bash
# Windows
python run_baselines.py

# Linux/Mac
python run_baselines.py
```

#### Transformer Standard:

```bash
python run_transformer.py
# OR
python -m src.models.transformer_training --config config/config_transformer.yaml
```

#### Transformer Intensive:

```bash
python -m src.models.transformer_training --config config/config_transformer_fullscale.yaml
```

### Option 3: Custom Training with CLI Arguments

```bash
# Override specific parameters
python -m src.models.transformer_training \
    --config config/config_transformer.yaml \
    --epochs 20 \
    --batch-size 16 \
    --learning-rate 2e-5 \
    --fp16

# Cloud training mode
python -m src.models.transformer_training \
    --config config/config_transformer_cloud.yaml \
    --mode cloud \
    --fp16
```

---

## Expected Performance

### Baseline Models

| Model | Accuracy | F1 Score | Training Time | Inference |
|-------|----------|----------|---------------|-----------|
| Logistic Regression | 85-88% | 0.83-0.86 | 5-10 min | 0.5-1 ms |
| Linear SVM | 85-88% | 0.83-0.86 | 5-10 min | 0.5-1 ms |

### Transformer Models

| Configuration | Accuracy | F1 Score | Training Time (GPU) | Inference |
|---------------|----------|----------|---------------------|-----------|
| Standard (256 seq) | 90-93% | 0.88-0.91 | 30-60 min | 5-10 ms |
| Intensive (512 seq) | 92-95% | 0.90-0.93 | 2-4 hours | 8-15 ms |

### Performance Comparison

```
Model Performance vs Speed Trade-off:

Fast & Good:     Logistic Regression (0.6ms, 85-88% acc)
Fast & Good:     Linear SVM (0.6ms, 85-88% acc)
Balanced:        DistilBERT Standard (8ms, 90-93% acc)
Best Accuracy:   DistilBERT Intensive (12ms, 92-95% acc)
```

---

## Training Output

### Training Report

After training completes, a JSON report is generated: `training_report.json`

**Example:**

```json
{
  "training_session": {
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T14:30:00",
    "total_duration_seconds": 16200,
    "total_duration_formatted": "4h 30m 0s"
  },
  "models_trained": [
    {
      "name": "Baseline Models",
      "status": "success",
      "duration": 600,
      "timestamp": "2024-01-15T10:00:00"
    },
    {
      "name": "DistilBERT Standard",
      "status": "success",
      "duration": 3600,
      "timestamp": "2024-01-15T10:10:00"
    },
    {
      "name": "DistilBERT Intensive",
      "status": "success",
      "duration": 12000,
      "timestamp": "2024-01-15T11:10:00"
    }
  ],
  "summary": {
    "total_models": 3,
    "successful": 3,
    "failed": 0,
    "interrupted": 0
  }
}
```

### Model Artifacts

**Baseline Models:**
```
models/baselines/
├── logistic_regression_model.pkl
├── linear_svm_model.pkl
├── tfidf_vectorizer.pkl
├── label_encoder.pkl
├── training_info.json
└── evaluation_results.json
```

**Transformer Models:**
```
models/transformer/distilbert/
├── config.json
├── pytorch_model.bin
├── tokenizer_config.json
├── vocab.txt
├── label_mapping.json
├── training_info.json
└── evaluation_results.json

models/transformer/distilbert_fullscale/
├── (same structure as above)
└── checkpoint-{best}/
    ├── config.json
    ├── pytorch_model.bin
    └── training_args.bin
```

---

## Monitoring Training

### Real-Time Monitoring

**Terminal Output:**
- Training progress bars
- Loss and metrics per epoch
- Evaluation results
- Early stopping notifications
- Checkpoint saving confirmations

**Example Output:**
```
Epoch 1/15: 100%|████████| 500/500 [02:30<00:00, 3.33it/s]
  train_loss: 0.4523
  eval_loss: 0.3821
  eval_accuracy: 0.8912
  eval_f1_macro: 0.8845
  ✓ New best model! (F1: 0.8845)

Epoch 2/15: 100%|████████| 500/500 [02:28<00:00, 3.37it/s]
  train_loss: 0.3214
  eval_loss: 0.3156
  eval_accuracy: 0.9123
  eval_f1_macro: 0.9078
  ✓ New best model! (F1: 0.9078)
```

### GPU Monitoring (if applicable)

```bash
# Monitor GPU usage
nvidia-smi -l 1

# Monitor GPU with detailed info
watch -n 1 nvidia-smi
```

---

## Troubleshooting

### Common Issues

#### 1. Out of Memory (OOM)

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
- Reduce `train_batch_size` (e.g., 32 → 16 → 8)
- Reduce `max_seq_length` (e.g., 512 → 256 → 128)
- Increase `gradient_accumulation_steps` (maintains effective batch size)
- Enable `fp16` for mixed precision (reduces memory by ~50%)
- Use CPU training if GPU memory is insufficient

**Example:**
```bash
# Reduce memory usage
python -m src.models.transformer_training \
    --config config/config_transformer.yaml \
    --batch-size 8 \
    --gradient-accumulation-steps 8
```

#### 2. Training Too Slow

**Symptoms:**
- Very long training time per epoch
- Low GPU utilization

**Solutions:**
- Enable `fp16` mixed precision
- Increase `dataloader_num_workers` (2-4)
- Increase `train_batch_size` if memory allows
- Use GPU instead of CPU
- Reduce `max_seq_length` if not critical

#### 3. Model Not Converging

**Symptoms:**
- Loss not decreasing
- Accuracy plateauing early
- High validation loss

**Solutions:**
- Increase `num_train_epochs`
- Adjust `learning_rate` (try 2e-5, 3e-5, 5e-5)
- Increase `warmup_ratio` (0.1 → 0.15 → 0.2)
- Reduce `weight_decay` if overfitting
- Check data quality and class balance

#### 4. Early Stopping Too Aggressive

**Symptoms:**
- Training stops too early
- Model could improve further

**Solutions:**
- Increase `patience` (5 → 8 → 10)
- Reduce `min_delta` (0.001 → 0.0005)
- Change `metric` to monitor (try `eval_loss` instead of `eval_f1_macro`)

#### 5. Missing Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 6. Data Files Not Found

**Symptoms:**
```
FileNotFoundError: data/processed/train.csv not found
```

**Solution:**
```bash
# Run preprocessing first
python run_preprocess.py
```

---

## Best Practices

### 1. Start Small, Scale Up

```bash
# 1. Quick test (3 epochs)
python -m src.models.transformer_training --epochs 3

# 2. Standard training (15 epochs)
python run_transformer.py

# 3. Full-scale training (25 epochs)
python -m src.models.transformer_training --config config/config_transformer_fullscale.yaml
```

### 2. Monitor Training Closely

- Watch first few epochs for convergence
- Check GPU/CPU utilization
- Monitor memory usage
- Verify early stopping is working

### 3. Save Intermediate Results

- Enable checkpointing (`save_steps`)
- Keep multiple checkpoints (`save_total_limit`)
- Save best model (`load_best_model_at_end`)

### 4. Use Early Stopping

- Always enable early stopping
- Set appropriate patience (5-8 for standard, 8-10 for intensive)
- Monitor the right metric (`eval_f1_macro` for balanced classes)

### 5. Experiment with Hyperparameters

- Learning rate: [1e-5, 2e-5, 3e-5, 5e-5]
- Batch size: [8, 16, 32, 64]
- Warmup ratio: [0.1, 0.15, 0.2]
- Dropout: [0.1, 0.15, 0.2]

---

## Advanced Topics

### Hyperparameter Tuning

For systematic hyperparameter search, consider using:
- Optuna
- Ray Tune
- Weights & Biases Sweeps

### Distributed Training

For multi-GPU training:
```bash
python -m torch.distributed.launch \
    --nproc_per_node=2 \
    src/models/transformer_training.py \
    --config config/config_transformer.yaml
```

### Cloud Training

See `docs/PHASE10_ADVANCED_TRAINING_SUMMARY.md` for GCP cloud training instructions.

---

## Summary

This guide provides comprehensive instructions for full-scale model training with:

✅ **3 Model Configurations** - Baseline, Standard Transformer, Intensive Transformer  
✅ **Early Stopping** - Automatic convergence detection  
✅ **Detailed Logging** - Real-time progress and metrics  
✅ **Performance Tracking** - Duration and resource monitoring  
✅ **Error Handling** - Graceful failures and recovery  
✅ **Reproducibility** - Fixed seeds and deterministic training  

**Estimated Total Training Time:**
- **GPU (RTX 3060+):** 2-6 hours
- **CPU (8+ cores):** 12-24 hours

**Expected Final Performance:**
- **Best Accuracy:** 92-95% (DistilBERT Intensive)
- **Best Speed:** 0.6ms (Baseline Models)
- **Best Balance:** 90-93% @ 8ms (DistilBERT Standard)

---

## Next Steps

After training completes:

1. **Evaluate Models:** `python run_tests.py`
2. **Compare Results:** Check `training_report.json`
3. **Test API:** `python scripts/client_example.py`
4. **Deploy:** Build Docker image and deploy to production

For deployment instructions, see:
- `docs/DOCKER_GUIDE.md`
- `docs/MULTI_MODEL_DOCKER_GUIDE.md`
- `docs/DOCKER_CLOUD_DEPLOYMENT_SUMMARY.md`

---

**Happy Training! 🚀**
