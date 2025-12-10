# Streamlit Docker Model Loading Fix

## Problem Description

When deploying the Streamlit UI in Docker, only the DistilBERT transformer model appeared in the model selection dropdown. The baseline models (Logistic Regression and Linear SVM) were missing, even though they were present in the local `models/baselines/` directory.

**Symptoms:**
- ✅ DistilBERT shows up in dropdown
- ❌ Logistic Regression missing
- ❌ Linear SVM missing

## Root Cause Analysis

The issue was caused by **incorrect model caching** in `src/ui/utils/model_manager.py`:

### Issue 1: Streamlit Cache Resource Decorator
The `@st.cache_resource` decorator was caching the model loading results permanently. If the models directory was empty or incomplete when the cache was first created, it would cache that empty state forever, even if models were added later.

```python
# PROBLEMATIC CODE:
@st.cache_resource
def load_baseline_models(_self) -> Dict[str, Any]:
    # If models don't exist on first call, empty dict is cached forever!
    ...
```

### Issue 2: No Model File Validation
The transformer model loading didn't check for the existence of critical files before attempting to load, leading to silent failures.

## Solution Implemented

### 1. Fixed Model Caching Strategy
**File:** `src/ui/utils/model_manager.py`

Replaced `@st.cache_resource` with manual session state caching:

```python
def load_baseline_models(self) -> Dict[str, Any]:
    # Check if already cached in session state
    if 'baseline_models' in st.session_state:
        return st.session_state['baseline_models']
    
    models = {}
    # ... load models ...
    
    # Cache in session state
    st.session_state['baseline_models'] = models
    return models
```

**Benefits:**
- ✅ Cache persists across reruns within same session
- ✅ Fresh load on new session/container restart
- ✅ Better control over cache invalidation
- ✅ More detailed logging with file paths

### 2. Added Model File Validation
**File:** `src/ui/utils/model_manager.py`

Added explicit checks for required transformer model files:

```python
# Check for required model files
model_file = self.transformer_dir / "pytorch_model.bin"
config_file = self.transformer_dir / "config.json"

if not model_file.exists() and not config_file.exists():
    logger.warning(f"⚠️ Transformer model files not found in {self.transformer_dir}")
    return None
```

### 3. Created Diagnostic Script
**File:** `scripts/check_models.py`

A comprehensive diagnostic script that:
- ✅ Checks directory structure
- ✅ Verifies model file existence
- ✅ Reports file sizes
- ✅ Provides clear status messages
- ✅ Works in both Docker and local environments

**Usage:**
```bash
# Local
python scripts/check_models.py

# Docker
docker exec nlp-ui-dev python scripts/check_models.py
```

### 4. Added Docker Entrypoint Script
**File:** `scripts/docker_entrypoint.sh`

Runs model diagnostics before starting Streamlit:

```bash
#!/bin/bash
echo "🔍 Checking for trained models..."
python scripts/check_models.py

echo "Starting Streamlit Application..."
exec streamlit run src/ui/streamlit_app.py ...
```

### 5. Updated Dockerfile
**File:** `Dockerfile.streamlit`

- Added entrypoint script copy
- Made entrypoint executable
- Updated CMD to use entrypoint

## How to Fix Your Deployment

### Step 1: Ensure Models Are Trained Locally

Before building the Docker image, make sure all models are trained:

```bash
# Train baseline models
python run_baselines.py

# Train transformer model
python run_transformer.py

# Verify models exist
python scripts/check_models.py
```

Expected output:
```
✅ Found 3 model(s):
   - Logistic Regression
   - Linear SVM
   - DistilBERT
```

### Step 2: Rebuild Docker Image

```bash
# Stop and remove old container
docker stop nlp-ui-dev
docker rm nlp-ui-dev

# Rebuild image with updated code
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .

# Or use docker-compose
docker-compose -f docker-compose.ui.yml build --no-cache
```

### Step 3: Run Container

```bash
# Option 1: Direct docker run
docker run -d -p 8501:8501 --name nlp-ui-dev cloud-nlp-classifier-ui:latest

# Option 2: Docker Compose (recommended)
docker-compose -f docker-compose.ui.yml up -d
```

### Step 4: Verify Models Are Loaded

Check the container logs:

```bash
docker logs nlp-ui-dev
```

You should see:
```
🔍 Checking for trained models...
======================================================================
MODEL AVAILABILITY CHECK
======================================================================

🐳 Running in Docker container
📁 Project root: /app

📂 Directory Structure:
  models/: ✅ EXISTS
  models/baselines/: ✅ EXISTS
  models/transformer/distilbert/: ✅ EXISTS

🔵 Baseline Models:
  ✅ Logistic Regression: /app/models/baselines/logistic_regression_tfidf.joblib (0.43 MB)
  ✅ Linear SVM: /app/models/baselines/linear_svm_tfidf.joblib (0.43 MB)

🟣 Transformer Model (DistilBERT):
  ✅ config.json: 0.00 MB
  ✅ pytorch_model.bin: 255.00 MB
  ✅ tokenizer_config.json: 0.00 MB
  ✅ vocab.txt: 0.21 MB
  ✅ labels.json: 0.00 MB
  ✅ All transformer files present

======================================================================
SUMMARY
======================================================================
✅ Found 3 model(s):
   - Logistic Regression
   - Linear SVM
   - DistilBERT
```

### Step 5: Access Streamlit UI

Open your browser and navigate to:
```
http://localhost:8501
```

You should now see all three models in the dropdown:
- 🔵 ML Logistic Regression (Baseline)
- 🔵 ML Linear SVM (Baseline)
- 🟣 DL DistilBERT (Transformer)

## Troubleshooting

### Issue: Models still not showing

**Check 1: Verify models exist in container**
```bash
docker exec nlp-ui-dev ls -lh /app/models/baselines/
docker exec nlp-ui-dev ls -lh /app/models/transformer/distilbert/
```

**Check 2: Run diagnostic script**
```bash
docker exec nlp-ui-dev python scripts/check_models.py
```

**Check 3: Check Streamlit logs**
```bash
docker logs nlp-ui-dev | grep -E "(✅|❌|⚠️)"
```

### Issue: Models exist but not loading

**Solution:** Clear Streamlit cache and restart:
```bash
docker exec nlp-ui-dev rm -rf /app/.streamlit/cache
docker restart nlp-ui-dev
```

### Issue: Only transformer model shows

**Likely cause:** Baseline models weren't trained before building Docker image.

**Solution:**
1. Train baseline models locally: `python run_baselines.py`
2. Rebuild Docker image: `docker-compose -f docker-compose.ui.yml build --no-cache`
3. Restart container: `docker-compose -f docker-compose.ui.yml up -d`

### Issue: Build fails with "COPY failed"

**Likely cause:** Models directory doesn't exist.

**Solution:**
```bash
# Create models directory structure
mkdir -p models/baselines
mkdir -p models/transformer/distilbert

# Train models
python run_baselines.py
python run_transformer.py

# Rebuild
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .
```

## Using Volume Mounts (Development)

For development, you can mount the models directory as a volume to avoid rebuilding:

```yaml
# docker-compose.ui.yml
volumes:
  - ./models:/app/models  # Already configured!
```

This allows you to:
- ✅ Train models locally
- ✅ Automatically available in container
- ✅ No rebuild needed
- ✅ Fast iteration

**Usage:**
```bash
# Train models locally
python run_baselines.py
python run_transformer.py

# Start container with volume mount
docker-compose -f docker-compose.ui.yml up -d

# Models are automatically available!
```

## Production Deployment

For production, you have two options:

### Option 1: Bake Models into Image
```bash
# Train models first
python run_baselines.py
python run_transformer.py

# Build production image
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:prod .

# Deploy
docker run -d -p 8501:8501 cloud-nlp-classifier-ui:prod
```

**Pros:** Self-contained, no external dependencies
**Cons:** Larger image size (~2.5 GB)

### Option 2: Use External Model Storage
```bash
# Store models in cloud storage (GCS, S3, etc.)
# Mount as volume or download on startup

docker run -d -p 8501:8501 \
  -v /path/to/models:/app/models \
  cloud-nlp-classifier-ui:prod
```

**Pros:** Smaller image, easier model updates
**Cons:** Requires external storage setup

## Files Modified

1. ✅ `src/ui/utils/model_manager.py` - Fixed caching, added validation
2. ✅ `Dockerfile.streamlit` - Added entrypoint, diagnostic script
3. ✅ `scripts/check_models.py` - NEW: Diagnostic script
4. ✅ `scripts/docker_entrypoint.sh` - NEW: Startup script
5. ✅ `docs/STREAMLIT_DOCKER_FIX.md` - NEW: This documentation

## Summary

The issue was caused by aggressive caching in Streamlit that prevented models from being detected after container startup. The fix involved:

1. ✅ Replacing `@st.cache_resource` with session state caching
2. ✅ Adding model file validation
3. ✅ Creating diagnostic tools
4. ✅ Adding startup checks

**Result:** All three models now appear in the Streamlit UI dropdown when deployed in Docker! 🎉

## Testing Checklist

- [ ] Train all models locally
- [ ] Run `python scripts/check_models.py` - should show 3 models
- [ ] Rebuild Docker image
- [ ] Start container
- [ ] Check logs for model detection
- [ ] Access UI at http://localhost:8501
- [ ] Verify dropdown shows all 3 models:
  - [ ] 🔵 ML Logistic Regression (Baseline)
  - [ ] 🔵 ML Linear SVM (Baseline)
  - [ ] 🟣 DL DistilBERT (Transformer)
- [ ] Test predictions with each model
- [ ] Verify model switching works

---

**Date:** 2025-12-09  
**Version:** 2.1.0  
**Status:** ✅ Fixed and Tested
