# Scripts Directory Documentation

## Overview

The `scripts/` directory contains 38 automation scripts for training, deployment, testing, and cloud operations. Scripts are provided in both PowerShell (`.ps1`) and Bash (`.sh`) formats for cross-platform compatibility.

**Purpose**: Automate all aspects of the ML pipeline from data preprocessing to cloud deployment, with platform-specific implementations for Windows, Linux, and Mac.

---

## Directory Structure

```
scripts/
├── Core Utilities (5 files)
│   ├── check_models.py                    # Model availability diagnostic
│   ├── client_example.py                  # Basic API client
│   ├── client_multimodel_example.py       # Multi-model comparison client
│   ├── download_dataset.py                # Dataset downloader (hate speech + toxicity)
│   └── docker_entrypoint.sh               # Streamlit Docker entrypoint
│
├── Local Training (6 files)
│   ├── run_preprocess_local.ps1/.sh       # Data preprocessing
│   ├── run_baselines_local.ps1/.sh        # Baseline model training
│   └── run_transformer_local.ps1/.sh      # Transformer local training
│
├── API & Serving (2 files)
│   └── run_api_local.ps1/.sh              # FastAPI server launcher
│
├── Cloud Training (3 files)
│   ├── setup_gcp_training.sh              # GCP VM environment setup
│   ├── run_gcp_training.sh                # Cloud transformer training
│   └── run_transformer_cloud.ps1          # Windows cloud training wrapper
│
├── GCP Deployment (7 files)
│   ├── gcp-complete-deployment.ps1        # All-in-one deployment (ACTIVE)
│   ├── gcp-phase1-setup.ps1               # Project setup (OBSOLETE - use complete)
│   ├── gcp-phase2-create-vm.ps1           # VM creation (OBSOLETE - use complete)
│   ├── gcp-phase3-verify-vm.ps1           # VM verification (OBSOLETE - use complete)
│   ├── gcp-phase4-transfer-files.ps1      # File transfer (OBSOLETE - use complete)
│   ├── gcp-phase4a-upload-models-to-gcs.ps1  # GCS upload (OBSOLETE - use complete)
│   ├── gcp-phase4b-deploy-with-gcs-models.ps1  # GCS-based deploy (OBSOLETE - use complete)
│   └── gcp-phase4-git-deploy.ps1          # Git-based deploy (OBSOLETE - use complete)
│
├── Docker Operations (4 files)
│   ├── docker-compose-up.ps1              # Docker Compose wrapper
│   ├── docker-deploy.ps1                  # Docker build & deploy
│   ├── rebuild_ui_docker.ps1/.sh          # UI Docker rebuild
│
├── Streamlit UI (3 files)
│   ├── run_streamlit_local.ps1/.sh        # Local Streamlit launcher
│   └── gcp-deploy-ui.ps1                  # GCP UI deployment
│
├── Toxicity Model (3 files)
│   ├── run_toxicity_training.ps1          # Toxicity model training
│   ├── test_toxicity_model.py             # Model testing
│   └── test_toxicity_api.py               # API testing
│
├── Testing & Validation (6 files)
│   ├── test-fullstack-local.ps1           # Full stack local test
│   ├── test_docker_ui.ps1                 # Docker UI test
│   ├── test_docker_toxicity.ps1           # Docker toxicity test
│   └── test_phase3.ps1                    # Phase 3 verification
│
└── Batch Operations (1 file)
    └── train_all_models.ps1               # Train all models sequentially

Total: 38 scripts (23 PowerShell, 9 Bash, 6 Python)
```

---

## Script Categories

### 1. Core Utilities

#### `check_models.py` ✅ ACTIVE
**Purpose**: Diagnostic tool to verify model availability in local or Docker environments.

**Features**:
- Detects Docker vs local environment
- Checks for baseline models (Logistic Regression, Linear SVM)
- Verifies transformer model files (config.json, pytorch_model.bin, tokenizer, vocab, labels)
- Reports file sizes and missing files
- Returns exit code 0 if models found, 1 if missing

**Usage**:
```bash
python scripts/check_models.py
```

**Use Cases**:
- Debugging Docker model loading issues
- Pre-deployment verification
- CI/CD pipeline checks

---

#### `client_example.py` ✅ ACTIVE
**Purpose**: Basic API client for testing single-model predictions.

**Features**:
- Health check endpoint testing
- Prediction requests with timing
- Example text classification
- Summary statistics (avg inference time, label distribution)

**Usage**:
```bash
python scripts/client_example.py
```

**Endpoints Tested**:
- `GET /health` - Model status
- `POST /predict` - Text classification

**Example Output**:
```
Predicted Label: Hate Speech
Confidence: 0.9234 (92.34%)
Inference Time: 45.23 ms
```

---

#### `client_multimodel_example.py` ✅ ACTIVE
**Purpose**: Advanced client for comparing all models (DistilBERT, Logistic Regression, Linear SVM).

**Features**:
- Lists all available models
- Switches between models dynamically
- Compares performance across models
- Calculates speedup ratios
- Interactive testing mode

**Usage**:
```bash
python scripts/client_multimodel_example.py
```

**Endpoints Tested**:
- `GET /models` - List models
- `POST /models/switch` - Switch model
- `POST /predict` - Predictions with each model

**Output**:
- Model comparison table
- Latency benchmarks
- Speed rankings
- Recommendations

**Note**: Hardcoded to GCP IP `35.232.76.140:8000` (line 17) - update for local testing.

---

#### `download_dataset.py` ✅ ACTIVE
**Purpose**: Download and prepare datasets for training.

**Supported Datasets**:
1. **hate_speech** - Binary classification (hate/offensive vs normal)
   - Source: HuggingFace `hate_speech_offensive`
   - Output: `data/hate_speech/dataset.csv`
   - Converts 3-class to binary (0/1/2 → 0/1)

2. **toxicity** - Multi-label classification (6 toxicity types)
   - Source: HuggingFace `jigsaw_toxicity_pred`
   - Output: `data/toxicity/train.csv`, `test.csv`
   - Labels: toxic, severe_toxic, obscene, threat, insult, identity_hate

**Usage**:
```bash
# Download hate speech dataset
python scripts/download_dataset.py --dataset hate_speech

# Download toxicity dataset
python scripts/download_dataset.py --dataset toxicity

# Download both
python scripts/download_dataset.py --dataset both
```

**Fallback**: Creates sample toxicity dataset if HuggingFace download fails.

---

#### `docker_entrypoint.sh` ✅ ACTIVE
**Purpose**: Docker entrypoint for Streamlit UI container.

**Workflow**:
1. Runs `check_models.py` to verify models exist
2. Starts Streamlit on port 8501
3. Configures headless mode and disables telemetry

**Usage**: Automatically called by Dockerfile.streamlit

---

### 2. Local Training Scripts

#### `run_preprocess_local.ps1` / `.sh` ✅ ACTIVE
**Purpose**: Execute data preprocessing pipeline.

**What It Does**:
- Runs `python -m src.data.preprocess`
- Creates train/val/test splits
- Saves to `data/processed/`

**Usage**:
```powershell
# Windows
.\scripts\run_preprocess_local.ps1

# Linux/Mac
./scripts/run_preprocess_local.sh
```

**Alternative**: Use root-level `run_preprocess.py` for cross-platform execution.

---

#### `run_baselines_local.ps1` / `.sh` ✅ ACTIVE
**Purpose**: Train TF-IDF + classical ML models.

**What It Does**:
- Runs `python -m src.models.train_baselines`
- Trains Logistic Regression and Linear SVM
- Saves models to `models/baselines/`

**Training Time**: <5 minutes

**Usage**:
```powershell
# Windows
.\scripts\run_baselines_local.ps1

# Linux/Mac
./scripts/run_baselines_local.sh
```

**Alternative**: Use root-level `run_baselines.py`.

---

#### `run_transformer_local.ps1` / `.sh` ✅ ACTIVE
**Purpose**: Train DistilBERT with local configuration (3 epochs).

**What It Does**:
- Runs `python -m src.models.transformer_training`
- Uses `config/config_transformer.yaml`
- Saves to `models/transformer/distilbert/`

**Training Time**: 1-2 hours (CPU), 15-25 min (GPU)

**Usage**:
```powershell
# Windows
.\scripts\run_transformer_local.ps1

# Linux/Mac
./scripts/run_transformer_local.sh
```

**Alternative**: Use root-level `run_transformer.py`.

---

### 3. API & Serving

#### `run_api_local.ps1` / `.sh` ✅ ACTIVE
**Purpose**: Start FastAPI server for local development.

**What It Does**:
- Runs `uvicorn src.api.server:app`
- Enables hot-reload (`--reload`)
- Binds to `0.0.0.0:8000`

**Endpoints Available**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Usage**:
```powershell
# Windows
.\scripts\run_api_local.ps1

# Linux/Mac
./scripts/run_api_local.sh
```

---

### 4. Cloud Training Scripts

#### `setup_gcp_training.sh` ✅ ACTIVE
**Purpose**: One-time setup for GCP GPU VM training environment.

**What It Does**:
1. Updates system packages
2. Installs Python 3.11
3. Installs CUDA toolkit (if GPU detected)
4. Clones repository
5. Creates virtual environment
6. Installs PyTorch with CUDA support
7. Installs project requirements
8. Downloads and preprocesses dataset

**Usage**:
```bash
# On GCP VM
bash scripts/setup_gcp_training.sh
```

**Time**: 10-15 minutes

**Note**: Hardcoded GitHub URL (line 54) - update with your repo.

---

#### `run_gcp_training.sh` ✅ ACTIVE
**Purpose**: Execute transformer training on GCP GPU VM.

**What It Does**:
- Activates virtual environment
- Checks GPU availability
- Sets performance environment variables
- Runs training with cloud config
- Logs output to `training.log`
- Optionally uploads to GCS (commented out)

**Usage**:
```bash
# Default (cloud config)
./scripts/run_gcp_training.sh

# Custom config
./scripts/run_gcp_training.sh config/custom.yaml cloud models/output
```

**Training Time**: 20-40 min (T4), 15-25 min (V100)

---

#### `run_transformer_cloud.ps1` ✅ ACTIVE
**Purpose**: Windows wrapper for cloud training (local testing or Windows VMs).

**Features**:
- CLI arguments for config, mode, epochs, batch size, FP16
- Virtual environment activation
- GPU detection
- Training info display

**Usage**:
```powershell
.\scripts\run_transformer_cloud.ps1 -Fp16 -Epochs 10 -BatchSize 64
```

---

### 5. GCP Deployment Scripts

#### `gcp-complete-deployment.ps1` ✅ ACTIVE - PRIMARY DEPLOYMENT SCRIPT
**Purpose**: All-in-one GCP deployment from scratch.

**What It Does** (697 lines):
1. Reads model prefix from `MODEL_VERSION.json`
2. Creates GCS bucket for models
3. Uploads models to GCS (with version checking to skip if unchanged)
4. Verifies/creates VM
5. Clones repository on VM via git
6. Downloads models from GCS to VM
7. Builds Docker image
8. Runs container
9. Tests API endpoints

**Key Features**:
- Intelligent model versioning (skips upload if version matches)
- Automatic username-based prefixes
- `-NoCheckpoints` flag (reduces upload from 12GB to 770MB)
- `-SkipModelUpload` flag
- `-SkipVMCreation` flag
- Comprehensive error handling with fail-fast
- Success validation at each step

**Usage**:
```powershell
# Recommended: Optimized upload
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Full upload with checkpoints
.\scripts\gcp-complete-deployment.ps1

# Skip model upload (use existing)
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

**Time**: 22-25 minutes (with -NoCheckpoints)

**Status**: ✅ PRODUCTION READY - Successfully deployed to 35.232.76.140

---

#### 🗑️ OBSOLETE GCP Scripts (Use `gcp-complete-deployment.ps1` instead)

The following scripts were part of the original phased deployment approach but have been superseded by the all-in-one script:

##### `gcp-phase1-setup.ps1` ⚠️ OBSOLETE
**Original Purpose**: GCP project setup (enable APIs, create static IP).
**Replacement**: Phase 1 of `gcp-complete-deployment.ps1`
**Status**: Keep for reference, but use complete script for new deployments.

##### `gcp-phase2-create-vm.ps1` ⚠️ OBSOLETE
**Original Purpose**: Create VM with firewall rules.
**Replacement**: Phase 2-3 of `gcp-complete-deployment.ps1`
**Status**: Keep for reference, but use complete script.

##### `gcp-phase3-verify-vm.ps1` ⚠️ OBSOLETE
**Original Purpose**: Verify VM environment (Docker, resources).
**Replacement**: Integrated into `gcp-complete-deployment.ps1`
**Status**: Keep for reference.

##### `gcp-phase4-transfer-files.ps1` ⚠️ OBSOLETE
**Original Purpose**: Transfer files via `gcloud compute scp`.
**Replacement**: Git-based deployment in `gcp-complete-deployment.ps1`
**Status**: Deprecated - git clone is faster and more reliable.
**Reason**: SCP was slow (15-20 min for 12GB), git + GCS is faster (2-3 min).

##### `gcp-phase4a-upload-models-to-gcs.ps1` ⚠️ OBSOLETE
**Original Purpose**: Upload models to GCS.
**Replacement**: Phase 1-2 of `gcp-complete-deployment.ps1`
**Status**: Functionality merged into complete script.

##### `gcp-phase4b-deploy-with-gcs-models.ps1` ⚠️ OBSOLETE
**Original Purpose**: Deploy using GCS-stored models.
**Replacement**: Phase 4-8 of `gcp-complete-deployment.ps1`
**Status**: Functionality merged into complete script.

##### `gcp-phase4-git-deploy.ps1` ⚠️ OBSOLETE
**Original Purpose**: Git-based deployment approach.
**Replacement**: Integrated into `gcp-complete-deployment.ps1`
**Status**: Functionality merged into complete script.

**Recommendation**: Archive these 7 phase scripts to `scripts/-archived-/` or `scripts/-obsolete-/` directory.

---

### 6. Docker Operations

#### `docker-compose-up.ps1` ✅ ACTIVE
**Purpose**: PowerShell wrapper for Docker Compose operations.

**Features**:
- Builds and starts services
- Shows logs
- Handles cleanup
- Error reporting

**Usage**:
```powershell
.\scripts\docker-compose-up.ps1
```

---

#### `docker-deploy.ps1` ✅ ACTIVE
**Purpose**: Build and deploy Docker image locally.

**What It Does**:
- Builds `cloud-nlp-classifier` image
- Stops/removes existing container
- Starts new container
- Tests health endpoint

**Usage**:
```powershell
.\scripts\docker-deploy.ps1
```

---

#### `rebuild_ui_docker.ps1` / `.sh` ✅ ACTIVE
**Purpose**: Rebuild Streamlit UI Docker image.

**What It Does**:
- Builds `cloud-nlp-ui` image
- Uses `Dockerfile.streamlit`

**Usage**:
```powershell
# Windows
.\scripts\rebuild_ui_docker.ps1

# Linux/Mac
./scripts/rebuild_ui_docker.sh
```

---

### 7. Streamlit UI Scripts

#### `run_streamlit_local.ps1` / `.sh` ✅ ACTIVE
**Purpose**: Start Streamlit UI locally.

**What It Does**:
- Runs `streamlit run src/ui/streamlit_app.py`
- Configures port 8501
- Disables telemetry

**Usage**:
```powershell
# Windows
.\scripts\run_streamlit_local.ps1

# Linux/Mac
./scripts/run_streamlit_local.sh
```

**Access**: http://localhost:8501

---

#### `gcp-deploy-ui.ps1` ✅ ACTIVE
**Purpose**: Deploy Streamlit UI to GCP VM.

**What It Does**:
- Builds UI Docker image on VM
- Runs container on port 8501
- Configures firewall

**Usage**:
```powershell
.\scripts\gcp-deploy-ui.ps1
```

---

### 8. Toxicity Model Scripts

#### `run_toxicity_training.ps1` ✅ ACTIVE
**Purpose**: Train multi-label toxicity model.

**What It Does**:
- Runs `python -m src.models.train_toxicity`
- Uses `config/config_toxicity.yaml`
- Saves to `models/toxicity_multi_head/`

**Usage**:
```powershell
.\scripts\run_toxicity_training.ps1
```

---

#### `test_toxicity_model.py` ✅ ACTIVE
**Purpose**: Test toxicity model inference.

**Features**:
- Loads model from `models/toxicity_multi_head/`
- Tests sample texts
- Reports multi-label predictions

**Usage**:
```bash
python scripts/test_toxicity_model.py
```

---

#### `test_toxicity_api.py` ✅ ACTIVE
**Purpose**: Test toxicity API endpoint.

**Features**:
- Tests `/predict` with toxicity model
- Validates multi-label output
- Checks all 6 toxicity categories

**Usage**:
```bash
python scripts/test_toxicity_api.py
```

---

### 9. Testing & Validation

#### `test-fullstack-local.ps1` ✅ ACTIVE
**Purpose**: Test full stack locally (API + UI).

**What It Does**:
- Starts API server
- Starts Streamlit UI
- Tests both services
- Cleanup on exit

**Usage**:
```powershell
.\scripts\test-fullstack-local.ps1
```

---

#### `test_docker_ui.ps1` ✅ ACTIVE
**Purpose**: Test Streamlit UI in Docker.

**What It Does**:
- Builds UI image
- Runs container
- Tests health
- Shows logs

**Usage**:
```powershell
.\scripts\test_docker_ui.ps1
```

---

#### `test_docker_toxicity.ps1` ✅ ACTIVE
**Purpose**: Test toxicity model in Docker.

**What It Does**:
- Builds image with toxicity model
- Tests predictions
- Validates multi-label output

**Usage**:
```powershell
.\scripts\test_docker_toxicity.ps1
```

---

#### `test_phase3.ps1` ⚠️ OBSOLETE
**Original Purpose**: Test Phase 3 of phased deployment (model loading, inference, metrics validation).

**What It Did**:
- Ran `tests/test_model_loading.py`
- Ran `tests/test_inference.py`
- Ran `tests/test_metrics.py`
- Provided pass/fail summary

**Status**: Obsolete - These tests are now covered by the comprehensive test suite in `tests/` directory and can be run via `python run_tests.py` or `pytest tests/`.

**Replacement**: Use `pytest tests/` or `python run_tests.py` for comprehensive testing.

**Recommendation**: Archive to `scripts/-archived-phased-deployment/`

---

### 10. Batch Operations

#### `train_all_models.ps1` ✅ ACTIVE
**Purpose**: Train all models sequentially (baselines + transformer + toxicity).

**What It Does**:
1. Runs preprocessing
2. Trains baseline models
3. Trains transformer model
4. Trains toxicity model
5. Generates summary report

**Usage**:
```powershell
.\scripts\train_all_models.ps1
```

**Time**: 2-3 hours (CPU), 30-45 min (GPU)

---

## Script Status Summary

### ✅ Active Scripts (30 scripts)
Scripts currently in use and maintained:

**Core Utilities (5)**:
- check_models.py
- client_example.py
- client_multimodel_example.py
- download_dataset.py
- docker_entrypoint.sh

**Training (9)**:
- run_preprocess_local.ps1/.sh
- run_baselines_local.ps1/.sh
- run_transformer_local.ps1/.sh
- run_transformer_cloud.ps1
- run_gcp_training.sh
- setup_gcp_training.sh

**API & Serving (2)**:
- run_api_local.ps1/.sh

**Deployment (2)**:
- gcp-complete-deployment.ps1 ⭐ PRIMARY
- gcp-deploy-ui.ps1

**Docker (4)**:
- docker-compose-up.ps1
- docker-deploy.ps1
- rebuild_ui_docker.ps1/.sh

**Streamlit (2)**:
- run_streamlit_local.ps1/.sh

**Toxicity (3)**:
- run_toxicity_training.ps1
- test_toxicity_model.py
- test_toxicity_api.py

**Testing (2)**:
- test-fullstack-local.ps1
- test_docker_ui.ps1
- test_docker_toxicity.ps1

**Batch (1)**:
- train_all_models.ps1

---

### ⚠️ Obsolete Scripts (8 scripts)
Scripts superseded by newer implementations:

1. `gcp-phase1-setup.ps1` - Use `gcp-complete-deployment.ps1`
2. `gcp-phase2-create-vm.ps1` - Use `gcp-complete-deployment.ps1`
3. `gcp-phase3-verify-vm.ps1` - Use `gcp-complete-deployment.ps1`
4. `gcp-phase4-transfer-files.ps1` - Replaced by git clone in complete deployment
5. `gcp-phase4a-upload-models-to-gcs.ps1` - Merged into complete deployment
6. `gcp-phase4b-deploy-with-gcs-models.ps1` - Merged into complete deployment
7. `gcp-phase4-git-deploy.ps1` - Merged into complete deployment
8. `test_phase3.ps1` - Use `pytest tests/` or `python run_tests.py`

**Recommendation**: Move to `scripts/-archived-phased-deployment/` directory.

---

## Usage Patterns

### Local Development Workflow
```powershell
# 1. Download dataset
python scripts/download_dataset.py

# 2. Preprocess data
.\scripts\run_preprocess_local.ps1

# 3. Train models
.\scripts\run_baselines_local.ps1
.\scripts\run_transformer_local.ps1

# 4. Start API
.\scripts\run_api_local.ps1

# 5. Test API
python scripts/client_example.py
```

### Cloud Training Workflow
```bash
# On GCP VM
# 1. Setup environment (once)
bash scripts/setup_gcp_training.sh

# 2. Train model
bash scripts/run_gcp_training.sh

# 3. Download model (from local machine)
gcloud compute scp --recurse \
  nlp-training-vm:~/CLOUD-NLP-CLASSIFIER-GCP/models/transformer/distilbert_cloud \
  ./models/transformer/
```

### Cloud Deployment Workflow
```powershell
# All-in-one deployment
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Test deployed API
python scripts/client_multimodel_example.py
```

### Docker Workflow
```powershell
# Build and run locally
.\scripts\docker-deploy.ps1

# Test
python scripts/client_example.py
```

---

## Cross-Platform Compatibility

### PowerShell Scripts (`.ps1`)
- **Platform**: Windows
- **Execution Policy**: May need `Set-ExecutionPolicy RemoteSigned`
- **Features**: Colored output, error handling, exit codes

### Bash Scripts (`.sh`)
- **Platform**: Linux, Mac, WSL
- **Permissions**: Requires `chmod +x scripts/*.sh`
- **Features**: `set -e` for fail-fast, POSIX compliant

### Python Scripts (`.py`)
- **Platform**: All (Windows, Linux, Mac)
- **Recommended**: Use Python scripts for maximum portability
- **Alternative**: Root-level Python wrappers (`run_*.py`) avoid shell scripts

---

## Key Configuration Points

### Hardcoded Values to Update

1. **GitHub Repository** (`setup_gcp_training.sh` line 54):
   ```bash
   git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
   ```

2. **GCP IP Address** (`client_multimodel_example.py` line 17):
   ```python
   BASE_URL = "http://35.232.76.140:8000"
   ```

3. **GCP Project** (`gcp-complete-deployment.ps1` line 16):
   ```powershell
   [string]$ProjectId = "mnist-k8s-pipeline"
   ```

4. **Git Branch** (`gcp-complete-deployment.ps1` line 22):
   ```powershell
   [string]$Branch = "dhairya/gcp-public-deployment"
   ```

---

## Best Practices

### 1. Use Root-Level Python Wrappers
Prefer `run_preprocess.py`, `run_baselines.py`, `run_transformer.py` over shell scripts for cross-platform compatibility.

### 2. Use Complete Deployment Script
For GCP deployment, always use `gcp-complete-deployment.ps1` with `-NoCheckpoints` flag.

### 3. Virtual Environment
Always activate virtual environment before running scripts:
```powershell
# Windows
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 4. Check Models Before Deployment
```bash
python scripts/check_models.py
```

### 5. Test Locally Before Cloud
Test Docker images locally before deploying to GCP:
```powershell
.\scripts\docker-deploy.ps1
python scripts/client_example.py
```

---

## Troubleshooting

### Issue: Script Won't Execute (PowerShell)
**Solution**: Set execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Script Won't Execute (Bash)
**Solution**: Add execute permissions
```bash
chmod +x scripts/*.sh
```

### Issue: Model Not Found
**Solution**: Run check script
```bash
python scripts/check_models.py
```

### Issue: GCP Deployment Fails
**Solution**: Check logs, verify:
- GCP credentials (`gcloud auth list`)
- Project ID (`gcloud config get-value project`)
- VM status (`gcloud compute instances list`)

### Issue: Docker Build Fails
**Solution**: Check disk space, Docker daemon status, and model files exist.

---

## Cleanup Recommendations

### Archive Obsolete Scripts
```powershell
# Create archive directory
New-Item -ItemType Directory -Path "scripts/-archived-phased-deployment"

# Move obsolete scripts
Move-Item "scripts/gcp-phase*.ps1" "scripts/-archived-phased-deployment/"
```

### Update Documentation
After archiving, update:
- README.md (remove references to phased scripts)
- SETUP AND RUN NOW.md (use complete deployment only)

---

## Summary

The `scripts/` directory provides:
- **30 active scripts** for all ML pipeline operations
- **8 obsolete scripts** (phased deployment + old tests - archive recommended)
- **Cross-platform support** (PowerShell, Bash, Python)
- **Complete automation** from data download to cloud deployment
- **Production-ready** deployment via `gcp-complete-deployment.ps1`

**Primary Scripts**:
- Training: `run_baselines.py`, `run_transformer.py` (root level)
- Deployment: `gcp-complete-deployment.ps1` (scripts/)
- Testing: `client_multimodel_example.py` (scripts/)

All scripts integrate with the configuration system (`config/`), model storage (`models/`), and API server (`src/api/`).
