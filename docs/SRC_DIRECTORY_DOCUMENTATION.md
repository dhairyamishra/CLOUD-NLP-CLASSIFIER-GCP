# Source Code Directory Documentation

## Overview

The `src/` directory contains all source code for the NLP classification system, organized into 4 main modules: API server, data processing, model training, and user interface.

**Total Structure**:
- **4 main modules**: api, data, models, ui
- **2 UI submodules**: components, utils
- **21 Python files** (excluding __init__.py)
- **~156 KB** of source code

---

## Directory Structure

```
src/
├── __init__.py                      # Package marker
├── api/                             # FastAPI server (2 files, 38 KB)
│   ├── __init__.py
│   ├── server.py                    # Multi-model API server (660 lines)
│   └── README.md                    # API documentation
├── data/                            # Data processing (2 files, 10 KB)
│   ├── __init__.py
│   ├── dataset_utils.py             # Dataset loading utilities
│   └── preprocess.py                # Text preprocessing pipeline
├── models/                          # Model training (6 files, 63 KB)
│   ├── __init__.py
│   ├── baselines.py                 # TF-IDF + classical ML models
│   ├── evaluation.py                # Metrics computation
│   ├── multi_head_model.py          # Multi-label toxicity model
│   ├── train_baselines.py           # Baseline training pipeline
│   ├── train_toxicity.py            # Toxicity model training
│   └── transformer_training.py      # DistilBERT training (650+ lines)
└── ui/                              # Streamlit interface (11 files, 79 KB)
    ├── __init__.py
    ├── streamlit_app.py             # Standalone UI (local models)
    ├── streamlit_app_api.py         # API-connected UI
    ├── components/                  # UI components (3 files)
    │   ├── __init__.py
    │   ├── header.py                # App header and branding
    │   ├── results_display.py       # Prediction results display
    │   └── sidebar.py               # Model selection sidebar
    └── utils/                       # UI utilities (4 files)
        ├── __init__.py
        ├── api_inference.py         # API client for predictions
        ├── helpers.py               # Color/emoji helpers
        ├── inference_handler.py     # Local model inference
        └── model_manager.py         # Model loading and caching
```

---

## PROGRESS CHECKPOINT 1: Structure Complete ✓

---

## Module 1: API (`src/api/`)

### Overview
FastAPI-based REST API server with multi-model support, dynamic model switching, and comprehensive endpoint validation.

### Files

#### `server.py` (660 lines, 32 KB)

**Purpose**: Production-ready FastAPI server with multi-model management.

**Key Classes**:
- `ModelManager` - Manages multiple models (DistilBERT, Logistic Regression, Linear SVM, Toxicity)
- `PredictionRequest` - Pydantic model for prediction input validation
- `PredictionResponse` - Pydantic model for prediction output
- `ModelSwitchRequest` - Model switching request validation

**API Endpoints**:
1. `GET /` - Root endpoint with API info and available models
2. `GET /health` - Health check with model status and metadata
3. `POST /predict` - Text classification with current model
4. `GET /models` - List all available models with details
5. `POST /models/switch` - Switch active model without restart
6. `GET /docs` - Swagger UI documentation
7. `GET /redoc` - ReDoc alternative documentation

**Model Management Features**:
- Dynamic model loading on startup
- Zero-downtime model switching
- Model type detection (transformer vs baseline vs toxicity)
- Label mapping for all model types
- Inference time measurement
- Comprehensive error handling

**Supported Models**:
- **DistilBERT**: `models/transformer/distilbert/` (transformer)
- **Logistic Regression**: `models/baselines/logistic_regression_tfidf.joblib` (baseline)
- **Linear SVM**: `models/baselines/linear_svm_tfidf.joblib` (baseline)
- **Toxicity**: `models/toxicity_multi_head/` (multi-label)

**Key Functions**:
- `_load_transformer_model()` - Load HuggingFace transformer
- `_load_baseline_model()` - Load joblib baseline model
- `_load_toxicity_model()` - Load multi-head toxicity model
- `_predict_transformer()` - Transformer inference
- `_predict_baseline()` - Baseline inference
- `_predict_toxicity()` - Multi-label toxicity inference
- `switch_model()` - Dynamic model switching

**Configuration**:
- CORS enabled for cross-origin requests
- Lifespan events for model loading
- Pydantic V2 compliant
- Environment variable `DEFAULT_MODEL` for startup model

**Usage**:
```python
# Start server
uvicorn src.api.server:app --host 0.0.0.0 --port 8000

# Make prediction
import requests
response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "Sample text"}
)
```

---

#### `README.md` (5.8 KB)

**Purpose**: API documentation with endpoint details, examples, and deployment instructions.

**Contents**:
- Endpoint specifications
- Request/response schemas
- cURL examples
- Python client examples
- Error handling guide
- Deployment instructions

---

## PROGRESS CHECKPOINT 2: API Module Complete ✓

---

## Module 2: Data (`src/data/`)

### Overview
Data loading, preprocessing, and train/val/test splitting utilities.

### Files

#### `dataset_utils.py` (4.5 KB)

**Purpose**: Dataset loading and splitting utilities.

**Key Functions**:

1. `load_raw_dataset(filepath: str) -> pd.DataFrame`
   - Load raw CSV dataset
   - Validate required columns (text, label)
   - Return pandas DataFrame

2. `train_val_test_split(df: pd.DataFrame, train_size=0.7, val_size=0.15, test_size=0.15, random_state=42)`
   - Stratified split into train/val/test
   - Maintains label distribution
   - Returns 3 DataFrames

3. `save_splits(train_df, val_df, test_df, output_dir="data/processed")`
   - Save splits to CSV files
   - Create output directory if needed
   - Log split statistics

4. `load_split(split_name: str, data_dir="data/processed") -> pd.DataFrame`
   - Load specific split (train/val/test)
   - Validate file exists
   - Return DataFrame

**Features**:
- Stratified splitting for balanced datasets
- Automatic directory creation
- Split statistics logging
- Error handling for missing files

**Usage**:
```python
from src.data.dataset_utils import load_raw_dataset, train_val_test_split

# Load and split
df = load_raw_dataset("data/raw/dataset.csv")
train, val, test = train_val_test_split(df)
```

---

#### `preprocess.py` (5.3 KB)

**Purpose**: Text preprocessing pipeline for cleaning and normalizing text data.

**Key Functions**:

1. `clean_text(text: str) -> str`
   - Remove URLs (http://, https://, www.)
   - Remove mentions (@username)
   - Remove hashtags (#hashtag)
   - Remove special characters (keep alphanumeric and spaces)
   - Convert to lowercase
   - Normalize whitespace
   - Strip leading/trailing spaces

2. `preprocess_dataframe(df: pd.DataFrame, text_column="text") -> pd.DataFrame`
   - Apply clean_text to all rows
   - Handle missing values
   - Remove empty texts after cleaning
   - Return cleaned DataFrame

3. `main()`
   - Load raw dataset
   - Apply preprocessing
   - Create train/val/test splits
   - Save processed splits
   - Log statistics

**Preprocessing Steps**:
1. URL removal
2. Mention removal
3. Hashtag removal
4. Special character removal
5. Lowercase conversion
6. Whitespace normalization

**Usage**:
```python
from src.data.preprocess import clean_text

text = "Check this out http://example.com @user #hashtag"
cleaned = clean_text(text)
# Result: "check this out"
```

**CLI Usage**:
```bash
python -m src.data.preprocess
```

---

## PROGRESS CHECKPOINT 3: Data Module Complete ✓

---

## Module 3: Models (`src/models/`)

### Overview
Model training, evaluation, and inference for baselines, transformers, and toxicity detection.

### Files

#### `baselines.py` (9.5 KB)

**Purpose**: TF-IDF + classical ML baseline models (Logistic Regression, Linear SVM).

**Key Class**: `BaselineTextClassifier`

**Methods**:
- `__init__(vectorizer_type="tfidf", classifier_type="logistic_regression", **kwargs)`
- `fit(X_train, y_train)` - Train vectorizer and classifier
- `predict(X)` - Predict class labels
- `predict_proba(X)` - Predict class probabilities
- `save(filepath)` - Save model to joblib file
- `load(filepath)` - Load model from joblib file (class method)

**Supported Vectorizers**:
- TF-IDF (default)
- Count Vectorizer

**Supported Classifiers**:
- Logistic Regression (default)
- Linear SVM
- Random Forest
- Naive Bayes

**Configuration Options**:
- `max_features` - Maximum vocabulary size
- `ngram_range` - N-gram range (default: (1, 2))
- `C` - Regularization strength (Logistic Regression/SVM)
- `max_iter` - Maximum iterations
- `class_weight` - Class balancing

**Usage**:
```python
from src.models.baselines import BaselineTextClassifier

# Train
model = BaselineTextClassifier(
    vectorizer_type="tfidf",
    classifier_type="logistic_regression",
    max_features=10000,
    C=1.0
)
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)

# Save/Load
model.save("models/baselines/model.joblib")
loaded_model = BaselineTextClassifier.load("models/baselines/model.joblib")
```

---

#### `evaluation.py` (6 KB)

**Purpose**: Comprehensive evaluation metrics for classification models.

**Key Function**: `compute_classification_metrics(y_true, y_pred, y_pred_proba=None, labels=None)`

**Metrics Computed**:
- **Accuracy**: Overall correctness
- **Precision**: Macro and weighted averages
- **Recall**: Macro and weighted averages
- **F1 Score**: Macro and weighted averages
- **ROC-AUC**: Binary or multi-class (OvR/OvO)
- **Confusion Matrix**: Full confusion matrix
- **Classification Report**: Per-class metrics

**Return Format**:
```python
{
    "accuracy": 0.95,
    "precision_macro": 0.94,
    "precision_weighted": 0.95,
    "recall_macro": 0.93,
    "recall_weighted": 0.95,
    "f1_macro": 0.93,
    "f1_weighted": 0.95,
    "roc_auc": 0.96,  # or roc_auc_ovr/roc_auc_ovo
    "confusion_matrix": [[...], [...]],
    "classification_report": "..."
}
```

**Features**:
- Handles binary and multi-class classification
- Automatic ROC-AUC calculation (binary/OvR/OvO)
- Comprehensive error handling
- Pretty-printed classification report

**Usage**:
```python
from src.models.evaluation import compute_classification_metrics

metrics = compute_classification_metrics(
    y_true=y_test,
    y_pred=predictions,
    y_pred_proba=probabilities,
    labels=["class_0", "class_1"]
)
print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1 Macro: {metrics['f1_macro']:.4f}")
```

---

#### `train_baselines.py` (9.1 KB)

**Purpose**: Complete training pipeline for baseline models.

**Main Function**: `main()`

**Pipeline Steps**:
1. Load configuration from `config/config_baselines.yaml`
2. Load preprocessed train/val/test splits
3. Train Logistic Regression model
4. Train Linear SVM model
5. Evaluate both models on test set
6. Save models to `models/baselines/`
7. Log metrics and training info

**Configuration**:
```yaml
vectorizer:
  type: "tfidf"
  max_features: 10000
  ngram_range: [1, 2]

logistic_regression:
  C: 1.0
  max_iter: 1000
  class_weight: "balanced"

linear_svm:
  C: 1.0
  max_iter: 1000
  class_weight: "balanced"
```

**Output Files**:
- `models/baselines/logistic_regression_tfidf.joblib`
- `models/baselines/linear_svm_tfidf.joblib`

**Logged Metrics**:
- Accuracy, Precision, Recall, F1 (macro/weighted)
- Training time
- Model size
- Confusion matrix

**Usage**:
```bash
python -m src.models.train_baselines
# or
python run_baselines.py
```

---

## PROGRESS CHECKPOINT 4: Models Module (Part 1) Complete ✓

---

#### `multi_head_model.py` (5.5 KB)

**Purpose**: Multi-label toxicity classification model with separate heads for each toxicity type.

**Key Class**: `MultiHeadToxicityModel(nn.Module)`

**Architecture**:
- Base: DistilBERT encoder
- 6 classification heads (one per toxicity type):
  - toxic
  - severe_toxic
  - obscene
  - threat
  - insult
  - identity_hate

**Methods**:
- `__init__(model_name, num_labels_per_head, dropout=0.1)`
- `forward(input_ids, attention_mask)` - Forward pass
- Returns: Dict with logits for each head

**Features**:
- Shared DistilBERT encoder
- Independent binary classifiers for each toxicity type
- Dropout for regularization
- Supports multi-label predictions

**Usage**:
```python
from src.models.multi_head_model import MultiHeadToxicityModel

model = MultiHeadToxicityModel(
    model_name="distilbert-base-uncased",
    num_labels_per_head=2,  # binary for each head
    dropout=0.1
)

outputs = model(input_ids, attention_mask)
# outputs = {
#     "toxic": tensor([[...]]),
#     "severe_toxic": tensor([[...]]),
#     ...
# }
```

---

#### `train_toxicity.py` (10.6 KB)

**Purpose**: Training pipeline for multi-label toxicity detection model.

**Main Function**: `main()`

**Pipeline Steps**:
1. Load configuration from `config/config_toxicity.yaml`
2. Load toxicity dataset (train/test)
3. Initialize MultiHeadToxicityModel
4. Create custom dataset and dataloaders
5. Train with multi-label BCE loss
6. Evaluate on test set
7. Save model and tokenizer
8. Log metrics for each toxicity type

**Toxicity Labels** (6 types):
- toxic
- severe_toxic
- obscene
- threat
- insult
- identity_hate

**Training Features**:
- Multi-label binary cross-entropy loss
- Per-head loss calculation
- Weighted loss for imbalanced labels
- Early stopping support
- Learning rate scheduling
- Mixed precision (FP16) support

**Configuration**:
```yaml
model:
  name: "distilbert-base-uncased"
  dropout: 0.1

training:
  train_batch_size: 16
  eval_batch_size: 32
  learning_rate: 2.0e-5
  num_train_epochs: 3
  warmup_steps: 500
```

**Output Files**:
- `models/toxicity_multi_head/config.json`
- `models/toxicity_multi_head/pytorch_model.bin`
- `models/toxicity_multi_head/tokenizer_config.json`
- `models/toxicity_multi_head/labels.json`
- `models/toxicity_multi_head/training_info.json`

**Usage**:
```bash
python -m src.models.train_toxicity
# or
.\scripts\run_toxicity_training.ps1
```

---

#### `transformer_training.py` (22 KB, 650+ lines)

**Purpose**: Advanced DistilBERT training pipeline with CLI interface and cloud support.

**Main Function**: `main()`

**Key Features**:

**1. CLI Interface** (argparse):
- `--config` - Config file path
- `--mode` - Training mode (local/cloud)
- `--output-dir` - Override output directory
- `--epochs` - Override number of epochs
- `--batch-size` - Override batch size
- `--learning-rate` - Override learning rate
- `--fp16` - Enable mixed precision
- `--no-early-stopping` - Disable early stopping
- `--seed` - Random seed

**2. Configuration Management**:
- Load from YAML config
- CLI overrides for all parameters
- Local vs cloud config support
- Validation and defaults

**3. Training Optimizations**:
- Early stopping (configurable patience)
- Learning rate schedulers:
  - linear
  - cosine
  - cosine_with_restarts
  - polynomial
  - constant
  - constant_with_warmup
- Mixed precision (FP16) with GPU detection
- Gradient accumulation
- Warmup steps
- DataLoader optimizations

**4. Model Training**:
- DistilBERT fine-tuning
- HuggingFace Trainer API
- Automatic best model selection
- Comprehensive logging

**5. Evaluation**:
- Accuracy, F1, Precision, Recall
- ROC-AUC
- Inference time measurement
- Per-class metrics

**6. Output Artifacts**:
- Model weights (pytorch_model.bin or model.safetensors)
- Tokenizer files
- Config files
- Label mappings (labels.json)
- Training info (training_info.json)

**Configuration Example**:
```yaml
model:
  name: "distilbert-base-uncased"
  max_seq_length: 128

training:
  train_batch_size: 32
  eval_batch_size: 64
  learning_rate: 2.0e-5
  num_train_epochs: 3
  
  lr_scheduler:
    type: "linear"
    warmup_ratio: 0.1
  
  early_stopping:
    enabled: true
    patience: 3
    metric: "f1"
  
  fp16:
    enabled: false
```

**Usage**:
```bash
# Basic training
python -m src.models.transformer_training

# Cloud training with FP16
python -m src.models.transformer_training \
  --config config/config_transformer_cloud.yaml \
  --mode cloud \
  --fp16

# Custom parameters
python -m src.models.transformer_training \
  --epochs 5 \
  --batch-size 32 \
  --learning-rate 3e-5 \
  --output-dir models/transformer/custom
```

---

## PROGRESS CHECKPOINT 5: Models Module Complete ✓

---

## Module 4: UI (`src/ui/`)

### Overview
Streamlit-based user interface with two modes: standalone (local models) and API-connected.

### Main Files

#### `streamlit_app.py` (6.3 KB)

**Purpose**: Standalone Streamlit UI with local model loading.

**Features**:
- Direct model loading (no API required)
- Model selection (DistilBERT, Logistic Regression, Linear SVM)
- Real-time text classification
- Confidence scores and probability charts
- Model performance comparison
- Caching for fast inference

**Components Used**:
- `header.py` - App branding
- `sidebar.py` - Model selection
- `results_display.py` - Results visualization
- `inference_handler.py` - Local inference
- `model_manager.py` - Model caching

**Usage**:
```bash
streamlit run src/ui/streamlit_app.py
# Access at http://localhost:8501
```

---

#### `streamlit_app_api.py` (11.8 KB)

**Purpose**: API-connected Streamlit UI for remote inference.

**Features**:
- Connects to FastAPI server
- Model switching via API
- Real-time predictions
- API health monitoring
- Error handling for API failures
- Supports all API models (including Toxicity)

**API Endpoints Used**:
- `GET /health` - Check API status
- `GET /models` - List available models
- `POST /models/switch` - Switch active model
- `POST /predict` - Get predictions

**Components Used**:
- `header.py` - App branding
- `sidebar.py` - Model selection
- `results_display.py` - Results visualization
- `api_inference.py` - API client

**Configuration**:
```python
API_URL = "http://localhost:8000"  # or remote URL
```

**Usage**:
```bash
# Start API first
uvicorn src.api.server:app --port 8000

# Start UI
streamlit run src/ui/streamlit_app_api.py
# Access at http://localhost:8501
```

---

## PROGRESS CHECKPOINT 6: UI Main Files Complete ✓

---

### UI Components (`src/ui/components/`)

#### `header.py` (2.5 KB)

**Purpose**: App header with branding and information.

**Function**: `render_header()`

**Features**:
- App title and description
- Project information
- Model information
- Usage instructions
- Styled with Streamlit markdown

**Usage**:
```python
from src.ui.components.header import render_header
render_header()
```

---

#### `results_display.py` (17 KB)

**Purpose**: Comprehensive results visualization with charts and metrics.

**Functions**:

1. `display_prediction_results(prediction_data, model_name=None)`
   - Main results display
   - Prediction label with confidence
   - Color-coded results (green/red)
   - Emoji indicators
   - Probability chart
   - DistilBERT label mapping (0/1 → Regular/Hate Speech)

2. `create_probability_chart(scores, model_name=None)`
   - Horizontal bar chart
   - Color-coded by label type
   - Percentage display
   - DistilBERT-aware labeling

3. `display_model_info(model_info)`
   - Model metadata display
   - Performance metrics
   - Model type and path

**Special Features**:
- DistilBERT label mapping (fixes numeric labels)
- Color coding: Green (safe), Red (toxic/hate)
- Emoji indicators: ✅ (safe), ⚠️ (toxic/hate)
- Responsive charts with Plotly

**Usage**:
```python
from src.ui.components.results_display import display_prediction_results

prediction_data = {
    "predicted_label": "Hate Speech",
    "confidence": 0.95,
    "scores": [
        {"label": "Regular Speech", "score": 0.05},
        {"label": "Hate Speech", "score": 0.95}
    ]
}
display_prediction_results(prediction_data, model_name="distilbert")
```

---

#### `sidebar.py` (4.9 KB)

**Purpose**: Sidebar with model selection and configuration.

**Functions**:

1. `render_sidebar(available_models, current_model=None)`
   - Model selection dropdown
   - Model information display
   - Configuration options
   - About section

2. `get_model_description(model_name)`
   - Returns model description
   - Performance characteristics
   - Use case recommendations

**Model Descriptions**:
- **DistilBERT**: Best accuracy (90-93%), slower (45-60ms)
- **Logistic Regression**: Balanced (85-88%), fast (3-7ms)
- **Linear SVM**: Fast (85-88%), ultra-fast (3-7ms)
- **Toxicity**: Multi-label toxicity detection

**Usage**:
```python
from src.ui.components.sidebar import render_sidebar

models = ["distilbert", "logistic_regression", "linear_svm"]
selected = render_sidebar(models, current_model="distilbert")
```

---

## PROGRESS CHECKPOINT 7: UI Components Complete ✓

---

### UI Utilities (`src/ui/utils/`)

#### `api_inference.py` (8.7 KB)

**Purpose**: API client for remote inference.

**Key Functions**:

1. `check_api_health(api_url)`
   - Check if API is running
   - Get current model info
   - Return health status

2. `get_available_models(api_url)`
   - Fetch list of available models
   - Return model details

3. `switch_model(api_url, model_name)`
   - Request model switch
   - Handle errors
   - Return success status

4. `predict_text(api_url, text)`
   - Send prediction request
   - Parse response
   - Handle errors

**Error Handling**:
- Connection errors
- Timeout errors
- API errors (4xx, 5xx)
- Validation errors

**Usage**:
```python
from src.ui.utils.api_inference import predict_text

result = predict_text(
    api_url="http://localhost:8000",
    text="Sample text"
)
```

---

#### `helpers.py` (4.6 KB)

**Purpose**: Helper functions for colors, emojis, and formatting.

**Key Functions**:

1. `get_label_color(label)`
   - Return color for label
   - Green for safe/regular
   - Red for toxic/hate
   - Gray for neutral

2. `get_label_emoji(label)`
   - Return emoji for label
   - ✅ for safe/regular
   - ⚠️ for toxic/hate
   - ℹ️ for neutral

3. `format_confidence(confidence)`
   - Format confidence as percentage
   - Color-coded by confidence level

4. `format_inference_time(time_ms)`
   - Format inference time
   - Human-readable units

**Label Mappings**:
- Safe labels: "regular", "normal", "safe", "non-toxic"
- Toxic labels: "hate", "toxic", "offensive", "threat", "insult"

**Usage**:
```python
from src.ui.utils.helpers import get_label_color, get_label_emoji

color = get_label_color("Hate Speech")  # Returns "#DC3545" (red)
emoji = get_label_emoji("Hate Speech")  # Returns "⚠️"
```

---

#### `inference_handler.py` (11.7 KB)

**Purpose**: Local model inference without API.

**Key Class**: `InferenceHandler`

**Methods**:
- `__init__(model_path, model_type)`
- `load_model()` - Load model from disk
- `predict(text)` - Make prediction
- `predict_batch(texts)` - Batch predictions

**Supported Model Types**:
- `transformer` - DistilBERT models
- `baseline` - Joblib models (LogReg, SVM)
- `toxicity` - Multi-head toxicity models

**Features**:
- Automatic model type detection
- Label mapping
- Confidence scores
- Inference time measurement
- Error handling

**Usage**:
```python
from src.ui.utils.inference_handler import InferenceHandler

handler = InferenceHandler(
    model_path="models/transformer/distilbert",
    model_type="transformer"
)
result = handler.predict("Sample text")
```

---

#### `model_manager.py` (12.2 KB)

**Purpose**: Model loading and caching for UI.

**Key Class**: `ModelManager`

**Methods**:
- `__init__()`
- `load_model(model_name, model_path, model_type)` - Load and cache
- `get_model(model_name)` - Get cached model
- `unload_model(model_name)` - Remove from cache
- `list_models()` - List cached models
- `clear_cache()` - Clear all cached models

**Features**:
- LRU caching with size limits
- Memory management
- Lazy loading
- Model metadata tracking
- Thread-safe operations

**Cache Configuration**:
- Max models: 3
- Max memory: 2 GB
- Eviction policy: LRU

**Usage**:
```python
from src.ui.utils.model_manager import ModelManager

manager = ModelManager()
model = manager.load_model(
    model_name="distilbert",
    model_path="models/transformer/distilbert",
    model_type="transformer"
)
```

---

## PROGRESS CHECKPOINT 8: UI Utils Complete ✓

---

## Summary

### Module Statistics

| Module | Files | Lines | Size | Purpose |
|--------|-------|-------|------|---------|
| **api** | 2 | ~660 | 38 KB | FastAPI server with multi-model support |
| **data** | 2 | ~300 | 10 KB | Data loading and preprocessing |
| **models** | 6 | ~2000 | 63 KB | Model training and evaluation |
| **ui** | 11 | ~2000 | 79 KB | Streamlit interface (standalone + API) |
| **Total** | 21 | ~5000 | 190 KB | Complete NLP classification system |

### Key Features by Module

**API Module**:
- Multi-model REST API
- Dynamic model switching
- 4 model types supported
- Comprehensive validation
- Production-ready

**Data Module**:
- Text preprocessing
- Dataset splitting
- Stratified sampling
- Clean pipeline

**Models Module**:
- Baseline models (TF-IDF + ML)
- Transformer training (DistilBERT)
- Toxicity detection (multi-label)
- Advanced training features
- Comprehensive evaluation

**UI Module**:
- Two deployment modes
- Real-time predictions
- Interactive visualizations
- Model comparison
- API integration

### Integration Points

1. **Data → Models**: Preprocessed data feeds training pipelines
2. **Models → API**: Trained models loaded by API server
3. **API → UI**: UI connects to API for predictions
4. **Models → UI**: Standalone UI loads models directly

### Technology Stack

- **API**: FastAPI, Pydantic, Uvicorn
- **Data**: Pandas, scikit-learn
- **Models**: PyTorch, Transformers, scikit-learn
- **UI**: Streamlit, Plotly
- **Common**: NumPy, YAML, JSON

---

## FINAL CHECKPOINT: Documentation Complete ✓

All 21 source files documented across 4 main modules and 2 submodules.
