# Tests Directory Documentation

## Overview

The `tests/` directory contains 10 test files (9 Python, 1 PowerShell) that validate all aspects of the ML pipeline from basic imports to API endpoints, model loading, inference, and advanced training features.

**Purpose**: Ensure code quality, validate model performance, verify API functionality, and confirm proper implementation of training features.

---

## Directory Structure

```
tests/
├── __init__.py                      # Python package marker (empty)
├── test_basic_imports.py            # Import validation and package structure
├── test_api.py                      # FastAPI endpoint testing with TestClient
├── test_baseline_inference.py       # Baseline model loading and predictions
├── test_model_loading.py            # Transformer model loading validation
├── test_inference.py                # Transformer inference and speed tests
├── test_metrics.py                  # Training metrics validation
├── test_advanced_training.py        # Phase 10 advanced features testing
├── verify_phase10.py                # Phase 10 feature verification
└── test_docker_api.ps1              # Docker API endpoint testing (PowerShell)
```

---

## Test Files

### 1. `test_basic_imports.py`

**Purpose**: Validate that all core modules can be imported and have expected attributes.

**Tests**:
- Data utilities import (`dataset_utils`, `preprocess`)
- Text cleaning functionality (URL removal, lowercase, whitespace)
- Config module existence
- Baseline classifier import
- Evaluation metrics import
- FastAPI app import and routes

**Key Functions**:
- `test_import_data_utils()` - Validates data processing modules
- `test_clean_text_function()` - Tests text preprocessing
- `test_import_config()` - Verifies config module
- `test_import_baseline_classifier()` - Checks baseline model class
- `test_import_evaluation_metrics()` - Validates metrics module
- `test_import_fastapi_app()` - Confirms API app structure

**Usage**:
```bash
pytest tests/test_basic_imports.py -v
```

**Expected Result**: 6 tests pass with zero import errors or warnings.

---

### 2. `test_api.py`

**Purpose**: Comprehensive FastAPI endpoint testing using TestClient.

**Tests** (11 total):
1. Root endpoint (`/`) - API info and status
2. Health check (`/health`) - Model status and metadata
3. Valid text prediction - Standard classification
4. Empty text validation - Should return 422 error
5. Whitespace-only validation - Should return 422 error
6. Missing text field - Should return 422 error
7. Long text handling - 100+ word texts
8. Special characters - Emojis and symbols
9. Multiple consecutive requests - Stress testing
10. OpenAPI schema availability - `/openapi.json`
11. Documentation endpoints - `/docs` and `/redoc`

**Key Features**:
- Uses FastAPI `TestClient` for isolated testing
- Skips tests if model not loaded (graceful degradation)
- Validates response structure and data types
- Checks confidence scores are in [0, 1] range
- Verifies inference time is positive

**Usage**:
```bash
pytest tests/test_api.py -v
```

**Expected Result**: 11 tests pass (or skip if model not loaded).

---

### 3. `test_baseline_inference.py`

**Purpose**: Verify baseline models (Logistic Regression, Linear SVM) can load and make predictions.

**What It Tests**:
- Model loading from joblib files
- Prediction generation for sample texts
- Probability estimation
- Confidence scores

**Test Samples**:
- Positive text: "I love this product, it's amazing!"
- Hate speech: "You are a stupid idiot and I hate you"
- Neutral text: "The weather is nice today"
- Severe hate: "Go kill yourself you worthless piece of trash"

**Models Tested**:
- `models/baselines/logistic_regression_tfidf.joblib`
- `models/baselines/linear_svm_tfidf.joblib`

**Usage**:
```bash
python tests/test_baseline_inference.py
```

**Output**: Displays predictions with confidence scores for each model.

---

### 4. `test_model_loading.py`

**Purpose**: Validate transformer model (DistilBERT) loads correctly after training.

**Validation Steps**:
1. Check model directory exists
2. Load tokenizer from saved files
3. Load model architecture and weights
4. Verify parameter count (66M parameters)
5. Load label mappings (id2label, label2id)
6. Test inference on sample text
7. Verify output shape matches num_classes
8. Check training_info.json exists
9. Display training metrics (accuracy, F1, training time)

**Expected Checks**:
- Model directory: `models/transformer/distilbert/`
- Files: tokenizer, model, labels.json, training_info.json
- Output shape: (1, num_classes)

**Usage**:
```bash
python tests/test_model_loading.py
```

**Exit Code**: 0 if all checks pass, 1 if any fail.

---

### 5. `test_inference.py`

**Purpose**: Test transformer inference functionality and measure performance.

**What It Tests**:
- Model and tokenizer loading
- Label mapping loading
- Inference on diverse text samples
- Softmax probability calculation
- Confidence score extraction
- Inference speed measurement (100 runs)

**Test Samples** (5 texts):
- Positive: "I love this product, it's amazing and works perfectly!"
- Negative: "This is terrible, worst experience ever. Very disappointed."
- Neutral: "It's okay, nothing special. Average quality."
- Very positive: "Absolutely fantastic! Highly recommend to everyone."
- Very negative: "Horrible service, would not recommend to anyone."

**Performance Metrics**:
- Average inference time (ms/sample)
- Measured over 100 runs for accuracy

**Usage**:
```bash
python tests/test_inference.py
```

**Output**: Predictions with confidence scores and speed benchmark.

---

### 6. `test_metrics.py`

**Purpose**: Validate training metrics are reasonable and within expected ranges.

**Validation Checks**:
1. Metrics in valid range [0, 1]
2. Training time is positive
3. Inference time is positive
4. Number of classes matches class list
5. Accuracy > 50% (reasonable performance)

**Metrics Validated**:
- Accuracy
- F1 Macro
- F1 Weighted
- Precision Macro
- Recall Macro
- ROC-AUC (if available)
- Training time (seconds/minutes)
- Average inference time (ms)

**Performance Assessment**:
- **Excellent**: Accuracy ≥ 90%, F1 ≥ 85%
- **Good**: Accuracy ≥ 85%, F1 ≥ 75%
- **Fair**: Accuracy ≥ 75%, F1 ≥ 65%
- **Poor**: Accuracy ≥ 60%, F1 ≥ 50%
- **Very Poor**: Below thresholds

**Usage**:
```bash
python tests/test_metrics.py
```

**Exit Code**: 0 if all validation checks pass, 1 if any fail.

---

### 7. `test_advanced_training.py`

**Purpose**: Test Phase 10 advanced training features with minimal training (1 epoch each).

**Tests** (6 total):
1. **Basic CLI Training** - CLI argument parsing, default settings
2. **FP16 Mixed Precision** - GPU detection, automatic FP32 fallback
3. **Cosine LR Scheduler** - Learning rate scheduler configuration
4. **Cloud Config Local Mode** - Cloud settings running locally
5. **Custom Hyperparameters** - CLI overrides for all parameters
6. **No Early Stopping** - Early stopping disable flag

**Features Tested**:
- CLI interface (`--epochs`, `--batch-size`, `--learning-rate`, `--fp16`)
- Configuration file loading
- LR scheduler types (linear, cosine, etc.)
- Mode switching (local/cloud)
- Output directory customization
- Early stopping toggle

**Duration**: 5-15 minutes per test (30-90 minutes total)

**Usage**:
```bash
python tests/test_advanced_training.py
```

**Note**: Interactive - prompts before each test. Requires preprocessed data.

---

### 8. `verify_phase10.py`

**Purpose**: Verify Phase 10 advanced training features are properly installed BEFORE training.

**Verification Checks**:

**Check 1: Training Script Features**
- CLI argument parsing (argparse)
- Cloud training mode support
- Configuration overrides
- Advanced LR schedulers
- FP16 validation
- Enhanced logging
- Warmup steps support
- DataLoader optimizations

**Check 2: Configuration Files**
- `config/config_transformer.yaml` (local)
- `config/config_transformer_cloud.yaml` (cloud)

**Check 3: Cloud Training Scripts**
- `scripts/setup_gcp_training.sh`
- `scripts/run_gcp_training.sh`
- `scripts/run_transformer_cloud.ps1`

**Check 4: Documentation**
- `docs/PHASE10_ADVANCED_TRAINING_SUMMARY.md`
- `docs/TESTING_ADVANCED_TRAINING.md`

**Check 5: Test Scripts**
- `quick_test_training.py`
- `test_advanced_training.py`

**Usage**:
```bash
python tests/verify_phase10.py
```

**Output**: Detailed checklist of Phase 10 features with pass/fail status.

**Exit Code**: 0 if all critical checks pass, 1 if any fail.

---

### 9. `test_docker_api.ps1`

**Purpose**: Test containerized API endpoints using PowerShell.

**Tests** (5 total):
1. **Health Check** - `GET /health`
2. **Root Endpoint** - `GET /`
3. **Positive Text Prediction** - "I love this product!"
4. **Negative Text Prediction** - "This is terrible and offensive"
5. **Neutral Text Prediction** - "The weather today is cloudy"

**Features**:
- Uses `Invoke-RestMethod` for HTTP requests
- JSON request/response handling
- Colored output (Green = pass, Red = fail)
- Displays full response for debugging

**Prerequisites**: Docker container running on `localhost:8000`

**Usage**:
```powershell
.\tests\test_docker_api.ps1
```

**Expected Result**: All 5 tests pass with JSON responses displayed.

---

## Test Categories

### Unit Tests
- `test_basic_imports.py` - Module imports
- `test_baseline_inference.py` - Baseline models
- `test_model_loading.py` - Transformer loading

### Integration Tests
- `test_api.py` - API endpoints
- `test_inference.py` - End-to-end inference
- `test_docker_api.ps1` - Dockerized API

### Validation Tests
- `test_metrics.py` - Training metrics
- `verify_phase10.py` - Feature verification

### System Tests
- `test_advanced_training.py` - Full training pipeline

---

## Running Tests

### Run All Tests
```bash
# Using pytest
pytest tests/ -v

# Using root-level runner
python run_tests.py
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
```

### Run Specific Test Function
```bash
pytest tests/test_api.py::test_health_endpoint -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Docker Tests
```powershell
.\tests\test_docker_api.ps1
```

### Run Training Tests
```bash
python tests/test_advanced_training.py
```

---

## Test Requirements

### Prerequisites
1. **Virtual environment activated**
2. **Dependencies installed** (`pip install -r requirements.txt`)
3. **Data preprocessed** (`python run_preprocess.py`)
4. **Models trained** (for inference tests):
   - Baselines: `python run_baselines.py`
   - Transformer: `python run_transformer.py`

### Optional (for specific tests)
- **Docker running** (for `test_docker_api.ps1`)
- **API server running** (for manual API tests)
- **GPU available** (for FP16 tests)

---

## Test Coverage

### Modules Tested
- `src.data` - Data processing and preprocessing
- `src.models` - Model training and inference
- `src.api` - FastAPI server and endpoints
- `config` - Configuration loading

### Features Tested
- Import validation
- Text cleaning
- Model loading (baseline + transformer)
- Inference (predictions + probabilities)
- API endpoints (health, predict, docs)
- Input validation (empty, whitespace, special chars)
- Performance metrics
- Training features (CLI, schedulers, FP16)

---

## Expected Test Results

### Successful Run
```
tests/test_basic_imports.py::test_import_data_utils PASSED
tests/test_basic_imports.py::test_clean_text_function PASSED
tests/test_basic_imports.py::test_import_config PASSED
tests/test_basic_imports.py::test_import_baseline_classifier PASSED
tests/test_basic_imports.py::test_import_evaluation_metrics PASSED
tests/test_basic_imports.py::test_import_fastapi_app PASSED

tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_predict_endpoint_valid_text PASSED
tests/test_api.py::test_predict_endpoint_empty_text PASSED
tests/test_api.py::test_predict_endpoint_whitespace_only PASSED
tests/test_api.py::test_predict_endpoint_missing_text PASSED
tests/test_api.py::test_predict_endpoint_long_text PASSED
tests/test_api.py::test_predict_endpoint_special_characters PASSED
tests/test_api.py::test_predict_endpoint_multiple_requests PASSED
tests/test_api.py::test_openapi_schema PASSED
tests/test_api.py::test_docs_endpoint PASSED
tests/test_api.py::test_redoc_endpoint PASSED

======================== 18 passed in 2.34s ========================
```

### With Model Not Loaded
```
tests/test_api.py::test_predict_endpoint_valid_text SKIPPED (Model not loaded)
tests/test_api.py::test_predict_endpoint_long_text SKIPPED (Model not loaded)
tests/test_api.py::test_predict_endpoint_special_characters SKIPPED (Model not loaded)
tests/test_api.py::test_predict_endpoint_multiple_requests SKIPPED (Model not loaded)
```

---

## Troubleshooting

### Issue: Import Errors
**Solution**: Ensure virtual environment is activated and dependencies installed.
```bash
pip install -r requirements.txt
```

### Issue: Model Not Found
**Solution**: Train models before running inference tests.
```bash
python run_baselines.py
python run_transformer.py
```

### Issue: API Tests Fail
**Solution**: Check if API server is running (for manual tests) or model is loaded.
```bash
# Start API
python -m uvicorn src.api.server:app --reload
```

### Issue: Docker Tests Fail
**Solution**: Ensure Docker container is running.
```bash
docker ps  # Check if nlp-api is running
docker start nlp-api  # Start if stopped
```

### Issue: Test Skipped
**Reason**: Model not loaded - this is expected behavior for graceful degradation.
**Action**: Train model or ignore skipped tests.

---

## Test Maintenance

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures and assertions
4. Add docstrings explaining test purpose
5. Update this documentation

### Test Best Practices
- **Isolation**: Tests should not depend on each other
- **Cleanup**: Clean up resources after tests
- **Mocking**: Mock external dependencies when possible
- **Assertions**: Use clear, descriptive assertions
- **Documentation**: Add docstrings to all test functions

---

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    pytest tests/ -v --cov=src --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Pre-commit Hook
```bash
#!/bin/bash
pytest tests/test_basic_imports.py -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Summary

The `tests/` directory provides:
- **10 test files** covering all pipeline components
- **18+ unit tests** for imports and basic functionality
- **11 API endpoint tests** with validation
- **6 advanced training tests** for Phase 10 features
- **Verification scripts** for feature confirmation
- **Docker testing** via PowerShell script
- **Performance benchmarking** for inference speed
- **Metrics validation** for training quality

**Test Coverage**:
- Data processing
- Model training
- Model inference
- API endpoints
- Docker deployment
- Advanced features

**Expected Pass Rate**: 100% when models are trained and environment is properly configured.

All tests integrate with pytest and can be run individually or as a suite via `python run_tests.py`.
