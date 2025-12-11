# Models Directory Documentation

## Overview

The `models/` directory stores all trained model artifacts for the three classification systems: **Baseline Models** (TF-IDF + classical ML), **Transformer Models** (DistilBERT for hate speech), and **Toxicity Models** (multi-label DistilBERT). These models are production-ready and used by both the FastAPI backend and Streamlit UI.

**Purpose**: Centralized storage for serialized models, tokenizers, configurations, and training metadata to enable inference without retraining.

---

## Directory Structure

```
models/
├── baselines/                           # Classical ML models (TF-IDF pipelines)
│   ├── logistic_regression_tfidf.joblib # Logistic Regression + TF-IDF (459 KB)
│   └── linear_svm_tfidf.joblib          # Linear SVM + TF-IDF (459 KB)
│
├── toxicity_multi_head/                 # Multi-label toxicity classifier
│   ├── config.json                      # Model architecture config
│   ├── labels.json                      # 6 toxicity label mappings
│   ├── model.safetensors                # Model weights (268 MB)
│   ├── special_tokens_map.json          # Special tokens ([CLS], [SEP], etc.)
│   ├── tokenizer.json                   # Fast tokenizer config
│   ├── tokenizer_config.json            # Tokenizer settings
│   └── vocab.txt                        # WordPiece vocabulary (30,522 tokens)
│
└── transformer/                         # DistilBERT hate speech classifiers
    ├── distilbert/                      # Standard local training
    │   ├── checkpoint-*/                # Training checkpoints (5 saved)
    │   ├── config.json                  # Model architecture config
    │   ├── labels.json                  # Binary label mappings
    │   ├── model.safetensors            # Model weights (268 MB)
    │   ├── special_tokens_map.json      # Special tokens
    │   ├── tokenizer_config.json        # Tokenizer settings
    │   ├── training_info.json           # Training metrics & timing
    │   └── vocab.txt                    # WordPiece vocabulary
    │
    └── distilbert_fullscale/            # Intensive full-scale training
        ├── checkpoint-*/                # Training checkpoints (10 saved)
        ├── config.json                  # Model architecture config
        ├── labels.json                  # Binary label mappings
        ├── model.safetensors            # Model weights (268 MB)
        ├── special_tokens_map.json      # Special tokens
        ├── tokenizer_config.json        # Tokenizer settings
        ├── training_info.json           # Training metrics & timing
        └── vocab.txt                    # WordPiece vocabulary
```

---

## Model Types

### 1. Baseline Models (`baselines/`)

**Format**: Scikit-learn pipelines serialized with `joblib`

**Components**:
- TF-IDF vectorizer (10,000 features, n-grams [1,3])
- Classifier (Logistic Regression or Linear SVM)

**Files**:

#### `logistic_regression_tfidf.joblib` (459 KB)
- **Algorithm**: Logistic Regression with L2 regularization
- **Regularization**: C=1.0
- **Solver**: SAGA (supports L1/L2)
- **Class Weight**: Balanced
- **Expected Performance**: 85-88% accuracy, 0.82-0.85 F1
- **Inference Speed**: 0.6-0.7 ms (12-23x faster than DistilBERT)

#### `linear_svm_tfidf.joblib` (459 KB)
- **Algorithm**: Linear Support Vector Machine
- **Loss**: Squared hinge
- **Regularization**: C=1.0, L2 penalty
- **Class Weight**: Balanced
- **Expected Performance**: 85-88% accuracy, 0.82-0.85 F1
- **Inference Speed**: 0.6 ms (23x faster than DistilBERT)

**Loading**:
```python
import joblib
pipeline = joblib.load('models/baselines/logistic_regression_tfidf.joblib')
prediction = pipeline.predict(["sample text"])
```

**Use Cases**:
- Ultra-fast inference (sub-millisecond)
- Resource-constrained environments
- High-throughput batch processing
- Baseline comparison for transformer models

---

### 2. Toxicity Multi-Head Model (`toxicity_multi_head/`)

**Format**: HuggingFace DistilBERT with multi-label classification head

**Architecture**:
- **Base Model**: `distilbert-base-uncased`
- **Layers**: 6 transformer layers
- **Attention Heads**: 12
- **Hidden Dimension**: 768
- **Vocab Size**: 30,522 tokens
- **Max Sequence Length**: 512 tokens
- **Problem Type**: Multi-label classification (6 independent binary classifiers)

**Labels** (6 toxicity categories):
1. `toxic` (id: 0)
2. `severe_toxic` (id: 1)
3. `obscene` (id: 2)
4. `threat` (id: 3)
5. `insult` (id: 4)
6. `identity_hate` (id: 5)

**Files**:

#### `config.json` (884 bytes)
- Model architecture configuration
- Dropout rates: 0.1 (model), 0.1 (attention), 0.2 (classifier)
- Label mappings (id2label, label2id)
- Problem type: `multi_label_classification`

#### `labels.json` (425 bytes)
- Explicit label mappings for all 6 toxicity classes
- Used by inference code to map predictions to human-readable labels

#### `model.safetensors` (268 MB)
- Model weights in SafeTensors format (safer than pickle)
- Contains all 66M parameters

#### `tokenizer.json` (742 KB)
- Fast tokenizer configuration (Rust-based)
- WordPiece tokenization rules

#### `vocab.txt` (231 KB)
- WordPiece vocabulary (30,522 tokens)
- Includes special tokens: [PAD], [UNK], [CLS], [SEP], [MASK]

**Loading**:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained('models/toxicity_multi_head/')
tokenizer = AutoTokenizer.from_pretrained('models/toxicity_multi_head/')
```

**Output**: 6 sigmoid probabilities (one per toxicity type), threshold at 0.5

**Use Cases**:
- Fine-grained toxicity detection
- Multi-label classification (text can have multiple toxicity types)
- Content moderation with detailed breakdowns

---

### 3. Transformer Models (`transformer/`)

**Format**: HuggingFace DistilBERT with binary classification head

**Architecture**:
- **Base Model**: `distilbert-base-uncased`
- **Layers**: 6 transformer layers
- **Attention Heads**: 12
- **Hidden Dimension**: 768
- **Vocab Size**: 30,522 tokens
- **Problem Type**: Single-label classification (binary)

**Labels** (hate speech detection):
- `Regular Speech` (id: 0)
- `Hate Speech` (id: 1)

---

#### 3.1 Standard Model (`transformer/distilbert/`)

**Training Configuration**:
- **Epochs**: 15 (with early stopping)
- **Batch Size**: 32 (train), 64 (eval)
- **Learning Rate**: 3e-5
- **Max Sequence Length**: 256 tokens
- **Early Stopping**: Patience 5, metric `eval_f1_macro`
- **LR Scheduler**: Cosine with restarts (3 cycles)
- **Gradient Accumulation**: 2 steps (effective batch = 64)

**Performance** (from `training_info.json`):
- **Accuracy**: 96.29%
- **F1 Macro**: 93.44%
- **F1 Weighted**: 96.31%
- **Precision Macro**: 92.89%
- **Recall Macro**: 94.03%
- **ROC-AUC**: 98.99%
- **Training Time**: 10.44 minutes
- **Inference Time**: 2.24 ms (average)

**Checkpoints**:
- 5 checkpoints saved: 800, 1000, 1100, 1200, 1300 steps
- Best model selected based on F1 macro score

**Files**:

#### `config.json` (587 bytes)
- Model architecture configuration
- Problem type: `single_label_classification`
- Dropout rates: 0.1 (model/attention), 0.2 (classifier)

#### `labels.json` (213 bytes)
- Binary label mappings: "Regular Speech" (0), "Hate Speech" (1)

#### `training_info.json` (552 bytes)
- Complete training metrics (accuracy, F1, precision, recall, ROC-AUC)
- Training time in seconds and minutes
- Average inference time in milliseconds
- Number of classes and class names

#### `model.safetensors` (268 MB)
- Fine-tuned model weights (66M parameters)

**Loading**:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained('models/transformer/distilbert/')
tokenizer = AutoTokenizer.from_pretrained('models/transformer/distilbert/')
```

**Use Cases**:
- High-accuracy hate speech detection
- Production deployment (balanced speed/accuracy)
- API serving with ~8ms latency

---

#### 3.2 Full-Scale Model (`transformer/distilbert_fullscale/`)

**Training Configuration**:
- **Epochs**: 25 (with patient early stopping)
- **Batch Size**: 16 (train), 32 (eval)
- **Learning Rate**: 2e-5
- **Max Sequence Length**: 512 tokens (full context)
- **Early Stopping**: Patience 8, metric `eval_f1_macro`
- **LR Scheduler**: Cosine with restarts (5 cycles)
- **Gradient Accumulation**: 4 steps (effective batch = 64)
- **Dropout**: 0.15 (higher regularization)
- **Label Smoothing**: 0.1

**Performance** (from `training_info.json`):
- **Accuracy**: 96.69% (+0.4% vs standard)
- **F1 Macro**: 94.17% (+0.73% vs standard)
- **F1 Weighted**: 96.72% (+0.41% vs standard)
- **Precision Macro**: 93.52% (+0.63% vs standard)
- **Recall Macro**: 94.85% (+0.82% vs standard)
- **ROC-AUC**: 99.00% (+0.01% vs standard)
- **Training Time**: 12.15 minutes (+1.71 min vs standard)
- **Inference Time**: 1.80 ms (20% faster than standard)

**Checkpoints**:
- 10 checkpoints saved: 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500, 1550, 1600 steps
- Some checkpoints empty (training stopped early)

**Key Improvements**:
- Longer sequences (512 vs 256 tokens) capture more context
- Higher dropout (0.15 vs 0.1) improves generalization
- More patient early stopping (8 vs 5) allows better convergence
- Label smoothing (0.1) reduces overconfidence

**Use Cases**:
- Maximum accuracy requirements
- Research experiments
- Benchmark for model improvements

---

## Model File Formats

### SafeTensors Format
All transformer models use `.safetensors` instead of `.bin` (PyTorch pickle):
- **Safer**: No arbitrary code execution risk
- **Faster**: Memory-mapped loading
- **Smaller**: More efficient serialization
- **Cross-platform**: Works across PyTorch/TensorFlow/JAX

### Joblib Format
Baseline models use `joblib` for scikit-learn pipelines:
- **Efficient**: Optimized for NumPy arrays
- **Compressed**: Smaller file sizes
- **Fast**: Quick serialization/deserialization

---

## Model Loading Patterns

### API Server (`src/api/server.py`)

**Baseline Models**:
```python
import joblib
self.pipeline = joblib.load(str(model_path))
self.classes = self.pipeline.classes_.tolist()
```

**Transformer Models**:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

self.model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
self.model.to(self.device)
self.model.eval()
```

### Streamlit UI (`src/ui/utils/model_manager.py`)

**Lazy Loading**:
```python
def load_transformer_model(self):
    if not self.transformer_dir.exists():
        return None
    
    model = AutoModelForSequenceClassification.from_pretrained(str(self.transformer_dir))
    tokenizer = AutoTokenizer.from_pretrained(str(self.transformer_dir))
    
    return {
        'model': model.to(self.device),
        'tokenizer': tokenizer,
        'labels': self._load_labels(self.transformer_dir / 'labels.json')
    }
```

---

## Model Comparison

| Model | Size | Accuracy | F1 Macro | Inference (ms) | Speed vs DistilBERT | Use Case |
|-------|------|----------|----------|----------------|---------------------|----------|
| **Linear SVM** | 459 KB | 85-88% | 0.82-0.85 | 0.6 | 23x faster | Ultra-fast, high-throughput |
| **Logistic Regression** | 459 KB | 85-88% | 0.82-0.85 | 0.66 | 12x faster | Fast, balanced |
| **DistilBERT (Standard)** | 268 MB | 96.29% | 93.44% | 2.24 | 1x (baseline) | Production, balanced |
| **DistilBERT (Fullscale)** | 268 MB | 96.69% | 94.17% | 1.80 | 1.2x faster | Maximum accuracy |
| **Toxicity Multi-Head** | 268 MB | N/A | N/A | ~2-3 | Similar | Multi-label toxicity |

---

## Checkpoint Management

### Purpose
Checkpoints enable:
- **Recovery**: Resume training after interruptions
- **Model Selection**: Choose best checkpoint based on validation metrics
- **Experimentation**: Compare different training stages

### Storage Strategy
- **Standard Model**: Keep 5 best checkpoints (save_total_limit=5)
- **Fullscale Model**: Keep 10 best checkpoints (save_total_limit=10)
- **Checkpoint Frequency**: Every 100 steps (standard), every 50 steps (fullscale)

### Checkpoint Contents
Each checkpoint directory contains:
- `pytorch_model.bin` or `model.safetensors` (model weights)
- `optimizer.pt` (optimizer state for resuming)
- `scheduler.pt` (LR scheduler state)
- `trainer_state.json` (training progress metadata)
- `training_args.bin` (training arguments)

### Cleanup
Checkpoints are excluded from Docker images and GCP uploads via `.dockerignore` and `-NoCheckpoints` flag to save storage (reduces 12 GB → 770 MB).

---

## Model Versioning

### Current Versions
All models tracked in `MODEL_VERSION.json`:
```json
{
  "version": "1.0.0",
  "models": {
    "distilbert": "1.0.0",
    "distilbert_fullscale": "1.0.0",
    "logistic_regression": "1.0.0",
    "linear_svm": "1.0.0",
    "toxicity_multi_head": "1.0.0"
  }
}
```

### Version Format
- **MAJOR**: Breaking changes (architecture change, incompatible API)
- **MINOR**: New features (improved accuracy, new model variant)
- **PATCH**: Bug fixes (training fixes, minor improvements)

---

## Storage & Deployment

### Local Storage
- Models stored in `models/` directory
- Total size: ~1.5 GB (with checkpoints: ~12 GB)
- Excluded from git via `.gitignore`

### GCP Storage
- Uploaded to `gs://nlp-classifier-models/`
- Organized by user prefix (e.g., `DPM-MODELS/`)
- Version-controlled via `MODEL_VERSION.json`
- Optimized uploads skip checkpoints (770 MB vs 12 GB)

### Docker Images
- Baseline models: Included (459 KB each)
- Transformer models: Included (268 MB each)
- Checkpoints: Excluded via `.dockerignore`
- Total image size: ~2.5 GB

---

## Model Selection Guide

### Choose Baseline Models When:
- Inference speed is critical (<1ms required)
- Memory is limited (<100 MB)
- Throughput is high (>1000 req/s)
- Accuracy 85-88% is acceptable

### Choose Standard DistilBERT When:
- Accuracy is important (>95%)
- Inference time 2-8ms is acceptable
- Balanced speed/accuracy needed
- Production deployment

### Choose Fullscale DistilBERT When:
- Maximum accuracy required (>96%)
- Longer context needed (512 tokens)
- Research or benchmarking
- Training time is not critical

### Choose Toxicity Model When:
- Multi-label classification needed
- Fine-grained toxicity detection
- Content moderation with breakdowns

---

## Integration Points

### FastAPI Server
- Loads models on startup via `ModelManager`
- Supports dynamic model switching (DistilBERT ↔ Logistic Regression ↔ Linear SVM)
- Endpoints: `/predict`, `/models`, `/models/switch`

### Streamlit UI
- Lazy loads models on first use
- Caches loaded models in session state
- Supports all 4 models (DistilBERT, Logistic Regression, Linear SVM, Toxicity)

### Training Scripts
- Save models after training completion
- Generate `training_info.json` with metrics
- Create checkpoints during training

---

## Troubleshooting

### Issue: Model Not Found
**Solution**: Verify model directory exists and contains required files (config.json, model.safetensors, tokenizer files).

### Issue: Out of Memory During Loading
**Solution**: Use baseline models (459 KB) instead of transformers (268 MB), or increase system memory.

### Issue: Slow Inference
**Solution**: Enable GPU (`device='cuda'`), use FP16 inference, or switch to baseline models.

### Issue: Incorrect Predictions
**Solution**: Check label mappings in `labels.json`, verify input preprocessing matches training.

### Issue: Checkpoint Loading Fails
**Solution**: Use final model (not checkpoints) for inference. Checkpoints are for training resumption only.

---

## Summary

The `models/` directory provides:
- **3 model families**: Baselines (TF-IDF + ML), Transformer (DistilBERT), Toxicity (multi-label)
- **5 trained models**: 2 baselines, 2 transformer variants, 1 toxicity
- **Production-ready artifacts**: Weights, configs, tokenizers, training metadata
- **Flexible deployment**: Local, Docker, GCP with version control
- **Performance range**: 0.6ms (Linear SVM) to 2.24ms (DistilBERT) inference
- **Accuracy range**: 85-88% (baselines) to 96.69% (fullscale DistilBERT)

All models are integrated with the API server and UI, enabling dynamic model selection based on speed/accuracy requirements.
