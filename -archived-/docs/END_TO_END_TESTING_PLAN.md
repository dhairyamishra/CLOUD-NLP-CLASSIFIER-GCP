# 🚀 End-to-End Testing Plan - CLOUD-NLP-CLASSIFIER-GCP

**Version:** 1.0  
**Date:** December 9, 2025  
**Purpose:** Complete validation of the entire ML pipeline from data download to production Docker deployment

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Testing Phases](#testing-phases)
4. [Phase 1: Environment Setup](#phase-1-environment-setup)
5. [Phase 2: Data Pipeline](#phase-2-data-pipeline)
6. [Phase 3: Baseline Models](#phase-3-baseline-models)
7. [Phase 4: Transformer Training](#phase-4-transformer-training)
8. [Phase 5: API Testing (Local)](#phase-5-api-testing-local)
9. [Phase 6: Unit & Integration Tests](#phase-6-unit--integration-tests)
10. [Phase 7: Docker Build & Test](#phase-7-docker-build--test)
11. [Phase 8: Multi-Model Testing](#phase-8-multi-model-testing)
12. [Phase 9: Performance Validation](#phase-9-performance-validation)
13. [Phase 10: Cleanup & Verification](#phase-10-cleanup--verification)
14. [Success Criteria](#success-criteria)
15. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This plan provides a **complete end-to-end testing workflow** to validate:

- ✅ Data download and preprocessing pipeline
- ✅ Baseline model training (Logistic Regression, Linear SVM)
- ✅ Transformer model training (DistilBERT)
- ✅ FastAPI server with all models
- ✅ Docker containerization with multi-model support
- ✅ Model switching and inference
- ✅ Performance metrics and validation

**Estimated Time:** 2-4 hours (depending on GPU availability)

---

## 🔧 Prerequisites

### System Requirements

- **OS:** Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **Python:** 3.11+ (recommended)
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 10GB free space
- **Docker:** Docker Desktop or Docker Engine installed
- **GPU:** Optional but recommended for transformer training

### Software Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Check Docker installation
docker --version
docker-compose --version

# Check Git
git --version
```

### Account Setup (Optional for Cloud)

- **GCP Account:** For cloud training/deployment (optional)
- **Hugging Face Account:** For dataset access (optional, public dataset)

---

## 📊 Testing Phases

| Phase | Component | Duration | Critical |
|-------|-----------|----------|----------|
| 1 | Environment Setup | 5-10 min | ✅ Yes |
| 2 | Data Pipeline | 5-10 min | ✅ Yes |
| 3 | Baseline Models | 5-10 min | ✅ Yes |
| 4 | Transformer Training | 30-120 min | ✅ Yes |
| 5 | API Testing (Local) | 10-15 min | ✅ Yes |
| 6 | Unit & Integration Tests | 5-10 min | ✅ Yes |
| 7 | Docker Build & Test | 15-20 min | ✅ Yes |
| 8 | Multi-Model Testing | 10-15 min | ✅ Yes |
| 9 | Performance Validation | 10-15 min | ⚠️ Optional |
| 10 | Cleanup & Verification | 5 min | ⚠️ Optional |

**Total Time:** 2-4 hours (varies with GPU availability)

---

## Phase 1: Environment Setup

### 1.1 Clone Repository (if not already done)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
cd CLOUD-NLP-CLASSIFIER-GCP

# Verify directory structure
ls -la
```

**Expected Output:**
```
config/
data/
docs/
models/
scripts/
src/
tests/
Dockerfile
requirements.txt
README.md
...
```

### 1.2 Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac (Bash):**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 1.3 Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "torch|transformers|fastapi|scikit-learn"
```

**Expected Output:**
```
torch                2.0.0+
transformers         4.30.0+
fastapi              0.100.0+
scikit-learn         1.3.0+
```

### 1.4 Verify GPU (Optional)

```bash
# Check if GPU is available
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

**Expected Output (with GPU):**
```
GPU Available: True
GPU Count: 1
GPU Name: NVIDIA GeForce RTX 3060
```

**Expected Output (without GPU):**
```
GPU Available: False
GPU Count: 0
GPU Name: N/A
```

### ✅ Phase 1 Success Criteria

- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] Python version 3.11+
- [ ] GPU detection working (if applicable)

---

## Phase 2: Data Pipeline

### 2.1 Download Dataset

```bash
# Download hate speech dataset from Hugging Face
python scripts/download_dataset.py
```

**Expected Output:**
```
Downloading dataset from Hugging Face...
Dataset downloaded successfully!
Saved to: data/raw/dataset.csv
Total samples: 24,783
```

### 2.2 Verify Raw Data

```bash
# Check if dataset file exists
ls -lh data/raw/dataset.csv

# View first few lines
head -n 5 data/raw/dataset.csv
```

**Expected Output:**
```
-rw-r--r-- 1 user user 5.2M Dec  9 12:00 data/raw/dataset.csv
```

### 2.3 Preprocess Data

```bash
# Run preprocessing pipeline
python run_preprocess.py
```

**Expected Output:**
```
Loading dataset from data/raw/dataset.csv...
Loaded 24,783 samples

Preprocessing text...
100%|████████████████████████████████| 24783/24783 [00:05<00:00, 4500.00it/s]

Splitting data...
Train: 17,348 samples (70%)
Val: 3,718 samples (15%)
Test: 3,717 samples (15%)

Saving processed data...
✓ Saved train.csv (17,348 samples)
✓ Saved val.csv (3,718 samples)
✓ Saved test.csv (3,717 samples)

Preprocessing complete!
```

### 2.4 Verify Processed Data

```bash
# Check processed data files
ls -lh data/processed/

# View sample from train set
head -n 3 data/processed/train.csv
```

**Expected Output:**
```
-rw-r--r-- 1 user user 3.6M Dec  9 12:05 train.csv
-rw-r--r-- 1 user user 780K Dec  9 12:05 val.csv
-rw-r--r-- 1 user user 780K Dec  9 12:05 test.csv
```

### ✅ Phase 2 Success Criteria

- [ ] Dataset downloaded successfully (24,783 samples)
- [ ] Raw data file exists: `data/raw/dataset.csv`
- [ ] Processed data files exist: `train.csv`, `val.csv`, `test.csv`
- [ ] Train/val/test split is 70/15/15
- [ ] No errors during preprocessing

---

## Phase 3: Baseline Models

### 3.1 Train Baseline Models

```bash
# Train Logistic Regression and Linear SVM
python run_baselines.py
```

**Expected Output:**
```
Loading training data...
Loaded 17,348 training samples

Training TF-IDF vectorizer...
Vocabulary size: 10,000 features

Training Logistic Regression...
Training time: 12.5 seconds

Training Linear SVM...
Training time: 15.3 seconds

Evaluating on validation set...

Logistic Regression Results:
  Accuracy: 0.8654
  F1 Score (macro): 0.8421
  Precision: 0.8598
  Recall: 0.8512

Linear SVM Results:
  Accuracy: 0.8712
  F1 Score (macro): 0.8489
  Precision: 0.8645
  Recall: 0.8567

Saving models...
✓ Saved models/baselines/logistic_regression.joblib
✓ Saved models/baselines/linear_svm.joblib
✓ Saved models/baselines/tfidf_vectorizer.joblib
✓ Saved models/baselines/label_encoder.joblib

Baseline training complete!
```

### 3.2 Verify Baseline Models

```bash
# Check model files
ls -lh models/baselines/

# Verify model loading
python scripts/check_models.py --model-type baseline
```

**Expected Output:**
```
-rw-r--r-- 1 user user  25M Dec  9 12:10 logistic_regression.joblib
-rw-r--r-- 1 user user  28M Dec  9 12:10 linear_svm.joblib
-rw-r--r-- 1 user user  15M Dec  9 12:10 tfidf_vectorizer.joblib
-rw-r--r-- 1 user user  2.0K Dec  9 12:10 label_encoder.joblib
```

### 3.3 Test Baseline Inference

```bash
# Run baseline inference test
pytest tests/test_baseline_inference.py -v
```

**Expected Output:**
```
tests/test_baseline_inference.py::test_logistic_regression_inference PASSED
tests/test_baseline_inference.py::test_linear_svm_inference PASSED
tests/test_baseline_inference.py::test_inference_speed PASSED

======================== 3 passed in 2.5s ========================
```

### ✅ Phase 3 Success Criteria

- [ ] Both baseline models trained successfully
- [ ] Accuracy > 85% for both models
- [ ] F1 Score > 0.82 for both models
- [ ] Model files saved in `models/baselines/`
- [ ] Inference tests pass
- [ ] Inference time < 10ms per sample

---

## Phase 4: Transformer Training

### 4.1 Train DistilBERT (Local - Quick Test)

```bash
# Train with local configuration (3 epochs)
python run_transformer.py
```

**Expected Output:**
```
Loading configuration from config/config_transformer.yaml...
Mode: local
Device: cuda (NVIDIA GeForce RTX 3060)

Loading training data...
Train: 17,348 samples
Val: 3,718 samples

Loading DistilBERT model...
Model: distilbert-base-uncased
Max sequence length: 128

Tokenizing dataset...
100%|████████████████████████████████| 17348/17348 [00:45<00:00, 385.00it/s]

Training Configuration:
  Epochs: 3
  Batch size: 32
  Learning rate: 2e-05
  LR scheduler: linear
  Early stopping: enabled (patience=3)
  FP16: disabled
  Gradient accumulation: 1

Starting training...

Epoch 1/3:
100%|████████████████████████████████| 543/543 [08:25<00:00, 1.07it/s]
Train Loss: 0.3245
Val Loss: 0.2156
Val Accuracy: 0.8723
Val F1: 0.8512

Epoch 2/3:
100%|████████████████████████████████| 543/543 [08:20<00:00, 1.08it/s]
Train Loss: 0.1876
Val Loss: 0.1945
Val Accuracy: 0.8856
Val F1: 0.8678

Epoch 3/3:
100%|████████████████████████████████| 543/543 [08:18<00:00, 1.09it/s]
Train Loss: 0.1234
Val Loss: 0.1823
Val Accuracy: 0.8912
Val F1: 0.8745

Training complete!
Total training time: 25 minutes 3 seconds

Final Results:
  Best Epoch: 3
  Best Val Accuracy: 0.8912
  Best Val F1: 0.8745

Saving model...
✓ Saved models/transformer/distilbert/pytorch_model.bin
✓ Saved models/transformer/distilbert/config.json
✓ Saved models/transformer/distilbert/tokenizer_config.json
✓ Saved models/transformer/distilbert/vocab.txt
✓ Saved models/transformer/distilbert/label_encoder.joblib
✓ Saved models/transformer/distilbert/training_info.json

Model saved to: models/transformer/distilbert/
```

### 4.2 Verify Transformer Model

```bash
# Check model files
ls -lh models/transformer/distilbert/

# Verify model loading
python scripts/check_models.py --model-type transformer
```

**Expected Output:**
```
-rw-r--r-- 1 user user 268M Dec  9 12:35 pytorch_model.bin
-rw-r--r-- 1 user user 1.2K Dec  9 12:35 config.json
-rw-r--r-- 1 user user  450 Dec  9 12:35 tokenizer_config.json
-rw-r--r-- 1 user user 232K Dec  9 12:35 vocab.txt
-rw-r--r-- 1 user user 2.0K Dec  9 12:35 label_encoder.joblib
-rw-r--r-- 1 user user  850 Dec  9 12:35 training_info.json
```

### 4.3 Test Transformer Inference

```bash
# Run transformer inference test
pytest tests/test_transformer_inference.py -v
```

**Expected Output:**
```
tests/test_transformer_inference.py::test_model_loading PASSED
tests/test_transformer_inference.py::test_inference PASSED
tests/test_transformer_inference.py::test_batch_inference PASSED

======================== 3 passed in 5.2s ========================
```

### ✅ Phase 4 Success Criteria

- [ ] Transformer model trained successfully
- [ ] Training completed without errors
- [ ] Accuracy > 85% (local) or > 90% (cloud)
- [ ] F1 Score > 0.82 (local) or > 0.88 (cloud)
- [ ] Model files saved in `models/transformer/distilbert/`
- [ ] Model loads and runs inference correctly
- [ ] Inference time < 100ms per sample (GPU)

---

## Phase 5: API Testing (Local)

### 5.1 Start FastAPI Server

**Terminal 1 (Start Server):**
```bash
# Start API server
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/CLOUD-NLP-CLASSIFIER-GCP']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.

Loading models...
✓ Loaded DistilBERT model
✓ Loaded Logistic Regression model
✓ Loaded Linear SVM model
Default model: distilbert

INFO:     Application startup complete.
```

### 5.2 Test API Endpoints

**Terminal 2 (Test Endpoints):**

```bash
# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product! It is amazing!"}'

# Test list models
curl http://localhost:8000/models

# Test model switching
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# Test prediction with new model
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is terrible and offensive"}'
```

**Expected Outputs:**

**Root Endpoint:**
```json
{
  "message": "Cloud NLP Text Classification API",
  "version": "2.0.0",
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"]
}
```

**Health Check:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"],
  "classes": ["hate_speech", "offensive_language", "neither"]
}
```

**Prediction:**
```json
{
  "text": "I love this product! It is amazing!",
  "predicted_label": "neither",
  "confidence": 0.9234,
  "all_scores": {
    "hate_speech": 0.0123,
    "offensive_language": 0.0643,
    "neither": 0.9234
  },
  "model_used": "distilbert",
  "inference_time_ms": 45.2
}
```

**List Models:**
```json
{
  "current_model": "distilbert",
  "available_models": [
    {
      "name": "distilbert",
      "type": "transformer",
      "description": "DistilBERT fine-tuned model",
      "accuracy": 0.8912,
      "f1_score": 0.8745,
      "inference_time_ms": 45
    },
    {
      "name": "logistic_regression",
      "type": "baseline",
      "description": "TF-IDF + Logistic Regression",
      "accuracy": 0.8654,
      "f1_score": 0.8421,
      "inference_time_ms": 5
    },
    {
      "name": "linear_svm",
      "type": "baseline",
      "description": "TF-IDF + Linear SVM",
      "accuracy": 0.8712,
      "f1_score": 0.8489,
      "inference_time_ms": 5
    }
  ]
}
```

### 5.3 Test Interactive API Documentation

```bash
# Open in browser
# Windows:
start http://localhost:8000/docs

# Linux:
xdg-open http://localhost:8000/docs

# Mac:
open http://localhost:8000/docs
```

**Verify:**
- [ ] Swagger UI loads correctly
- [ ] All endpoints visible (/, /health, /predict, /models, /models/switch)
- [ ] Can test endpoints interactively
- [ ] Request/response schemas displayed

### 5.4 Run Client Example Script

```bash
# Run comprehensive client example
python scripts/client_example.py
```

**Expected Output:**
```
=== Cloud NLP Classification API Client ===

Testing API endpoints...

1. Root Endpoint:
   ✓ API is running
   Version: 2.0.0
   Current model: distilbert

2. Health Check:
   ✓ API is healthy
   Models loaded: 3

3. Single Prediction:
   Text: "I love this product!"
   Prediction: neither
   Confidence: 92.34%
   Inference time: 45.2ms

4. Batch Predictions:
   Processing 5 samples...
   ✓ All predictions successful
   Average inference time: 47.8ms

5. Model Switching:
   ✓ Switched to logistic_regression
   ✓ Prediction with new model successful
   Inference time: 5.1ms (9x faster!)

All tests passed! ✓
```

### ✅ Phase 5 Success Criteria

- [ ] API server starts without errors
- [ ] All models load successfully
- [ ] Root endpoint returns correct info
- [ ] Health check shows all 3 models
- [ ] Prediction endpoint works correctly
- [ ] Model switching works without restart
- [ ] Interactive docs accessible
- [ ] Client example script passes all tests
- [ ] Inference times within expected ranges

---

## Phase 6: Unit & Integration Tests

### 6.1 Run Complete Test Suite

```bash
# Run all tests with the universal test runner
python run_tests.py
```

**Expected Output:**
```
=== Running Test Suite ===

Discovering tests...
Found 25 tests

Running tests...

tests/test_basic_imports.py::test_import_pandas PASSED
tests/test_basic_imports.py::test_import_sklearn PASSED
tests/test_basic_imports.py::test_import_torch PASSED
tests/test_basic_imports.py::test_import_transformers PASSED
tests/test_basic_imports.py::test_import_fastapi PASSED
tests/test_basic_imports.py::test_import_api_server PASSED

tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_predict_endpoint PASSED
tests/test_api.py::test_predict_invalid_input PASSED
tests/test_api.py::test_list_models_endpoint PASSED
tests/test_api.py::test_switch_model_endpoint PASSED
tests/test_api.py::test_switch_invalid_model PASSED

tests/test_baseline_inference.py::test_load_baseline_models PASSED
tests/test_baseline_inference.py::test_logistic_regression_inference PASSED
tests/test_baseline_inference.py::test_linear_svm_inference PASSED
tests/test_baseline_inference.py::test_inference_speed PASSED

tests/test_transformer_inference.py::test_load_transformer_model PASSED
tests/test_transformer_inference.py::test_transformer_inference PASSED
tests/test_transformer_inference.py::test_batch_inference PASSED

tests/test_advanced_training.py::test_config_loading PASSED
tests/test_advanced_training.py::test_early_stopping_config PASSED
tests/test_advanced_training.py::test_lr_scheduler_config PASSED
tests/test_advanced_training.py::test_fp16_config PASSED

======================== 25 passed in 45.2s ========================

✓ All tests passed!
✓ Zero deprecation warnings
✓ Pydantic V2 compliant
```

### 6.2 Run Tests with Coverage

```bash
# Run with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

**Expected Output:**
```
======================== Coverage Report ========================
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/__init__.py                       0      0   100%
src/api/__init__.py                   0      0   100%
src/api/server.py                   245     12    95%
src/data/__init__.py                  0      0   100%
src/data/preprocess.py              156      8    95%
src/models/__init__.py                0      0   100%
src/models/train_baselines.py       198     10    95%
src/models/transformer_training.py  412     25    94%
src/models/evaluation.py            123      6    95%
-----------------------------------------------------
TOTAL                              1134     61    95%

HTML coverage report generated: htmlcov/index.html
```

### 6.3 Run Specific Test Categories

```bash
# Import tests only
pytest tests/test_basic_imports.py -v

# API tests only
pytest tests/test_api.py -v

# Model inference tests only
pytest tests/test_baseline_inference.py tests/test_transformer_inference.py -v

# Training config tests only
pytest tests/test_advanced_training.py -v
```

### ✅ Phase 6 Success Criteria

- [ ] All 25+ tests pass
- [ ] Zero test failures
- [ ] Zero deprecation warnings
- [ ] Code coverage > 90%
- [ ] All test categories pass independently
- [ ] No Pydantic V2 warnings
- [ ] No FastAPI deprecation warnings

---

## Phase 7: Docker Build & Test

### 7.1 Verify Models Exist

```bash
# Check all required models are present
ls -lh models/baselines/
ls -lh models/transformer/distilbert/
```

**Expected:**
```
models/baselines/
  logistic_regression.joblib
  linear_svm.joblib
  tfidf_vectorizer.joblib
  label_encoder.joblib

models/transformer/distilbert/
  pytorch_model.bin
  config.json
  tokenizer_config.json
  vocab.txt
  label_encoder.joblib
  training_info.json
```

### 7.2 Build Docker Image

```bash
# Build the Docker image (this may take 5-10 minutes)
docker build -t cloud-nlp-classifier:test .

# Monitor build progress
# Look for successful completion of all steps
```

**Expected Output:**
```
[+] Building 487.3s (18/18) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.85kB
 => [internal] load .dockerignore
 => => transferring context: 1.45kB
 => [internal] load metadata for docker.io/library/python:3.11-slim
 => [1/13] FROM docker.io/library/python:3.11-slim
 => [internal] load build context
 => => transferring context: 350.2MB
 => [2/13] WORKDIR /app
 => [3/13] RUN apt-get update && apt-get install -y ...
 => [4/13] COPY requirements.txt .
 => [5/13] RUN pip install --no-cache-dir -r requirements.txt
 => [6/13] COPY src/ ./src/
 => [7/13] COPY config/ ./config/
 => [8/13] COPY models/ ./models/
 => [9/13] RUN useradd -m -u 1000 appuser
 => [10/13] RUN chown -R appuser:appuser /app
 => [11/13] USER appuser
 => [12/13] EXPOSE 8000
 => [13/13] HEALTHCHECK ...
 => exporting to image
 => => exporting layers
 => => writing image sha256:abc123...
 => => naming to docker.io/library/cloud-nlp-classifier:test

Successfully built cloud-nlp-classifier:test
```

### 7.3 Verify Docker Image

```bash
# Check image size and details
docker images cloud-nlp-classifier:test

# Inspect image
docker inspect cloud-nlp-classifier:test
```

**Expected Output:**
```
REPOSITORY               TAG       IMAGE ID       CREATED         SIZE
cloud-nlp-classifier     test      abc123def456   2 minutes ago   2.1GB
```

### 7.4 Run Docker Container

```bash
# Run container with default model (DistilBERT)
docker run -d -p 8000:8000 --name nlp-api-test cloud-nlp-classifier:test

# Wait for startup (5-8 seconds)
sleep 10

# Check container status
docker ps

# View startup logs
docker logs nlp-api-test
```

**Expected Logs:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.

Loading models...
✓ Loaded DistilBERT model from /app/models/transformer/distilbert
✓ Loaded Logistic Regression model from /app/models/baselines/logistic_regression.joblib
✓ Loaded Linear SVM model from /app/models/baselines/linear_svm.joblib
Default model: distilbert

INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 7.5 Test Containerized API

```bash
# Test health check
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Test list models
curl http://localhost:8000/models
```

**Expected:**
- All endpoints respond correctly
- Same responses as local API testing
- Inference times similar to local

### 7.6 Test Docker Health Check

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' nlp-api-test

# View health check logs
docker inspect --format='{{json .State.Health}}' nlp-api-test | python -m json.tool
```

**Expected:**
```
Status: healthy
FailingStreak: 0
Log: [
  {
    "Start": "2025-12-09T17:30:00Z",
    "End": "2025-12-09T17:30:00Z",
    "ExitCode": 0,
    "Output": "healthy"
  }
]
```

### 7.7 Stop and Remove Test Container

```bash
# Stop container
docker stop nlp-api-test

# Remove container
docker rm nlp-api-test
```

### ✅ Phase 7 Success Criteria

- [ ] Docker image builds successfully
- [ ] Image size ~2-2.5 GB
- [ ] Container starts without errors
- [ ] All 3 models load successfully
- [ ] Health check passes (status: healthy)
- [ ] API endpoints respond correctly
- [ ] Inference works as expected
- [ ] Container logs show no errors

---

## Phase 8: Multi-Model Testing

### 8.1 Test All Model Variants

```bash
# Test 1: Run with default model (DistilBERT)
docker run -d -p 8000:8000 --name nlp-distilbert cloud-nlp-classifier:test
sleep 10
curl http://localhost:8000/health | python -m json.tool
docker stop nlp-distilbert && docker rm nlp-distilbert

# Test 2: Run with Logistic Regression
docker run -d -p 8000:8000 -e DEFAULT_MODEL=logistic_regression --name nlp-logreg cloud-nlp-classifier:test
sleep 10
curl http://localhost:8000/health | python -m json.tool
docker stop nlp-logreg && docker rm nlp-logreg

# Test 3: Run with Linear SVM
docker run -d -p 8000:8000 -e DEFAULT_MODEL=linear_svm --name nlp-svm cloud-nlp-classifier:test
sleep 10
curl http://localhost:8000/health | python -m json.tool
docker stop nlp-svm && docker rm nlp-svm
```

**Verify:**
- Each container starts with correct default model
- Health check shows correct `current_model`
- All 3 models available in each container

### 8.2 Test Dynamic Model Switching

```bash
# Start container with DistilBERT
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier:test
sleep 10

# Test 1: Predict with DistilBERT
echo "=== Test 1: DistilBERT ==="
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I hate this offensive content"}' | python -m json.tool

# Test 2: Switch to Logistic Regression
echo "=== Test 2: Switch to Logistic Regression ==="
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}' | python -m json.tool

# Test 3: Predict with Logistic Regression
echo "=== Test 3: Predict with Logistic Regression ==="
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I hate this offensive content"}' | python -m json.tool

# Test 4: Switch to Linear SVM
echo "=== Test 4: Switch to Linear SVM ==="
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "linear_svm"}' | python -m json.tool

# Test 5: Predict with Linear SVM
echo "=== Test 5: Predict with Linear SVM ==="
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I hate this offensive content"}' | python -m json.tool

# Cleanup
docker stop nlp-api && docker rm nlp-api
```

**Verify:**
- Model switches without container restart
- Each prediction shows correct `model_used`
- Inference times match expected values (DistilBERT ~50ms, baselines ~5ms)
- Predictions are consistent for each model

### 8.3 Run Multi-Model Client Example

```bash
# Start container
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier:test
sleep 10

# Run multi-model client example
python scripts/client_multimodel_example.py
```

**Expected Output:**
```
=== Multi-Model Testing Client ===

Testing all 3 models with the same input...

Input: "This is offensive hate speech content"

Model 1: DistilBERT
  Prediction: hate_speech
  Confidence: 94.2%
  Inference time: 48.3ms

Model 2: Logistic Regression
  Prediction: hate_speech
  Confidence: 87.6%
  Inference time: 5.1ms (9.5x faster!)

Model 3: Linear SVM
  Prediction: hate_speech
  Confidence: 89.3%
  Inference time: 4.8ms (10.1x faster!)

Performance Comparison:
  DistilBERT:           48.3ms (baseline)
  Logistic Regression:   5.1ms (9.5x faster)
  Linear SVM:            4.8ms (10.1x faster)

Accuracy Comparison:
  DistilBERT:           94.2% confidence
  Logistic Regression:  87.6% confidence
  Linear SVM:           89.3% confidence

All models agree on prediction: hate_speech ✓

# Cleanup
docker stop nlp-api && docker rm nlp-api
```

### ✅ Phase 8 Success Criteria

- [ ] All 3 models can be set as default via env var
- [ ] Model switching works without restart
- [ ] Each model produces predictions correctly
- [ ] Inference times match expectations:
  - DistilBERT: 40-60ms
  - Logistic Regression: 3-7ms
  - Linear SVM: 3-7ms
- [ ] Multi-model client example passes all tests
- [ ] No errors during model switching

---

## Phase 9: Performance Validation

### 9.1 Measure Inference Latency

```bash
# Start container
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier:test
sleep 10

# Create performance test script
cat > test_performance.sh << 'EOF'
#!/bin/bash
echo "=== Performance Testing ==="
echo ""

# Test DistilBERT
echo "Testing DistilBERT (100 requests)..."
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "This is a test message for performance testing"}' \
    -w "%{time_total}\n" -o /dev/null
done | awk '{sum+=$1; count++} END {print "Average: " sum/count*1000 "ms"}'

# Switch to Logistic Regression
curl -s -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}' > /dev/null

echo ""
echo "Testing Logistic Regression (100 requests)..."
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "This is a test message for performance testing"}' \
    -w "%{time_total}\n" -o /dev/null
done | awk '{sum+=$1; count++} END {print "Average: " sum/count*1000 "ms"}'
EOF

chmod +x test_performance.sh
./test_performance.sh
```

**Expected Output:**
```
=== Performance Testing ===

Testing DistilBERT (100 requests)...
Average: 52.3ms

Testing Logistic Regression (100 requests)...
Average: 6.2ms
```

### 9.2 Measure Throughput

```bash
# Install Apache Bench (if not installed)
# Ubuntu/Debian: sudo apt-get install apache2-utils
# Mac: brew install httpd (includes ab)
# Windows: Download from Apache website

# Test throughput with DistilBERT
ab -n 1000 -c 10 -p payload.json -T application/json http://localhost:8000/predict

# Create payload file
echo '{"text": "This is a test message"}' > payload.json
```

**Expected Output:**
```
Concurrency Level:      10
Time taken for tests:   45.234 seconds
Complete requests:      1000
Failed requests:        0
Requests per second:    22.11 [#/sec] (mean)
Time per request:       452.34 [ms] (mean)
Time per request:       45.23 [ms] (mean, across all concurrent requests)
```

### 9.3 Memory Usage

```bash
# Monitor container memory usage
docker stats nlp-api --no-stream

# Check detailed memory info
docker inspect nlp-api | grep -A 10 Memory
```

**Expected Output:**
```
CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %
abc123def456   nlp-api   15.2%     1.2GiB / 8GiB        15.0%
```

### 9.4 Cleanup

```bash
# Stop and remove container
docker stop nlp-api && docker rm nlp-api

# Remove test scripts
rm -f test_performance.sh payload.json
```

### ✅ Phase 9 Success Criteria

- [ ] DistilBERT inference: 40-60ms average
- [ ] Baseline inference: 3-7ms average
- [ ] Throughput: 20-50 req/s (single worker)
- [ ] Memory usage: ~1.2GB active
- [ ] Zero failed requests in load test
- [ ] Container remains stable under load

---

## Phase 10: Cleanup & Verification

### 10.1 Docker Cleanup

```bash
# Stop all running containers
docker stop $(docker ps -q --filter ancestor=cloud-nlp-classifier:test)

# Remove all test containers
docker rm $(docker ps -a -q --filter ancestor=cloud-nlp-classifier:test)

# Optional: Remove test image
docker rmi cloud-nlp-classifier:test

# Clean up unused Docker resources
docker system prune -f
```

### 10.2 Verify Final State

```bash
# Check directory structure
ls -lh data/raw/
ls -lh data/processed/
ls -lh models/baselines/
ls -lh models/transformer/distilbert/

# Verify all model files exist
python scripts/check_models.py --all
```

**Expected Output:**
```
=== Model Verification ===

Baseline Models:
  ✓ logistic_regression.joblib (25.3 MB)
  ✓ linear_svm.joblib (28.1 MB)
  ✓ tfidf_vectorizer.joblib (15.2 MB)
  ✓ label_encoder.joblib (2.1 KB)

Transformer Model:
  ✓ pytorch_model.bin (268.4 MB)
  ✓ config.json (1.2 KB)
  ✓ tokenizer_config.json (450 B)
  ✓ vocab.txt (232.1 KB)
  ✓ label_encoder.joblib (2.1 KB)
  ✓ training_info.json (850 B)

All models verified successfully! ✓
```

### 10.3 Generate Test Report

```bash
# Create test report
cat > END_TO_END_TEST_REPORT.md << 'EOF'
# End-to-End Test Report

**Date:** $(date)
**Tester:** [Your Name]
**Duration:** [Total Time]

## Test Results

### Phase 1: Environment Setup
- [ ] PASS - Virtual environment created
- [ ] PASS - Dependencies installed
- [ ] PASS - GPU detection working

### Phase 2: Data Pipeline
- [ ] PASS - Dataset downloaded (24,783 samples)
- [ ] PASS - Data preprocessed successfully
- [ ] PASS - Train/val/test splits created

### Phase 3: Baseline Models
- [ ] PASS - Logistic Regression trained (Acc: X.XX%)
- [ ] PASS - Linear SVM trained (Acc: X.XX%)
- [ ] PASS - Models saved and loadable

### Phase 4: Transformer Training
- [ ] PASS - DistilBERT trained (Acc: X.XX%)
- [ ] PASS - Model saved and loadable
- [ ] PASS - Inference working

### Phase 5: API Testing (Local)
- [ ] PASS - API server starts
- [ ] PASS - All endpoints working
- [ ] PASS - Model switching works

### Phase 6: Unit & Integration Tests
- [ ] PASS - All 25+ tests pass
- [ ] PASS - Zero deprecation warnings
- [ ] PASS - Coverage > 90%

### Phase 7: Docker Build & Test
- [ ] PASS - Image builds successfully
- [ ] PASS - Container runs correctly
- [ ] PASS - Health checks pass

### Phase 8: Multi-Model Testing
- [ ] PASS - All models work in container
- [ ] PASS - Model switching works
- [ ] PASS - Performance as expected

### Phase 9: Performance Validation
- [ ] PASS - Latency within targets
- [ ] PASS - Throughput acceptable
- [ ] PASS - Memory usage normal

### Phase 10: Cleanup
- [ ] PASS - All resources cleaned up
- [ ] PASS - Final verification complete

## Summary

**Total Tests:** 50+
**Passed:** XX
**Failed:** XX
**Success Rate:** XX%

## Notes

[Add any observations, issues, or recommendations]

EOF

echo "Test report template created: END_TO_END_TEST_REPORT.md"
```

### ✅ Phase 10 Success Criteria

- [ ] All Docker resources cleaned up
- [ ] All model files verified
- [ ] Test report generated
- [ ] No lingering processes or containers

---

## 🎯 Success Criteria

### Overall Success Criteria

The end-to-end test is considered **SUCCESSFUL** if:

1. **Data Pipeline** ✅
   - Dataset downloaded (24,783 samples)
   - Data preprocessed without errors
   - Train/val/test splits created (70/15/15)

2. **Model Training** ✅
   - Baseline models trained (Acc > 85%)
   - Transformer model trained (Acc > 85% local, > 90% cloud)
   - All model files saved correctly

3. **API Functionality** ✅
   - API server starts without errors
   - All endpoints respond correctly
   - Model switching works without restart
   - Interactive docs accessible

4. **Testing** ✅
   - All unit tests pass (25+ tests)
   - Zero deprecation warnings
   - Code coverage > 90%
   - Integration tests pass

5. **Docker Deployment** ✅
   - Image builds successfully (~2GB)
   - Container runs without errors
   - All 3 models load correctly
   - Health checks pass
   - API endpoints work in container

6. **Multi-Model Support** ✅
   - All models accessible via API
   - Dynamic model switching works
   - Performance matches expectations
   - No errors during switching

7. **Performance** ✅
   - DistilBERT: 40-60ms inference
   - Baselines: 3-7ms inference
   - Throughput: 20-50 req/s
   - Memory: ~1.2GB active
   - Zero failed requests

### Minimum Passing Criteria

- [ ] All 10 phases completed
- [ ] Zero critical errors
- [ ] All models functional
- [ ] Docker container runs successfully
- [ ] API endpoints respond correctly
- [ ] Performance within acceptable ranges

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue 1: Dataset Download Fails

**Symptoms:**
```
Error: Failed to download dataset from Hugging Face
ConnectionError: HTTPSConnectionPool...
```

**Solutions:**
```bash
# Check internet connection
ping huggingface.co

# Try with different mirror
export HF_ENDPOINT=https://hf-mirror.com
python scripts/download_dataset.py

# Manual download
# Visit: https://huggingface.co/datasets/hate_speech_offensive
# Download and place in data/raw/dataset.csv
```

#### Issue 2: GPU Not Detected

**Symptoms:**
```
GPU Available: False
Training on CPU (this will be slow)
```

**Solutions:**
```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU again
python -c "import torch; print(torch.cuda.is_available())"
```

#### Issue 3: Docker Build Fails

**Symptoms:**
```
ERROR: failed to solve: failed to compute cache key
```

**Solutions:**
```bash
# Check if models exist
ls -lh models/baselines/
ls -lh models/transformer/distilbert/

# Train models if missing
python run_baselines.py
python run_transformer.py

# Build with no cache
docker build --no-cache -t cloud-nlp-classifier:test .

# Check Docker disk space
docker system df
docker system prune -a
```

#### Issue 4: Container Won't Start

**Symptoms:**
```
Error: Container exits immediately
docker logs shows: ModuleNotFoundError
```

**Solutions:**
```bash
# Check logs
docker logs nlp-api

# Run interactively to debug
docker run -it -p 8000:8000 cloud-nlp-classifier:test /bin/bash

# Inside container, test manually
python -c "from src.api.server import app"

# Rebuild image
docker rmi cloud-nlp-classifier:test
docker build -t cloud-nlp-classifier:test .
```

#### Issue 5: Port Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Solutions:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Or use different port
docker run -p 8001:8000 cloud-nlp-classifier:test
```

#### Issue 6: Out of Memory

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
```bash
# Reduce batch size in config
# Edit config/config_transformer.yaml:
training:
  train_batch_size: 16  # Reduce from 32

# Enable gradient accumulation
training:
  gradient_accumulation_steps: 2

# Use CPU instead
device: "cpu"

# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory: 8GB
```

#### Issue 7: Tests Failing

**Symptoms:**
```
FAILED tests/test_api.py::test_predict_endpoint
AssertionError: Model not loaded
```

**Solutions:**
```bash
# Ensure models are trained
python scripts/check_models.py --all

# Retrain if missing
python run_baselines.py
python run_transformer.py

# Run tests with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_api.py::test_predict_endpoint -v -s
```

#### Issue 8: Slow Training

**Symptoms:**
```
Training is taking hours on CPU
```

**Solutions:**
```bash
# Use GPU if available
# Check GPU: nvidia-smi

# Use cloud training (GCP)
# See README.md section on GCP Cloud Training

# Reduce epochs for testing
python -m src.models.transformer_training --epochs 1

# Use smaller model (already using DistilBERT, smallest option)
```

### Getting Help

If you encounter issues not covered here:

1. **Check Logs:**
   ```bash
   # API logs
   docker logs nlp-api
   
   # Training logs
   cat models/transformer/distilbert/training.log
   ```

2. **Check Documentation:**
   - `README.md` - Main documentation
   - `docs/DOCKER_GUIDE.md` - Docker details
   - `docs/MULTI_MODEL_DOCKER_GUIDE.md` - Multi-model info
   - `docs/PHASE10_ADVANCED_TRAINING_SUMMARY.md` - Training details

3. **Verify Environment:**
   ```bash
   python --version
   pip list
   docker --version
   nvidia-smi  # If using GPU
   ```

4. **Clean Start:**
   ```bash
   # Remove virtual environment
   rm -rf venv
   
   # Recreate and reinstall
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

---

## 📝 Test Execution Checklist

Use this checklist to track your progress:

### Pre-Test Setup
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Docker installed and running

### Phase 1: Environment Setup
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] GPU detection verified (if applicable)

### Phase 2: Data Pipeline
- [ ] Dataset downloaded (24,783 samples)
- [ ] Data preprocessed successfully
- [ ] Train/val/test splits created

### Phase 3: Baseline Models
- [ ] Logistic Regression trained
- [ ] Linear SVM trained
- [ ] Models saved and verified

### Phase 4: Transformer Training
- [ ] DistilBERT trained
- [ ] Model saved and verified
- [ ] Inference tested

### Phase 5: API Testing (Local)
- [ ] API server started
- [ ] All endpoints tested
- [ ] Model switching verified
- [ ] Client example passed

### Phase 6: Unit & Integration Tests
- [ ] All tests passed
- [ ] Zero warnings
- [ ] Coverage > 90%

### Phase 7: Docker Build & Test
- [ ] Image built successfully
- [ ] Container runs correctly
- [ ] Health checks pass
- [ ] API accessible

### Phase 8: Multi-Model Testing
- [ ] All models work in container
- [ ] Model switching tested
- [ ] Multi-model client passed

### Phase 9: Performance Validation
- [ ] Latency measured
- [ ] Throughput tested
- [ ] Memory usage checked

### Phase 10: Cleanup
- [ ] Docker resources cleaned
- [ ] Final verification complete
- [ ] Test report generated

---

## 📊 Expected Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1 | 5-10 min | 10 min |
| Phase 2 | 5-10 min | 20 min |
| Phase 3 | 5-10 min | 30 min |
| Phase 4 | 30-120 min | 150 min |
| Phase 5 | 10-15 min | 165 min |
| Phase 6 | 5-10 min | 175 min |
| Phase 7 | 15-20 min | 195 min |
| Phase 8 | 10-15 min | 210 min |
| Phase 9 | 10-15 min | 225 min |
| Phase 10 | 5 min | 230 min |

**Total: ~2-4 hours** (depending on GPU availability and training time)

---

## 🎉 Conclusion

This end-to-end testing plan ensures complete validation of the CLOUD-NLP-CLASSIFIER-GCP repository from data download through production Docker deployment. Following this plan guarantees that all components work correctly and are ready for production use.

**Key Achievements:**
- ✅ Complete data pipeline validated
- ✅ All 3 models trained and tested
- ✅ API functionality verified
- ✅ Docker deployment successful
- ✅ Multi-model support confirmed
- ✅ Performance metrics validated

**Next Steps:**
- Deploy to GCP Cloud Run (see README.md)
- Set up monitoring and logging
- Implement CI/CD pipeline
- Add more models or features

---

**Document Version:** 1.0  
**Last Updated:** December 9, 2025  
**Maintained By:** CLOUD-NLP-CLASSIFIER-GCP Team
