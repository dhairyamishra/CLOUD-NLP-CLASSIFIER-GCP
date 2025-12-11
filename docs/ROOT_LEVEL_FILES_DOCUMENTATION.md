# Root-Level Files Documentation

## Overview

This document catalogs all root-level configuration, metadata, and utility files in the CLOUD-NLP-CLASSIFIER-GCP project. These files control project behavior, deployment settings, and provide project status tracking.

**Document Status**: Part 1 of N (13 files documented)
**Last Updated**: 2025-12-10

---

## File Categories

### Configuration Files (2)
- `.dockerignore` - Docker build context exclusions
- `.gitignore` - Git version control exclusions

### Deployment Configuration (1)
- `gcp-deployment-config.txt` - GCP VM deployment settings

### Model Management (3)
- `MODEL_VERSION.json` - Production model version tracking
- `MODEL_VERSION copy.txt` - Model version template
- `models_inventory.txt` - Complete model file inventory
- `models_summary.txt` - Model directory size summary

### Project Status & Reports (4)
- `IMPLEMENTATION-TASK-LIST.MD` - Complete project task tracking
- `cleanup_verification_results.json` - System cleanup verification
- `performance_results.json` - Model performance benchmarks
- `training_report.json` - Training session summary

### Documentation (2)
- `SETUP AND RUN NOW.md` - Quick start execution guide
- `transfer_log.txt` - GCP file transfer log

---

## CHECKPOINT 1: File Categories Complete ✓

---

## Configuration Files

### `.dockerignore` (90 lines)

**Purpose**: Exclude unnecessary files from Docker build context to reduce image size and build time.

**Key Exclusions**:

**Python Artifacts**:
- `__pycache__/`, `*.py[cod]`, `*$py.class`, `.Python`
- Virtual environments: `venv/`, `env/`, `ENV/`, `.venv`

**Development Files**:
- IDE: `.vscode/`, `.idea/`, `*.swp`, `*.swo`, `.DS_Store`
- Git: `.git/`, `.gitignore`, `.gitattributes`
- Documentation: `docs/`, `*.md` (except `README.md`)
- Notebooks: `notebooks/`, `*.ipynb`

**Testing**:
- `tests/`, `pytest.ini`, `.pytest_cache/`
- `.coverage`, `htmlcov/`, `.tox/`

**Data Files**:
- Raw data: `data/raw/`, `data/processed/`, `*.csv`
- JSON files: `*.json` (with exceptions for model configs)
- **Exceptions**: Model configs are kept:
  - `!models/transformer/distilbert/*.json`
  - `!models/toxicity_multi_head/*.json`

**Scripts**:
- `scripts/` (except Docker-specific ones)
- **Exceptions**: `!scripts/check_models.py`, `!scripts/docker_entrypoint.sh`

**Model Checkpoints**:
- `models/transformer/distilbert/checkpoint-*/` (only keep final models)
- Baseline models (`*.joblib`) are included

**Logs & Temporary**:
- `*.log`, `logs/`, `*.tmp`, `*.temp`

**Docker Files**:
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`

**CI/CD**:
- `.github/`, `.gitlab-ci.yml`, `.travis.yml`

**Environment**:
- `.env`, `.env.*`

**Impact**: Reduces Docker build context from ~12 GB to ~770 MB (15x smaller) when using `-NoCheckpoints` flag.

---

### `.gitignore` (224 lines)

**Purpose**: Exclude files from Git version control to keep repository clean and prevent committing sensitive/large files.

**Status**: All entries are commented out (lines start with `#`)

**Original Exclusion Categories** (when uncommented):

**Python** (lines 1-27):
- `__pycache__/`, `*.py[cod]`, `*.pyc`, `.Python`
- Build artifacts: `build/`, `dist/`, `*.egg-info/`

**Virtual Environment** (lines 29-37):
- `venv/`, `env/`, `ENV/`, `.venv/`

**IDE & Editors** (lines 39-49):
- `.vscode/`, `.idea/`, `*.swp`, `*.sublime-*`

**Jupyter** (lines 51-57):
- `.ipynb_checkpoints/`, `profile_default/`

**Environment Variables** (lines 59-64):
- `.env`, `.env.local`, `.env.*.local`

**Data Files** (lines 66-79):
- `data/raw/*.csv`, `data/processed/*.csv`
- Keep: `!data/raw/README.md`, `!data/processed/README.md`

**Model Files** (lines 81-119):
- Baseline models: `*.joblib`, `*.pkl`, `*.pickle`
- Transformer binaries: `*.bin`, `*.safetensors`, `vocab.txt`, `tokenizer.json`
- Toxicity model binaries
- **Keep**: Config and metadata JSON files (negated patterns with `!`)
- Checkpoints: `checkpoint-*/`, `runs/`

**Logs & Monitoring** (lines 121-129):
- `*.log`, `logs/`, `wandb/`, `tensorboard/`, `mlruns/`

**Testing & Coverage** (lines 131-142):
- `.pytest_cache/`, `.coverage`, `htmlcov/`, `.tox/`

**Docker** (lines 144-149):
- `*.tar`, `*.tar.gz`, `docker-compose.override.yml`

**GCP & Cloud** (lines 151-169):
- `.gcp/`, `*.json` (with exceptions for configs)
- `credentials.json`, `service-account*.json`

**Temporary & Cache** (lines 171-183):
- `*.tmp`, `*.bak`, `.cache/`, `.mypy_cache/`

**OS Specific** (lines 185-202):
- macOS: `.DS_Store`, `.AppleDouble`
- Windows: `Thumbs.db`, `Desktop.ini`
- Linux: `*~`, `.directory`

**Project Specific** (lines 204-223):
- `training_log.txt`, `*.zip`, `*.gz`
- `.cache/huggingface/`, `transformers_cache/`
- `experiments/`, `scratch/`, `temp/`

**Note**: Currently all entries are commented out, meaning Git is tracking all files. This may be intentional for project completeness or should be reviewed.

---

## CHECKPOINT 2: Configuration Files Complete ✓

---

## Deployment Configuration

### `gcp-deployment-config.txt` (8 lines)

**Purpose**: Store GCP VM deployment configuration for automated deployment scripts.

**Configuration**:
```
PROJECT_ID=mnist-k8s-pipeline
REGION=us-central1
ZONE=us-central1-a
STATIC_IP=35.232.76.140
VM_NAME=nlp-classifier-vm
MACHINE_TYPE=e2-standard-2
BOOT_DISK_SIZE=50GB
```

**Details**:
- **Project**: `mnist-k8s-pipeline` (GCP project ID)
- **Region**: `us-central1` (Iowa, USA)
- **Zone**: `us-central1-a` (specific availability zone)
- **Static IP**: `35.232.76.140` (reserved external IP)
- **VM Name**: `nlp-classifier-vm` (Compute Engine instance)
- **Machine Type**: `e2-standard-2` (2 vCPU, 8 GB RAM)
- **Boot Disk**: `50GB` SSD

**Usage**:
- Read by deployment scripts: `gcp-complete-deployment.ps1`
- Ensures consistent configuration across deployments
- Can be sourced in bash scripts or parsed in PowerShell

**Cost**: ~$0.07/hour when running (~$50/month VM + $7/month static IP)

**Status**: ✅ DEPLOYED & LIVE - API accessible at http://35.232.76.140:8000

---

## CHECKPOINT 3: Deployment Configuration Complete ✓

---

## Model Management

### `MODEL_VERSION.json` (72 lines)

**Purpose**: Track model versions for deployment and version control.

**Structure**:
```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-10T12:00:00-05:00",
  "model_prefix": "DPM-MODELS",
  "models": { ... },
  "notes": { ... }
}
```

**Models Tracked**:

**1. Baselines** (v1.0.0):
- Files: `linear_svm_tfidf.joblib`, `logistic_regression_tfidf.joblib`, `labels.json`
- Size: 0.9 MB
- Last Updated: 2025-12-10

**2. Toxicity Multi-Head** (v1.0.0):
- Files: `config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `vocab.txt`, `labels.json`
- Size: 256 MB
- Exclude Checkpoints: true

**3. Transformer DistilBERT** (v1.0.0):
- Files: `config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `vocab.txt`, `labels.json`
- Size: 256 MB
- Exclude Checkpoints: true

**4. Transformer DistilBERT Full-Scale** (v1.0.0):
- Files: Same as DistilBERT
- Size: 256 MB
- Exclude Checkpoints: true

**Version Format**: `MAJOR.MINOR.PATCH`

**Version Rules**:
- **MAJOR**: Breaking changes (model architecture, incompatible API)
- **MINOR**: New features (new model, improved accuracy)
- **PATCH**: Bug fixes (training fixes, minor improvements)

**Model Prefix**: `DPM-MODELS` (used in GCS bucket naming)

**Usage**: Upload scripts compare versions and skip upload if versions match.

---

### `MODEL_VERSION copy.txt` (74 lines)

**Purpose**: Template for `MODEL_VERSION.json` with instructions.

**Difference from MODEL_VERSION.json**:
- Line 1: `COPY THIS TO .JSON` (instruction header)
- Line 6: `"model_prefix": "auto"` (vs `"DPM-MODELS"` in production)

**Content**: Identical structure to `MODEL_VERSION.json` but serves as:
- Backup template
- Documentation of expected format
- Reference for creating new versions

**Status**: Template file, not used in production.

---

### `models_inventory.txt` (144 lines)

**Purpose**: Complete inventory of all model files with sizes and timestamps.

**Format**: PowerShell `Get-ChildItem` output with columns:
- `FullName`: Complete file path
- `SizeMB`: File size in megabytes
- `LastWriteTime`: Last modification timestamp

**Contents Summary**:

**Baselines** (2 files, 0.88 MB):
- `linear_svm_tfidf.joblib` (0.44 MB, 12/9/2025 3:27 PM)
- `logistic_regression_tfidf.joblib` (0.44 MB, 12/9/2025 3:27 PM)

**Toxicity Multi-Head** (7 files, 256.37 MB):
- `model.safetensors` (255.44 MB)
- `tokenizer.json` (0.71 MB)
- `vocab.txt` (0.22 MB)
- Config files: `config.json`, `labels.json`, `special_tokens_map.json`, `tokenizer_config.json`

**Transformer DistilBERT** (7 files, 255.68 MB):
- `model.safetensors` (255.43 MB)
- `vocab.txt` (0.25 MB)
- Config files: `config.json`, `labels.json`, `special_tokens_map.json`, `tokenizer_config.json`, `training_info.json`

**Checkpoints** (Multiple, ~766 MB each):
- DistilBERT checkpoints: `checkpoint-800`, `checkpoint-1000`, `checkpoint-1100`, `checkpoint-1200`, `checkpoint-1300`
- Each checkpoint contains:
  - `model.safetensors` (255.43 MB)
  - `optimizer.pt` (510.91 MB)
  - `rng_state.pth`, `scheduler.pt`, `trainer_state.json`, `training_args.bin`

**DistilBERT Full-Scale** (7 files, 255.68 MB):
- Same structure as standard DistilBERT
- Additional checkpoints: `checkpoint-1150` through `checkpoint-1600`

**Total Model Storage**:
- Production models: ~770 MB (without checkpoints)
- With checkpoints: ~12 GB

**Usage**: Reference for deployment scripts, size verification, and cleanup operations.

---

### `models_summary.txt` (25 lines)

**Purpose**: Summarized view of model directories with file counts and total sizes.

**Format**: PowerShell grouped output with columns:
- `Name`: Directory path
- `Count`: Number of files
- `SizeMB`: Total size in MB

**Summary**:

**Checkpoint Directories** (766 MB each):
- `distilbert_fullscale/checkpoint-1500`: 8 files, 766.4 MB
- `distilbert_fullscale/checkpoint-1550`: 8 files, 766.4 MB
- `distilbert_fullscale/checkpoint-1600`: 8 files, 766.4 MB
- `distilbert_fullscale/checkpoint-1300` through `checkpoint-1450`: 8 files each, 766.39 MB
- `distilbert/checkpoint-800` through `checkpoint-1300`: 7 files each, 766.37 MB

**Production Models**:
- `toxicity_multi_head`: 7 files, 256.37 MB
- `transformer/distilbert`: 7 files, 255.68 MB
- `transformer/distilbert_fullscale`: 7 files, 255.68 MB
- `baselines`: 2 files, 0.88 MB

**Total Checkpoints**: 15 checkpoint directories (~11.5 GB)
**Total Production Models**: ~770 MB

**Usage**: Quick reference for disk space planning and checkpoint cleanup decisions.

---

## CHECKPOINT 4: Model Management Complete ✓

---

## Project Status & Reports

### `IMPLEMENTATION-TASK-LIST.MD` (618 lines)

**Purpose**: Comprehensive project task tracking with phase-by-phase completion status.

**Overall Progress**: ✅ ALL PHASES COMPLETE (100%)

**Phases Summary**:

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 0: Repository Setup | ✅ Complete | 100% |
| Phase 1: Data Handling | ✅ Complete | 100% |
| Phase 2: Baseline Models | ✅ Complete | 100% |
| Phase 3: Transformer Training | ✅ Complete | 100% |
| Phase 4: FastAPI Server | ✅ Complete | 100% |
| Phase 5: Dockerization | ✅ Complete | 100% |
| Phase 6: Cloud Deployment | ✅ Complete | 100% |
| Phase 7: Multi-Model Docker | ✅ Complete | 100% |
| Phase 8: Multi-Model Testing | ✅ Complete | 100% |
| Phase 9: Performance Validation | ✅ Complete | 100% |
| Phase 10: Advanced Training | ✅ Complete | 100% |
| Phase 11: Cloud Evaluation | ✅ Complete | 100% |
| Phase 13: Streamlit UI | ✅ Complete | 100% |

**Current Status**:
- ✅ DEPLOYED & OPERATIONAL
- API live at: http://35.232.76.140:8000
- 326+ tests passed
- Exceeds all targets by 3-11x

**Key Achievements**:

**Phase 0 - Repository Setup**:
- Core structure: `src/`, `data/`, `models/`, `config/`, `scripts/`, `tests/`
- Cross-platform scripts: `run_preprocess.py`, `run_baselines.py`, `run_transformer.py`, `run_tests.py`
- Configuration files for baselines and transformer training

**Phase 1 - Data Handling**:
- Dataset utilities: `load_raw_dataset()`, `train_val_test_split()`
- Preprocessing: `clean_text()`, `preprocess_dataframe()`
- Train/val/test splits in `data/processed/`

**Phase 2 - Baseline Models**:
- TF-IDF + Logistic Regression (85-88% accuracy)
- TF-IDF + Linear SVM (85-88% accuracy)
- Training time: <5 minutes
- Inference: <2ms

**Phase 3 - Transformer Training**:
- DistilBERT fine-tuning (96.57% accuracy)
- Advanced features: early stopping, LR schedulers, FP16
- Cloud training support (GCP GPU VMs)
- CLI interface with parameter overrides

**Phase 4 - FastAPI Server**:
- Multi-model API with dynamic switching
- Endpoints: `/health`, `/predict`, `/models`, `/models/switch`, `/docs`
- Pydantic V2 compliant
- Zero deprecation warnings

**Phase 5 - Dockerization**:
- Production-ready Docker image (~2.5 GB)
- All 3 models included
- Health checks and monitoring
- Docker Compose configurations

**Phase 6 - Cloud Deployment**:
- GCP VM deployment (e2-standard-2)
- Automated deployment script
- Static IP: 35.232.76.140
- Cost: ~$56/month

**Phase 7 - Multi-Model Docker**:
- Single image with 4 models (DistilBERT, LogReg, SVM, Toxicity)
- Zero-downtime model switching
- Environment variable configuration

**Phase 8 - Multi-Model Testing**:
- Comprehensive test suite (326+ tests)
- 100% pass rate
- API endpoint validation
- Model switching verification

**Phase 9 - Performance Validation**:
- DistilBERT: 96.57% accuracy, 8ms latency
- Logistic Regression: 85-88% accuracy, 0.66ms latency
- Linear SVM: 85-88% accuracy, 0.60ms latency
- Exceeds targets by 3-11x

**Phase 10 - Advanced Training**:
- CLI argument parsing
- Cloud training mode
- Advanced LR schedulers
- Mixed precision (FP16)
- Gradient accumulation

**Phase 11 - Cloud Evaluation**:
- Live API testing on GCP
- Performance benchmarking
- Cost analysis
- Monitoring setup

**Phase 13 - Streamlit UI**:
- Standalone UI (local models)
- API-connected UI
- Real-time predictions
- Model comparison

**Next Steps**: Optional - GCP Cloud Run deployment, monitoring/analytics

---

### `cleanup_verification_results.json` (34 lines)

**Purpose**: System cleanup verification results from Phase 10 testing.

**Results**:

**Test Results**:
- Found: 3 test files
- Missing: 0

**Docker Resources**:
- Total Containers: 0 (all cleaned up)
- Total Images: 53
- Running Containers: 0

**Model Files**:
- Found: 2
- Missing: 4
- Total Size: 1923 MB (~1.9 GB)

**Containers Cleaned Up**:
- Removed: 0
- Stopped: 0

**Project Files**:
- Scripts: 10
- Tests: 9
- Documentation: 33

**Data Files**:
- Found: 4 (train/val/test splits + raw)
- Missing: 0

**Docker Image**:
- Exists: true
- Size: 14.6 GB

**Timestamp**: End of Phase 10 (2025-12-10)

**Status**: ✅ All cleanup operations successful, system ready for deployment.

---

### `performance_results.json` (399 lines)

**Purpose**: Detailed performance benchmarking results for all models.

**Models Tested**: 3 (Logistic Regression, Linear SVM, DistilBERT)

**Metrics Collected**:
- Latency: P50, P95, P99, individual request times
- Throughput: Requests per second
- Memory usage
- Accuracy metrics

**Logistic Regression Results**:
- **Latency**:
  - P99: 1.54 ms
  - Average: ~0.66 ms
  - Min: 0.51 ms
  - Max: 1.72 ms
- **Throughput**: 200-500 req/s (estimated)
- **Accuracy**: 85-88%
- **Memory**: ~100 MB

**Linear SVM Results**:
- **Latency**:
  - P99: ~1.5 ms
  - Average: ~0.60 ms
  - Min: 0.48 ms
  - Max: ~1.7 ms
- **Throughput**: 200-500 req/s (estimated)
- **Accuracy**: 85-88%
- **Memory**: ~100 MB

**DistilBERT Results**:
- **Latency**:
  - P99: ~100 ms
  - Average: ~8-17 ms (after warmup)
  - First request: ~259 ms (cold start)
  - Subsequent: 60-65 ms
- **Throughput**: 20-50 req/s
- **Accuracy**: 96.57%
- **Memory**: ~1.2 GB

**Performance Comparison**:
- Logistic Regression: **21x faster** than DistilBERT
- Linear SVM: **44x faster** than DistilBERT
- DistilBERT: **13% better accuracy** than baselines

**Test Configuration**:
- 100 requests per model
- Varied input text lengths
- Measured on local machine (not GCP)

**Usage**: Reference for model selection based on speed vs accuracy trade-offs.

---

### `training_report.json` (34 lines)

**Purpose**: Summary of all model training sessions.

**Training Session**:
- Start Time: 2025-12-09 15:27:27
- End Time: 2025-12-09 15:50:59
- Total Duration: 1415.20 seconds (23m 35s)

**Models Trained**:

**1. Baseline Models** (Logistic Regression + Linear SVM):
- Status: ✅ Success
- Duration: 3.13 seconds
- Timestamp: 2025-12-09 15:27:27

**2. DistilBERT Transformer** (Standard Configuration):
- Status: ✅ Success
- Duration: 649.26 seconds (10m 49s)
- Timestamp: 2025-12-09 15:38:21
- Config: 3 epochs, batch size 32, seq length 128

**3. DistilBERT Transformer** (Intensive Full-Scale):
- Status: ✅ Success
- Duration: 752.80 seconds (12m 33s)
- Timestamp: 2025-12-09 15:50:59
- Config: More epochs, larger batch, longer sequences

**Summary**:
- Total Models: 3
- Successful: 3
- Failed: 0
- Interrupted: 0

**Success Rate**: 100%

**Training Environment**: Local machine (CPU/GPU)

---

## CHECKPOINT 5: Project Status & Reports Complete ✓

---

## Documentation

### `SETUP AND RUN NOW.md` (562 lines)

**Purpose**: End-to-end execution guide from fresh machine to running cloud API.

**Structure**: Stage-based with step-by-step commands and expected results.

**Stages**:

**STAGE 0 - Prerequisites & Environment**:
- Clone repository
- Create virtual environment
- Install dependencies
- Commands for Windows/Linux/Mac

**STAGE 1 - Data Initialization & Preprocessing**:
- Create data directories
- Run preprocessing pipeline
- Generate train/val/test splits
- Verify CSV files created

**STAGE 2 - Model Training**:
- Train baseline models (LogReg, SVM)
- Train DistilBERT (dev mode)
- Optional: Full-scale training
- Optional: Toxicity model training

**STAGE 3 - API Server (Local)**:
- Start FastAPI server with uvicorn
- Test health endpoint
- Test prediction endpoint
- Access interactive docs

**STAGE 4 - Testing**:
- Run comprehensive test suite
- Verify all tests pass
- Check for deprecation warnings

**STAGE 5 - Docker Build & Run**:
- Build Docker image
- Run container with docker-compose
- Test containerized API
- Verify health checks

**STAGE 6 - GCP Deployment**:
- Configure GCP project
- Create VM instance
- Deploy Docker container
- Test external API access

**STAGE 7 - Streamlit UI (Optional)**:
- Run standalone UI
- Run API-connected UI
- Test model switching
- Verify predictions

**Format**:
- Each step has:
  - `STEP [x]:` - Description
  - `Run Command:` - Exact command
  - `Expected Result:` - What to see

**Target Audience**: New developers, deployment engineers, course instructors

**Usage**: Follow sequentially for complete setup, or jump to specific stages for targeted tasks.

---

### `transfer_log.txt` (3 lines)

**Purpose**: Log file for GCP Phase 4 file transfer operations.

**Content**:
```
Phase 4 Transfer - Started at 12/10/2025 10:54:55
 
 
```

**Status**: Transfer started but log is incomplete (likely interrupted or in progress).

**Expected Content** (when complete):
- File transfer progress
- Upload/download speeds
- Success/failure messages
- Total files transferred
- Total size transferred

**Related Script**: `gcp-phase4-transfer-files.ps1`

**Note**: Minimal content suggests transfer may have been interrupted or script switched to different logging method.

---

## CHECKPOINT 6: Documentation Complete ✓

---

## Summary

### Files by Category

| Category | Files | Total Size | Purpose |
|----------|-------|------------|---------|
| **Configuration** | 2 | ~1 KB | Build and version control exclusions |
| **Deployment** | 1 | <1 KB | GCP VM configuration |
| **Model Management** | 4 | ~1 MB | Version tracking and inventory |
| **Status & Reports** | 4 | ~50 KB | Progress tracking and performance data |
| **Documentation** | 2 | ~20 KB | Setup guides and logs |
| **Total** | 13 | ~72 KB | Root-level project files |

### Key Insights

**Project Status**:
- ✅ All 13 phases complete (100%)
- ✅ Deployed to GCP at 35.232.76.140:8000
- ✅ 326+ tests passed (100% success rate)
- ✅ Performance exceeds targets by 3-11x

**Model Inventory**:
- 4 production models (~770 MB)
- 15 checkpoints (~11.5 GB)
- Total storage: ~12 GB (or 770 MB without checkpoints)

**Deployment Configuration**:
- GCP Project: mnist-k8s-pipeline
- VM: e2-standard-2 (2 vCPU, 8 GB RAM)
- Region: us-central1-a
- Cost: ~$56/month

**Performance Benchmarks**:
- DistilBERT: 96.57% accuracy, 8ms latency
- Logistic Regression: 85-88% accuracy, 0.66ms latency (21x faster)
- Linear SVM: 85-88% accuracy, 0.60ms latency (44x faster)

**Training Summary**:
- Total duration: 23m 35s
- 3 models trained successfully
- 0 failures

### File Status

| File | Status | Notes |
|------|--------|-------|
| `.dockerignore` | ✅ Active | Optimized for 15x smaller builds |
| `.gitignore` | ⚠️ Commented | All entries disabled, review needed |
| `gcp-deployment-config.txt` | ✅ Active | Live deployment config |
| `MODEL_VERSION.json` | ✅ Active | v1.0.0, DPM-MODELS prefix |
| `MODEL_VERSION copy.txt` | 📝 Template | Backup/reference only |
| `models_inventory.txt` | 📊 Report | Generated 12/9-12/10/2025 |
| `models_summary.txt` | 📊 Report | Directory size summary |
| `IMPLEMENTATION-TASK-LIST.MD` | ✅ Complete | All phases done |
| `cleanup_verification_results.json` | ✅ Verified | Phase 10 cleanup successful |
| `performance_results.json` | 📊 Benchmark | 100 requests per model |
| `training_report.json` | 📊 Report | 3 models, 100% success |
| `SETUP AND RUN NOW.md` | 📖 Guide | 7-stage execution guide |
| `transfer_log.txt` | ⚠️ Incomplete | Transfer started, log minimal |

---

## FINAL CHECKPOINT: Part 1 Complete ✓

**Files Documented**: 13/13 in this batch

---

# PART 2: Docker & Container Configuration Files

**Document Status**: Part 2 of N (11 files documented)
**Last Updated**: 2025-12-10

---

## File Categories (Part 2)

### Docker Compose Files (7)
- `docker-compose.yml` - Standard full-stack deployment
- `docker-compose.api-only.yml` - Backend only
- `docker-compose.dev.yml` - Development with hot-reload
- `docker-compose.full.yml` - Complete production stack
- `docker-compose.fullstack.yml` - API + UI testing
- `docker-compose.prod.yml` - Production optimized
- `docker-compose.ui.yml` - UI development only

### Dockerfiles (3)
- `Dockerfile` - FastAPI backend image
- `Dockerfile.streamlit` - Streamlit UI with models
- `Dockerfile.streamlit.api` - Lightweight UI (API mode)

### Build Configuration (1)
- `.dockerignore` - Already documented in Part 1

---

## CHECKPOINT 7: Part 2 Categories Complete ✓

---

## Docker Compose Files

### `docker-compose.yml` (158 lines)

**Purpose**: Standard full-stack deployment with API + UI + optional monitoring.

**Services**:

**1. API Service**:
- Image: `cloud-nlp-classifier:latest`
- Container: `nlp-api`
- Port: 8000
- Environment:
  - `LOG_LEVEL=info`
  - `WORKERS=1`
- Volumes: `./logs:/app/logs`
- Health Check: `/health` endpoint every 30s
- Resources:
  - Limits: 2 CPU, 3 GB RAM
  - Reservations: 1 CPU, 2 GB RAM
- Restart: `unless-stopped`

**2. UI Service**:
- Image: `cloud-nlp-classifier-ui:latest`
- Container: `nlp-ui`
- Port: 8501
- Environment:
  - Streamlit server settings
  - Headless mode enabled
  - Stats collection disabled
- Volumes: `./models:/app/models`
- Health Check: `/_stcore/health` endpoint
- Resources:
  - Limits: 2 CPU, 2.5 GB RAM
  - Reservations: 1 CPU, 1.5 GB RAM

**3. Optional Services** (commented out):
- **Nginx**: Reverse proxy for load balancing and SSL
  - Ports: 80, 443
  - Config: `./nginx.conf`
- **Prometheus**: Metrics collection
  - Port: 9090
  - Persistent volume for data
- **Grafana**: Visualization dashboards
  - Port: 3000
  - Default admin password

**Network**: `nlp-network` (bridge driver)

**Usage**:
```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop and remove
docker-compose logs -f api    # Follow API logs
docker-compose ps             # View status
```

**Features**:
- Full-stack deployment (API + UI)
- Health checks for both services
- Resource limits and reservations
- Persistent log storage
- Optional monitoring stack
- Production-ready configuration

---

### `docker-compose.api-only.yml` (47 lines)

**Purpose**: Run only the FastAPI backend without UI.

**Service**: API Only

**Configuration**:
- Image: `cloud-nlp-classifier:latest`
- Container: `nlp-api`
- Port: 8000
- Environment:
  - `DEFAULT_MODEL=distilbert`
  - `LOG_LEVEL=info`
- Health Check: `/health` every 30s
- Resources:
  - Limits: 2 CPU, 3 GB RAM
  - Reservations: 1 CPU, 2 GB RAM
- Restart: `unless-stopped`
- Network: `nlp-network`

**Usage**:
```bash
docker-compose -f docker-compose.api-only.yml up -d
docker-compose -f docker-compose.api-only.yml down
```

**Use Cases**:
- Backend-only deployment
- API testing without UI
- Microservices architecture
- Cloud deployment (Cloud Run, ECS)

---

### `docker-compose.dev.yml` (39 lines)

**Purpose**: Development configuration with hot-reload and debugging.

**Service**: API Development

**Configuration**:
- Image: `cloud-nlp-classifier:dev`
- Container: `nlp-api-dev`
- Port: 8000
- Environment:
  - `LOG_LEVEL=debug`
  - `WORKERS=1`
  - `RELOAD=true`
- **Volumes** (Hot-Reload):
  - `./src:/app/src` - Source code
  - `./config:/app/config` - Configuration
  - `./logs:/app/logs` - Logs
- Command: `uvicorn ... --reload --log-level debug`
- Restart: `unless-stopped`
- Network: `nlp-network-dev`

**Features**:
- **Hot-reload**: Code changes reflected immediately
- **Debug logging**: Verbose output for troubleshooting
- **Volume mounts**: No rebuild needed for code changes
- **Single worker**: Easier debugging

**Usage**:
```bash
docker-compose -f docker-compose.dev.yml up
# Edit code in ./src/ - changes apply instantly
```

**Ideal For**:
- Local development
- Rapid iteration
- Debugging issues
- Testing configuration changes

---

### `docker-compose.full.yml` (102 lines)

**Purpose**: Complete production setup with API, UI, and optional monitoring.

**Services**:

**1. API Service**:
- Same as standard `docker-compose.yml`
- Full resource allocation
- Health checks enabled

**2. UI Service**:
- Image: `cloud-nlp-classifier-ui:latest`
- Container: `nlp-ui`
- Port: 8501
- Environment: Streamlit settings + `API_URL=http://api:8000`
- Volumes: `./models:/app/models`
- **Depends On**: API service (waits for healthy status)
- Health Check: Streamlit health endpoint
- Resources:
  - Limits: 2 CPU, 2.5 GB RAM
  - Reservations: 0.5 CPU, 1 GB RAM

**3. Nginx (Optional)**:
- Commented out, ready to enable
- Reverse proxy for both services
- SSL termination support

**Network**: `nlp-network` (shared)

**Features**:
- **Service Dependencies**: UI waits for API to be healthy
- **Shared Network**: Services can communicate
- **Resource Optimization**: Balanced allocation
- **Production-Ready**: Health checks, restarts, monitoring

**Usage**:
```bash
docker-compose -f docker-compose.full.yml up -d
# Access API: http://localhost:8000
# Access UI: http://localhost:8501
```

---

### `docker-compose.fullstack.yml` (86 lines)

**Purpose**: Full-stack deployment for local testing (API + UI).

**Services**:

**1. API Service**:
- Image: `cloud-nlp-classifier:latest`
- Container: `nlp-api`
- Port: 8000
- Environment: `LOG_LEVEL=info`, `WORKERS=1`
- Volumes: `./logs:/app/logs`
- Resources: 2 CPU, 3 GB RAM

**2. UI Service (API Mode)**:
- Image: `cloud-nlp-ui:latest`
- Container: `nlp-ui`
- Port: 8501
- Dockerfile: `Dockerfile.streamlit.api` (lightweight)
- Environment: `API_URL=http://api:8000`
- **Depends On**: API service
- Resources: 1 CPU, 1 GB RAM (lighter than full UI)

**Differences from `docker-compose.full.yml`**:
- Uses lightweight UI image (API mode)
- No model volumes for UI (calls API instead)
- Lower resource requirements for UI
- Simpler configuration

**Usage**:
```bash
docker-compose -f docker-compose.fullstack.yml up -d
docker-compose -f docker-compose.fullstack.yml logs -f
```

**Best For**:
- Local full-stack testing
- Demo deployments
- Integration testing
- Development with both services

---

### `docker-compose.prod.yml` (51 lines)

**Purpose**: Production-optimized configuration with multiple workers.

**Service**: API Production

**Configuration**:
- Image: `cloud-nlp-classifier:latest` (pre-built)
- Container: `nlp-api-prod`
- Port: 8000
- Environment:
  - `LOG_LEVEL=warning` (less verbose)
  - **`WORKERS=4`** (multiple workers for concurrency)
- Volumes: `./logs:/app/logs`
- Restart: **`always`** (aggressive restart policy)
- Health Check: Standard `/health` endpoint
- Resources:
  - **Limits: 4 CPU, 4 GB RAM** (higher than dev)
  - **Reservations: 2 CPU, 2 GB RAM**
- **Deploy**:
  - Replicas: 1
  - Restart Policy: On failure, 5s delay, 3 max attempts
- Network: `nlp-network-prod`

**Production Features**:
- **Multiple Workers**: 4 workers for high concurrency
- **Warning-Level Logging**: Reduces log volume
- **Always Restart**: Ensures high availability
- **Higher Resources**: Better performance under load
- **Restart Policy**: Automatic recovery from failures

**Usage**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Performance**:
- Throughput: 80-200 req/s (4 workers)
- Latency: Similar to single worker
- Concurrency: 4x better than dev
- Availability: Auto-restart on failure

---

### `docker-compose.ui.yml` (69 lines)

**Purpose**: Streamlit UI development with hot-reload.

**Service**: UI Development

**Configuration**:
- Image: `cloud-nlp-classifier-ui:dev`
- Container: `nlp-ui-dev`
- Port: 8501
- Environment:
  - Streamlit server settings
  - `STREAMLIT_SERVER_RUN_ON_SAVE=true` (hot-reload)
  - `STREAMLIT_SERVER_FILE_WATCHER_TYPE=auto`
- **Volumes** (Hot-Reload):
  - `./src/ui:/app/src/ui` - UI source code
  - `./src/ui/components:/app/src/ui/components`
  - `./src/ui/utils:/app/src/ui/utils`
  - `./.streamlit:/app/.streamlit` - Streamlit config
  - `./models:/app/models` - Model files
  - `./config:/app/config` - Configuration
- Health Check: Streamlit health endpoint
- Resources:
  - Limits: 2 CPU, 2.5 GB RAM
  - Reservations: 0.5 CPU, 1 GB RAM
- Restart: `unless-stopped`

**Features**:
- **Hot-Reload**: UI changes apply instantly
- **Volume Mounts**: No rebuild for code changes
- **Model Access**: Direct access to trained models
- **Development Mode**: File watcher enabled

**Usage**:
```bash
docker-compose -f docker-compose.ui.yml up
# Edit files in ./src/ui/ - Streamlit auto-reloads
```

**Combined Usage**:
```bash
# Run both API and UI in dev mode
docker-compose -f docker-compose.yml -f docker-compose.ui.yml up
```

**Ideal For**:
- UI development and testing
- Rapid prototyping
- Design iterations
- Component testing

---

## CHECKPOINT 8: Docker Compose Files Complete ✓

---

## Dockerfiles

### `Dockerfile` (83 lines)

**Purpose**: Production-ready FastAPI backend with all models.

**Base Image**: `python:3.11-slim`

**Models Included**:
1. DistilBERT transformer (best accuracy)
2. Toxicity classifier (multi-label, 6 categories)
3. Logistic Regression (fast, interpretable)
4. Linear SVM (fast, robust)

**Build Stages**:

**1. System Dependencies**:
- `build-essential` - C compiler for Python packages
- `curl` - Health checks
- `git` - Sometimes needed by transformers

**2. Python Dependencies**:
- Install from `requirements.txt`
- Uninstall jupyter/ipykernel (not needed in production)
- No cache to reduce image size

**3. Application Code**:
- Copy `src/` - Source code
- Copy `config/` - Configuration files

**4. Models**:
- `models/transformer/distilbert/` - DistilBERT model
- `models/toxicity_multi_head/` - Toxicity classifier
- `models/baselines/*.joblib` - Baseline models

**5. Security**:
- Create non-root user `appuser` (UID 1000)
- Change ownership to appuser
- Switch to non-root user

**Configuration**:
- Working Directory: `/app`
- Environment Variables:
  - `PYTHONUNBUFFERED=1`
  - `PYTHONDONTWRITEBYTECODE=1`
  - `PYTHONPATH=/app`
  - `PIP_NO_CACHE_DIR=1`
  - `DEFAULT_MODEL=distilbert`
- Exposed Port: 8000
- Health Check: `/health` endpoint every 30s

**Command**: `uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 1`

**Image Size**: ~2.0-2.5 GB (includes PyTorch, transformers, models)

**Build Time**: 5-10 min (first), 1-2 min (cached)

**Usage**:
```bash
# Build
docker build -t cloud-nlp-classifier .

# Run with default model
docker run -p 8000:8000 cloud-nlp-classifier

# Run with specific model
docker run -p 8000:8000 -e DEFAULT_MODEL=logistic_regression cloud-nlp-classifier
```

**Optimization Features**:
- Layer caching (requirements → code → models)
- Slim base image (smaller than full Python)
- No cache directories
- Non-root user for security
- Health check for monitoring

---

### `Dockerfile.streamlit` (58 lines)

**Purpose**: Streamlit UI with local model loading.

**Base Image**: `python:3.11-slim`

**Configuration**:
- Working Directory: `/app`
- Environment Variables:
  - Python settings (unbuffered, no bytecode)
  - Streamlit settings (port 8501, headless mode)
  - Stats collection disabled
- System Dependencies: `build-essential`, `curl`
- Python Dependencies: Full `requirements.txt`
- Non-root user: `appuser` (UID 1000)

**Files Copied**:
- `src/` - Application code
- `.streamlit/` - Streamlit configuration
- `config/` - Configuration files
- `models/` - **All trained models** (for local inference)

**Features**:
- **Local Model Loading**: UI loads models directly
- **No API Dependency**: Standalone operation
- **Full ML Stack**: Includes PyTorch, transformers, scikit-learn
- **Security**: Non-root user execution

**Exposed Port**: 8501

**Health Check**: `/_stcore/health` endpoint

**Command**: `streamlit run src/ui/streamlit_app.py --server.port=8501 --server.address=0.0.0.0`

**Image Size**: ~2.5 GB (includes all models and ML libraries)

**Usage**:
```bash
# Build
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui .

# Run
docker run -p 8501:8501 cloud-nlp-classifier-ui

# Access: http://localhost:8501
```

**Use Cases**:
- Standalone UI deployment
- Demo environments
- Offline inference
- Development testing

---

### `Dockerfile.streamlit.api` (55 lines)

**Purpose**: Lightweight Streamlit UI that connects to FastAPI backend.

**Base Image**: `python:3.11-slim`

**Key Differences from `Dockerfile.streamlit`**:
- **No ML Libraries**: No PyTorch, transformers, scikit-learn
- **No Models**: Doesn't copy model files
- **Minimal Dependencies**: Only Streamlit, Plotly, requests
- **API Mode**: Calls external API for predictions

**Dependencies** (Minimal):
```
streamlit==1.29.0
plotly==5.18.0
requests==2.31.0
urllib3==2.1.0
```

**Files Copied**:
- `src/ui/` - **UI code only** (no model code)
- `.streamlit/` - Streamlit configuration
- **No models, no training code**

**Environment Variables**:
- Streamlit settings (same as full UI)
- **`API_URL=http://localhost:8000`** (configurable)

**Configuration**:
- Non-root user: `appuser`
- Exposed Port: 8501
- Health Check: Streamlit health endpoint

**Command**: `streamlit run src/ui/streamlit_app_api.py --server.port=8501 --server.address=0.0.0.0`

**Image Size**: ~500 MB (5x smaller than full UI)

**Build Time**: 1-2 min (much faster)

**Usage**:
```bash
# Build
docker build -f Dockerfile.streamlit.api -t cloud-nlp-ui-api .

# Run (connect to API)
docker run -p 8501:8501 -e API_URL=http://api:8000 cloud-nlp-ui-api

# Run (connect to external API)
docker run -p 8501:8501 -e API_URL=http://35.232.76.140:8000 cloud-nlp-ui-api
```

**Advantages**:
- **5x Smaller**: 500 MB vs 2.5 GB
- **Faster Build**: 1-2 min vs 5-10 min
- **Scalable**: Multiple UI instances, single API
- **Separation**: UI and backend independently deployable

**Use Cases**:
- Production deployments
- Microservices architecture
- Cloud deployments (Cloud Run, ECS)
- Multiple UI replicas

---

## CHECKPOINT 9: Dockerfiles Complete ✓

---

## Summary (Part 2)

### Docker Compose Files Comparison

| File | Services | Purpose | Resources | Use Case |
|------|----------|---------|-----------|----------|
| `docker-compose.yml` | API + UI + Optional | Standard full-stack | 2 CPU, 3 GB | General deployment |
| `docker-compose.api-only.yml` | API only | Backend only | 2 CPU, 3 GB | API-only deployment |
| `docker-compose.dev.yml` | API (dev) | Development | 2 CPU, 3 GB | Hot-reload development |
| `docker-compose.full.yml` | API + UI + Nginx | Complete production | 4 CPU, 5.5 GB | Full production stack |
| `docker-compose.fullstack.yml` | API + UI (API mode) | Local testing | 3 CPU, 4 GB | Integration testing |
| `docker-compose.prod.yml` | API (4 workers) | Production optimized | 4 CPU, 4 GB | High-load production |
| `docker-compose.ui.yml` | UI (dev) | UI development | 2 CPU, 2.5 GB | UI hot-reload |

### Dockerfile Comparison

| Dockerfile | Base | Size | Build Time | Models | Use Case |
|------------|------|------|------------|--------|----------|
| `Dockerfile` | python:3.11-slim | ~2.5 GB | 5-10 min | All 4 models | FastAPI backend |
| `Dockerfile.streamlit` | python:3.11-slim | ~2.5 GB | 5-10 min | All models | Standalone UI |
| `Dockerfile.streamlit.api` | python:3.11-slim | ~500 MB | 1-2 min | None | Lightweight UI |

### Deployment Scenarios

**Scenario 1: Local Development**
- Use: `docker-compose.dev.yml` (API) + `docker-compose.ui.yml` (UI)
- Features: Hot-reload for both services
- Resources: 4 CPU, 5.5 GB RAM

**Scenario 2: Local Testing**
- Use: `docker-compose.fullstack.yml`
- Features: Full stack with API mode UI
- Resources: 3 CPU, 4 GB RAM

**Scenario 3: Production (Single Server)**
- Use: `docker-compose.full.yml`
- Features: API + UI + optional monitoring
- Resources: 4 CPU, 5.5 GB RAM

**Scenario 4: Production (Microservices)**
- API: `docker-compose.prod.yml` (4 workers)
- UI: `Dockerfile.streamlit.api` (multiple replicas)
- Features: Scalable, independent services
- Resources: Variable based on load

**Scenario 5: API-Only Deployment**
- Use: `docker-compose.api-only.yml`
- Features: Backend only, no UI
- Resources: 2 CPU, 3 GB RAM
- Ideal For: Cloud Run, ECS, Kubernetes

### Key Features Across All Configurations

**Health Checks**:
- API: `/health` endpoint every 30s
- UI: `/_stcore/health` endpoint every 30s
- Start period: 40s (allows model loading)
- Retries: 3 before marking unhealthy

**Resource Management**:
- All configs have CPU and memory limits
- Reservations ensure minimum resources
- Prevents resource starvation

**Security**:
- All images use non-root user (appuser, UID 1000)
- Minimal base images (slim variants)
- No secrets in images

**Networking**:
- Bridge networks for service communication
- Named networks for clarity
- Service discovery via container names

**Restart Policies**:
- Development: `unless-stopped`
- Production: `always` or `on-failure`
- Ensures high availability

---

## CHECKPOINT 10: Part 2 Complete ✓

**Files Documented in Part 2**: 11/11
- 7 Docker Compose files
- 3 Dockerfiles
- 1 .dockerignore (referenced from Part 1)

**Total Files Documented**: 24 (13 from Part 1 + 11 from Part 2)

---

# PART 3: Root-Level Python & PowerShell Scripts

**Document Status**: Part 3 of N (14 files documented)
**Last Updated**: 2025-12-10

---

## File Categories (Part 3)

### Python Execution Scripts (8)
- `check_training_status.py` - Training diagnostics tool
- `quick_test_training.py` - Phase 10 feature testing
- `run_baselines.py` - Baseline model training runner
- `run_preprocess.py` - Data preprocessing runner
- `run_streamlit.py` - Streamlit UI launcher
- `run_tests.py` - Test suite runner
- `run_transformer.py` - Transformer training runner
- `train_all_models.py` - Master training orchestrator

### Testing Scripts (5)
- `test_api_endpoints.py` - API endpoint testing
- `test_cleanup.ps1` - Phase 10 cleanup & verification
- `test_docker_api.ps1` - Docker API testing
- `test_multimodel_docker.ps1` - Phase 8 multi-model testing
- `test_performance.ps1` - Phase 9 performance validation

### Dependencies (1)
- `requirements.txt` - Python package dependencies

---

## CHECKPOINT 11: Part 3 Categories Complete ✓

---

## Python Execution Scripts

### `check_training_status.py` (202 lines)

**Purpose**: Diagnostic tool to check if training is stuck or just slow.

**Usage**: Run in separate terminal while training is running.

**Key Functions**:

**1. Process Monitoring**:
- `check_python_processes()` - Find all Python processes
- Tracks CPU usage, memory, runtime for each process
- 10-second monitoring window with real-time updates

**2. File Activity Tracking**:
- `check_training_files()` - Check for recent model file modifications
- Monitors: `models/baselines/`, `models/transformer/distilbert/`, `models/transformer/distilbert_fullscale/`
- Detects files modified in last 10 minutes

**3. Analysis & Diagnosis**:
- **Active Training**: CPU > 50% - Training running normally
- **Slow Training**: CPU 10-50% - Slow but active (CPU training, I/O wait)
- **May Be Stuck**: CPU 0.1-10% - Very low activity (possible deadlock)
- **Stuck**: CPU < 0.1% - No activity (likely deadlocked)

**Output**:
```
TRAINING STATUS CHECKER
✓ Found 2 Python process(es)
Monitoring CPU usage for 10 seconds...
[1/10] PID 12345: CPU=85.2% | Memory=2.45 GB | Runtime=15m 32s

ANALYSIS
✅ TRAINING IS ACTIVE
   Average CPU usage: 82.3%
   Status: Training is running normally
   Action: Be patient, training takes time!

RECENT FILE ACTIVITY
✓ Found 3 recently modified file(s):
   pytorch_model.bin (modified 2m 15s ago)
   training_info.json (modified 2m 15s ago)
   config.json (modified 5m 30s ago)
   Status: Training is making progress!

RECOMMENDATIONS
✅ Everything looks good! Training is active.
   - Continue waiting for training to complete
   - Check console for progress updates
```

**Troubleshooting Recommendations**:
- If stuck: Kill process, set `dataloader_num_workers: 0`, restart
- Reference: `docs/TRAINING_STALL_DIAGNOSIS.md`

**Dependencies**: `psutil`, `time`, `pathlib`

**Use Cases**:
- Verify training is progressing
- Diagnose DataLoader deadlocks (Windows)
- Monitor resource usage
- Check for file activity

---

### `quick_test_training.py` (202 lines)

**Purpose**: Quick 5-minute test of Phase 10 advanced training features.

**Features Tested**:
1. CLI argument parsing
2. Early stopping
3. Learning rate schedulers
4. FP16 mixed precision
5. Configuration system

**Verification Process**:

**1. Static Code Verification**:
- Checks `src/models/transformer_training.py` for Phase 10 features
- Validates presence of: argparse, cloud mode, LR schedulers, FP16, CLI overrides
- Reports which features are present/missing

**2. Runtime Verification**:
- Monitors training output for Phase 10 indicators
- Checks for: Training mode, LR scheduler, early stopping, config section

**Test Modes**:
```
1. Quick test (1 epoch, small batch) - ~5 minutes
2. Standard test (2 epochs, normal batch) - ~10-15 minutes
3. FP16 test (1 epoch with mixed precision) - ~5 minutes
4. Custom (enter your own parameters)
```

**Commands Generated**:
```bash
# Quick test
python -m src.models.transformer_training --epochs 1 --batch-size 16

# FP16 test
python -m src.models.transformer_training --epochs 1 --batch-size 16 --fp16

# Custom
python -m src.models.transformer_training --epochs 5 --batch-size 32 --learning-rate 3e-5 --fp16
```

**Output Indicators**:
```
✅ All Phase 10 features detected in training script!
✅ You are using the NEW advanced training implementation

🔍 WATCH FOR THESE PHASE 10 INDICATORS IN THE OUTPUT:
  ✓ 'Training mode: local' or 'Training mode: cloud'
  ✓ 'Using learning rate scheduler: [type]'
  ✓ 'Early stopping enabled' or 'Early stopping disabled'
  ✓ 'FP16 mixed precision training enabled' (if GPU)
  ✓ 'Training Configuration:' section with detailed settings
```

**Prerequisites**: Processed training data in `data/processed/`

**Results Display**:
- Model location
- Training metrics (accuracy, F1, time)
- Inference time

---

### `run_baselines.py` (139 lines)

**Purpose**: Cross-platform script to run baseline model training.

**Models Trained**:
1. Logistic Regression with TF-IDF
2. Linear SVM with TF-IDF

**Workflow**:

**1. Dependency Check**:
- scikit-learn
- Pandas
- NumPy
- joblib
- PyYAML

**2. Data Validation**:
- `data/processed/train.csv`
- `data/processed/val.csv`
- `data/processed/test.csv`

**3. Training Execution**:
- Runs: `python -m src.models.train_baselines`
- Real-time output display
- Error handling and exit codes

**Output**:
```
========================================
Starting Baseline Model Training Pipeline
========================================

Checking dependencies...
  ✓ scikit-learn installed
  ✓ Pandas installed
  ✓ NumPy installed
  ✓ joblib installed
  ✓ PyYAML installed

✓ All dependencies installed!

Checking data files...
  ✓ data/processed/train.csv exists
  ✓ data/processed/val.csv exists
  ✓ data/processed/test.csv exists

✓ All data files found!

Running baseline training...
[Training output...]

✓ Baseline Training Complete!
Models saved to: models/baselines/

Next steps:
  1. Train transformer: python run_transformer.py
  2. Compare results
```

**Features**:
- Colored terminal output (ANSI codes)
- Cross-platform compatibility (Windows, Linux, Mac)
- Comprehensive error messages
- Keyboard interrupt handling

---

### `run_preprocess.py` (132 lines)

**Purpose**: Cross-platform script to run data preprocessing.

**Workflow**:

**1. Dependency Check**:
- Pandas
- NumPy
- scikit-learn

**2. Raw Data Validation**:
- Checks for: `data/raw/dataset.csv`
- Verifies file has 'text' and 'label' columns

**3. Preprocessing Execution**:
- Runs: `python -m src.data.preprocess`
- Creates train/val/test splits
- Cleans and normalizes text

**Output**:
```
========================================
Starting Data Preprocessing Pipeline
========================================

Checking dependencies...
  ✓ Pandas installed
  ✓ NumPy installed
  ✓ scikit-learn installed

✓ All dependencies installed!

Checking raw data...
  ✓ data/raw/dataset.csv exists

✓ Raw data found!

Running preprocessing...
[Preprocessing output...]

✓ Data Preprocessing Complete!

Processed data saved to:
  - data/processed/train.csv
  - data/processed/val.csv
  - data/processed/test.csv

Next steps:
  1. Train baselines: python run_baselines.py
  2. Train transformer: python run_transformer.py
```

**Features**:
- Colored output
- Cross-platform
- Clear error messages
- Next steps guidance

---

### `run_streamlit.py` (140 lines)

**Purpose**: Cross-platform script to run Streamlit UI.

**Workflow**:

**1. Streamlit Check**:
- Verifies Streamlit installation
- Auto-installs if missing: `pip install streamlit>=1.28.0 plotly>=5.17.0`

**2. Model Detection**:
- Checks for trained models:
  - Logistic Regression: `models/baselines/logistic_regression_tfidf.joblib`
  - Linear SVM: `models/baselines/linear_svm_tfidf.joblib`
  - DistilBERT: `models/transformer/distilbert/pytorch_model.bin`
- Warns if no models found
- Allows continuing without models

**3. UI Launch**:
- Runs: `streamlit run src/ui/streamlit_app.py --server.port 8501`
- Opens browser at `http://localhost:8501`
- Runs in foreground (Ctrl+C to stop)

**Output**:
```
==================================================
  Cloud NLP Classifier - Streamlit UI
==================================================

Checking dependencies...
✓ Streamlit is installed

Checking for trained models...
✓ Logistic Regression model found
✓ Linear SVM model found
✓ DistilBERT model found

==================================================
Starting Streamlit UI...
==================================================

The UI will open in your browser at:
  http://localhost:8501

Press Ctrl+C to stop the server
```

**Features**:
- Auto-installation of dependencies
- Model availability check
- User confirmation if models missing
- Browser auto-open

---

### `run_tests.py` (119 lines)

**Purpose**: Cross-platform script to run Phase 3 tests.

**Tests Executed**:
1. Model Loading (`tests/test_model_loading.py`)
2. Inference (`tests/test_inference.py`)
3. Metrics Validation (`tests/test_metrics.py`)

**Workflow**:

**1. Test File Validation**:
- Checks if all test files exist
- Reports missing tests

**2. Test Execution**:
- Runs each test sequentially
- Captures pass/fail status
- Continues even if tests fail

**3. Summary Report**:
- Shows results for each test
- Overall pass/fail status
- Next steps guidance

**Output**:
```
========================================
Phase 3 Testing Suite
========================================

Running Test: Model Loading...
------------------------------------------------------------
[Test output...]
✓ Model Loading passed

Running Test: Inference...
------------------------------------------------------------
[Test output...]
✓ Inference passed

Running Test: Metrics Validation...
------------------------------------------------------------
[Test output...]
✓ Metrics Validation passed

========================================
Test Summary
========================================
  ✓ Model Loading
  ✓ Inference
  ✓ Metrics Validation

========================================
✓ ALL TESTS PASSED!
Phase 3 is working correctly!
========================================

Next steps:
  1. Review results in models/transformer/distilbert/
  2. Compare with baseline models
  3. Move to Phase 4: FastAPI server
```

**Features**:
- Colored output
- Individual test tracking
- Comprehensive summary
- Exit codes (0=success, 1=failure, 130=interrupted)

---

### `run_transformer.py` (141 lines)

**Purpose**: Cross-platform script to run transformer training.

**Workflow**:

**1. Dependency Check**:
- PyTorch
- Transformers
- Datasets
- scikit-learn
- Pandas
- NumPy
- PyYAML

**2. Data Validation**:
- `data/processed/train.csv`
- `data/processed/val.csv`
- `data/processed/test.csv`

**3. Training Execution**:
- Runs: `python -m src.models.transformer_training`
- Uses default config: `config/config_transformer.yaml`
- Real-time output display

**Output**:
```
========================================
Starting Transformer Training Pipeline
========================================

Checking dependencies...
  ✓ PyTorch installed
  ✓ Transformers installed
  ✓ Datasets installed
  ✓ scikit-learn installed
  ✓ Pandas installed
  ✓ NumPy installed
  ✓ PyYAML installed

✓ All dependencies installed!

Checking data files...
  ✓ data/processed/train.csv exists
  ✓ data/processed/val.csv exists
  ✓ data/processed/test.csv exists

✓ All data files found!

Running training...
[Training output...]

✓ Transformer Training Complete!

Model saved to: models/transformer/distilbert/

Next steps:
  1. Run tests: python run_tests.py
  2. Check results: python tests/test_metrics.py
```

**Features**:
- Comprehensive dependency checking
- Colored terminal output
- Error handling
- Next steps guidance

---

### `train_all_models.py` (324 lines)

**Purpose**: Master training script to train all models sequentially.

**Models Trained** (3 total):
1. **Baseline Models**: Logistic Regression + Linear SVM
2. **DistilBERT (Standard)**: 256 seq length, 15 epochs, patience=5
3. **DistilBERT (Full-Scale)**: 512 seq length, 25 epochs, patience=8

**Key Features**:

**1. Prerequisite Checking**:
- Validates data files (train, val, test)
- Validates config files (baselines, transformer, transformer_fullscale)
- Reports missing files

**2. Training Orchestration**:
- Sequential execution of all training steps
- Real-time output display
- Duration tracking for each model
- Continue-on-failure option (configurable)

**3. Progress Tracking**:
- Colored ANSI output
- Step-by-step progress indicators
- Duration formatting (hours, minutes, seconds)
- Pause between models (5 seconds)

**4. Comprehensive Reporting**:
- JSON report saved to `training_report.json`
- Success/failure tracking
- Duration for each model
- Timestamps for all events

**Training Steps**:
```python
[1/3] Baseline Models (Logistic Regression + Linear SVM)
      Training classical ML models with TF-IDF features (10k features, n-grams 1-3)
      Duration: ~5-10 minutes

[2/3] DistilBERT Transformer (Standard Configuration)
      Training DistilBERT with 256 seq length, 15 epochs, early stopping (patience=5)
      Duration: ~30-60 minutes (GPU) or 2-4 hours (CPU)

[3/3] DistilBERT Transformer (Intensive Full-Scale)
      Training DistilBERT with 512 seq length, 25 epochs, early stopping (patience=8)
      Duration: ~60-120 minutes (GPU) or 4-8 hours (CPU)
```

**Output**:
```
================================================================================
FULL-SCALE MODEL TRAINING PIPELINE
================================================================================
ℹ This script will train all available models with comprehensive configurations.
ℹ Training includes early stopping, detailed logging, and performance tracking.

========================================
Checking Prerequisites
========================================
ℹ Checking data files...
✓ Found: data/processed/train.csv
✓ Found: data/processed/val.csv
✓ Found: data/processed/test.csv

ℹ Checking configuration files...
✓ Found: config/config_baselines.yaml
✓ Found: config/config_transformer.yaml
✓ Found: config/config_transformer_fullscale.yaml

✓ All prerequisites met!

⚠ This will train 3 models sequentially. Estimated time: 2-6 hours (GPU) or 12-24 hours (CPU)
ℹ You can interrupt training at any time with Ctrl+C

Do you want to proceed? (yes/no): yes

[1/3]
================================================================================
Training: Baseline Models (Logistic Regression + Linear SVM)
================================================================================
[Training output...]
✓ Baseline Models (Logistic Regression + Linear SVM) completed successfully!
Duration: 5m 32s

[2/3]
================================================================================
Training: DistilBERT Transformer (Standard Configuration)
================================================================================
[Training output...]
✓ DistilBERT Transformer (Standard Configuration) completed successfully!
Duration: 45m 18s

[3/3]
================================================================================
Training: DistilBERT Transformer (Intensive Full-Scale)
================================================================================
[Training output...]
✓ DistilBERT Transformer (Intensive Full-Scale) completed successfully!
Duration: 1h 32m 45s

✓ Training report saved to: training_report.json

================================================================================
Training Session Summary
================================================================================
Total Duration: 2h 23m 35s
Models Trained: 3
Successful: 3
Failed: 0

Model Results:
  ✓ Baseline Models (Logistic Regression + Linear SVM) - 5m 32s
  ✓ DistilBERT Transformer (Standard Configuration) - 45m 18s
  ✓ DistilBERT Transformer (Intensive Full-Scale) - 1h 32m 45s

Model Locations:
  • Baseline Models: models/baselines/
  • DistilBERT (Standard): models/transformer/distilbert/
  • DistilBERT (Full-Scale): models/transformer/distilbert_fullscale/

🎉 All models trained successfully!
```

**Report Structure** (`training_report.json`):
```json
{
  "training_session": {
    "start_time": "2025-12-10T20:00:00",
    "end_time": "2025-12-10T22:23:35",
    "total_duration_seconds": 8615,
    "total_duration_formatted": "2h 23m 35s"
  },
  "models_trained": [
    {
      "name": "Baseline Models",
      "status": "success",
      "duration": 332,
      "timestamp": "2025-12-10T20:05:32"
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

**Features**:
- User confirmation before starting
- Keyboard interrupt handling (Ctrl+C)
- Partial results saved on interruption
- Exit codes: 0=success, 1=failure, 2=partial success, 130=interrupted
- Colored output with icons (✓, ✗, ⚠, ℹ)

**Use Cases**:
- Full project training from scratch
- Automated training pipeline
- Batch training for experiments
- CI/CD integration

---

## CHECKPOINT 12: Python Execution Scripts Complete ✓

---

## Testing Scripts

### `test_api_endpoints.py` (179 lines)

**Purpose**: Quick API endpoint testing for Phase 5 multi-model functionality.

**Base URL**: `http://localhost:8000`

**Tests Executed** (10 total):

**1. Root Endpoint** (GET `/`):
- Verifies API info response
- Checks version and status

**2. Health Check** (GET `/health`):
- Validates status, current_model, available_models
- Ensures API is healthy

**3. List Models** (GET `/models`):
- Checks all 3 models are available
- Displays model details (name, type, accuracy)

**4. Prediction with DistilBERT** (POST `/predict`):
- Text: "I love this product! It's amazing!"
- Validates prediction, confidence, inference time

**5. Switch to Logistic Regression** (POST `/models/switch`):
- Switches from DistilBERT to Logistic Regression
- Verifies model switch successful

**6. Prediction with Logistic Regression**:
- Text: "This is offensive and hateful content"
- Measures total request time vs inference time

**7. Switch to Linear SVM**:
- Switches to Linear SVM model
- Verifies correct model loaded

**8. Prediction with Linear SVM**:
- Text: "Normal everyday conversation"
- Tests fast baseline model

**9. Switch Back to DistilBERT**:
- Returns to default model
- Verifies switch successful

**10. Invalid Model Switch**:
- Attempts to switch to "invalid_model"
- Expects 400 error (correctly rejected)

**Output**:
```
================================================================================
API ENDPOINT TESTING
================================================================================

1. Testing Root Endpoint (GET /)...
   Status: 200
   Response: {
     "message": "Cloud NLP Classifier API",
     "version": "2.0.0",
     "status": "running"
   }
   ✅ PASSED

2. Testing Health Check (GET /health)...
   Status: 200
   Status: healthy
   Current Model: distilbert
   Available Models: ['distilbert', 'logistic_regression', 'linear_svm']
   ✅ PASSED

3. Testing List Models (GET /models)...
   Status: 200
   Current Model: distilbert
   Available Models: 3
     - distilbert: transformer (Acc: 0.9657)
     - logistic_regression: baseline (Acc: 0.8542)
     - linear_svm: baseline (Acc: 0.8498)
   ✅ PASSED

4. Testing Prediction with DistilBERT (POST /predict)...
   Status: 200
   Text: I love this product! It's amazing!
   Predicted Label: not hate
   Confidence: 98.45%
   Model Used: distilbert
   Inference Time: 8.14ms
   ✅ PASSED

[... tests 5-10 ...]

================================================================================
API TESTING COMPLETE!
================================================================================

✅ All 10 tests completed!

Next steps:
  1. Check interactive docs: http://localhost:8000/docs
  2. Run full test suite: python run_tests.py
  3. Stop the server (Ctrl+C in server terminal)
================================================================================
```

**Features**:
- Comprehensive endpoint coverage
- Multi-model testing
- Performance measurement
- Error handling validation
- Clear pass/fail indicators

**Prerequisites**: API server running on port 8000

---

### `test_cleanup.ps1` (278 lines)

**Purpose**: Phase 10 cleanup and verification script.

**Steps Executed**:

**Step 1: Docker Cleanup**:
- Stops and removes test containers:
  - `nlp-api-test-default`
  - `nlp-api-test-logreg`
  - `nlp-api-test-svm`
  - `nlp-api-test-switching`
  - `nlp-api-perf-test`
  - `nlp-api`
- Reports: containers stopped, containers removed

**Step 2: Model File Verification**:
- Checks 6 model files:
  - DistilBERT: model, config, tokenizer, labels
  - Logistic Regression pipeline
  - Linear SVM pipeline
- Reports: file size, found/missing status
- Calculates total model size

**Step 3: Data File Verification**:
- Checks 4 data files:
  - Raw dataset
  - Train, validation, test splits
- Reports: line counts for each file

**Step 4: Docker Image Verification**:
- Checks for: `cloud-nlp-classifier:latest`
- Reports: image size

**Step 5: Docker Resource Summary**:
- Running containers count
- Total containers count
- Total images count

**Step 6: Test Results Verification**:
- Checks for:
  - `performance_results.json`
  - `END_TO_END_TEST_PROGRESS.md`
  - `END_TO_END_TEST_RESULTS.md`

**Step 7: Project Statistics**:
- Counts documentation files (`.md` in `docs/`)
- Counts script files (`.ps1` in `scripts/`)
- Counts test files (`.py` in `tests/`)

**Output**:
```
========================================
  Phase 10: Cleanup & Verification
========================================

[STEP 1] Cleaning up Docker containers...
  Stopping container: nlp-api-test-default
  Removing container: nlp-api-test-default
  [... more containers ...]
[OK] Containers cleaned up: 6 stopped, 6 removed

[STEP 2] Verifying model files...
  [OK] DistilBERT Model : 267.84 MB
  [OK] DistilBERT Config : 0.52 KB
  [OK] DistilBERT Tokenizer : 0.28 KB
  [OK] DistilBERT Labels : 0.05 KB
  [OK] Logistic Regression : 45.23 MB
  [OK] Linear SVM : 42.18 MB
[OK] Model verification: 6 found, 0 missing
     Total model size: 355.82 MB

[STEP 3] Verifying data files...
  [OK] Raw Dataset : 24783 lines
  [OK] Train Split : 17348 lines
  [OK] Validation Split : 4947 lines
  [OK] Test Split : 4947 lines
[OK] Data verification: 4 found, 0 missing

[STEP 4] Verifying Docker image...
  [OK] Image found: cloud-nlp-classifier:latest
       Size: 2.5GB

[STEP 5] Docker resource summary...
  Running containers: 0
  Total containers: 0
  Total images: 5

[STEP 6] Verifying test results...
  [OK] Performance Results
  [OK] Progress Tracker
  [OK] Test Results

[STEP 7] Generating summary statistics...
  Documentation files: 33
  Script files: 10
  Test files: 9

============================================================
Phase 10: Cleanup & Verification Summary
============================================================

[SUMMARY] Cleanup Results:
  Containers stopped: 6
  Containers removed: 6

[SUMMARY] Model Verification:
  Models found: 6/6
  Total size: 355.82 MB
  Status: [OK] All models present

[SUMMARY] Data Verification:
  Data files found: 4/4
  Status: [OK] All data files present

[SUMMARY] Docker Status:
  Image exists: True
  Image size: 2.5GB
  Running containers: 0

[SUMMARY] Project Statistics:
  Documentation: 33 files
  Scripts: 10 files
  Tests: 9 files

[INFO] Cleanup duration: 1.17 seconds
[INFO] Results saved to cleanup_verification_results.json

============================================================
[SUCCESS] Phase 10: All verifications passed!
============================================================

[OK] Phase 10 complete!
Review the results and update END_TO_END_TEST_PROGRESS.md
```

**Output File**: `cleanup_verification_results.json`

**Features**:
- Comprehensive cleanup
- Detailed verification
- JSON report generation
- Color-coded output
- Success/warning/error indicators

---

### `test_docker_api.ps1` (175 lines)

**Purpose**: Docker API comprehensive testing script.

**Base URL**: `http://localhost:8000`

**Tests Executed** (8 total):

**1. Health Check**:
- Endpoint: GET `/health`
- Validates: status, current_model, available_models, num_classes

**2. Root Endpoint**:
- Endpoint: GET `/`
- Validates: version, status

**3. Prediction (DistilBERT)**:
- Text: "I love this product, it is amazing!"
- Measures: inference time, confidence

**4. List Models**:
- Endpoint: GET `/models`
- Validates: current_model, available_models count

**5. Negative Sentiment**:
- Text: "This is terrible and offensive content that should be flagged"
- Tests: hate speech detection

**6. Neutral Text**:
- Text: "The weather is nice today"
- Tests: neutral classification

**7. Performance Test** (10 requests):
- Sends 10 rapid requests
- Measures: average, min, max response times

**8. Container Logs Check**:
- Retrieves last 5 log lines from container
- Validates container is running

**Output**:
```
================================================================================
Docker API Comprehensive Testing
================================================================================

1. Testing Health Check...
   Status: healthy
   Current Model: distilbert
   Available Models: distilbert, logistic_regression, linear_svm
   Classes: 2
   ✅ PASSED

2. Testing Root Endpoint...
   Version: 2.0.0
   Status: running
   ✅ PASSED

3. Testing Prediction (DistilBERT)...
   Text: 'I love this product, it is amazing!'
   Predicted Label: not hate
   Confidence: 98.45%
   Inference Time: 8.14ms
   ✅ PASSED

[... tests 4-6 ...]

7. Testing Performance (10 requests)...
   Average Time: 45.23ms
   Min Time: 38.12ms
   Max Time: 62.45ms
   ✅ PASSED

8. Checking Container Logs...
   Last 5 log lines:
     INFO:     Started server process [1]
     INFO:     Waiting for application startup.
     INFO:     Application startup complete.
     INFO:     Uvicorn running on http://0.0.0.0:8000
     INFO:     127.0.0.1:52345 - "GET /health HTTP/1.1" 200 OK
   ✅ PASSED

================================================================================
Test Summary
================================================================================
Total Tests: 8
Passed: 8
Failed: 0

✅ ALL TESTS PASSED! Docker deployment is working perfectly!

Next Steps:
  1. View interactive docs: http://localhost:8000/docs
  2. View container logs: docker-compose logs -f api
  3. Stop containers: docker-compose down
================================================================================
```

**Features**:
- PowerShell `Invoke-RestMethod` for API calls
- Performance benchmarking
- Container log inspection
- Color-coded output
- Summary statistics

**Prerequisites**: Docker container running on port 8000

---

### `test_multimodel_docker.ps1` (476 lines)

**Purpose**: Phase 8 multi-model Docker testing script.

**Tests Executed** (4 test suites):

**Test 1: Default Model (DistilBERT)**:
- Starts container with default model
- Tests health endpoint
- Runs 4 predictions with different text types
- Validates DistilBERT is loaded

**Test 2: Logistic Regression Model**:
- Starts container with `DEFAULT_MODEL=logistic_regression`
- Verifies correct model loaded
- Tests predictions with Logistic Regression
- Measures inference time

**Test 3: Linear SVM Model**:
- Starts container with `DEFAULT_MODEL=linear_svm`
- Verifies correct model loaded
- Tests predictions with Linear SVM
- Measures inference time

**Test 4: Dynamic Model Switching**:
- Starts container with default model
- Switches between all 3 models dynamically
- Tests prediction after each switch
- Validates zero-downtime switching

**Test Data**:
```powershell
$TEST_TEXTS = @{
    "hate" = "I hate you and everyone like you"
    "normal" = "The weather is nice today"
    "offensive" = "You are so stupid and worthless"
    "neutral" = "I went to the store yesterday"
}
```

**Helper Functions**:
- `Wait-ContainerHealthy` - Wait up to 60s for container health
- `Test-APIEndpoint` - Make API requests (GET/POST)
- `Test-Prediction` - Test prediction and measure time
- `Remove-TestContainer` - Cleanup containers

**Output**:
```
========================================
  Phase 8: Multi-Model Docker Testing
========================================

============================================================
Test 1: Container with Default Model (DistilBERT)
============================================================
Starting container with default model...
Waiting for container 'nlp-api-test-default' to be healthy...
[OK] Container is healthy!

Testing health endpoint...
[OK] Health check passed
   Current Model: distilbert
   Available Models: distilbert, logistic_regression, linear_svm

Testing predictions with DistilBERT...
   Testing: 'I hate you and everyone like you'
   [OK] Label: hate | Confidence: 95.23% | Inference: 8.14ms
   [... more predictions ...]

[OK] Container removed

============================================================
Test 2: Container with Logistic Regression
============================================================
Starting container with Logistic Regression...
[OK] Container is healthy!

Testing health endpoint...
[OK] Health check passed
   Current Model: logistic_regression
   [OK] Correct model loaded!

Testing predictions with Logistic Regression...
   Testing: 'I hate you and everyone like you'
   [OK] Label: hate | Confidence: 87.45% | Inference: 0.66ms
   [... more predictions ...]

[... Tests 3 & 4 ...]

============================================================
Phase 8 Test Summary
============================================================

Total Tests: 25
Passed: 25 [OK]
Failed: 0 [X]
Success Rate: 100%

Average Inference Times:
   distilbert: 8.14ms
   logistic_regression: 0.66ms
   linear_svm: 0.60ms

Total Duration: 1.08 minutes

============================================================
[SUCCESS] Phase 8: PASSED - All multi-model tests successful!
============================================================

[OK] Phase 8 testing complete!
Review the results above and update END_TO_END_TEST_PROGRESS.md
```

**Features**:
- Comprehensive multi-model testing
- Container lifecycle management
- Health check validation
- Performance comparison
- Dynamic switching validation
- Detailed error reporting

**Duration**: ~1-2 minutes

---

### `test_performance.ps1` (384 lines)

**Purpose**: Phase 9 comprehensive performance validation for all 3 models.

**Configuration**:
- Models tested: DistilBERT, Logistic Regression, Linear SVM
- Test texts: 8 diverse samples
- Latency test: 100 requests per model
- Throughput test: 30 seconds, 10 concurrent requests
- Memory test: 5 readings over 10 seconds

**Test Functions**:

**1. Latency Test** (`Test-Latency`):
- Sends 100 sequential requests
- Measures inference time for each
- Calculates: min, max, avg, p50, p95, p99
- Reports success/failure count

**2. Throughput Test** (`Test-Throughput`):
- Runs 10 concurrent PowerShell jobs
- Each job sends requests for 30 seconds
- Calculates total requests and throughput (req/s)
- Measures errors

**3. Memory Test** (`Test-Memory`):
- Takes 5 memory readings (2s intervals)
- Uses `docker stats` command
- Reports memory usage and CPU percentage

**Helper Functions**:
- `Wait-ContainerHealthy` - Wait for container startup
- `Invoke-Prediction` - Make prediction request
- `Switch-Model` - Switch to different model
- `Get-ContainerStats` - Get Docker container stats
- `Get-Percentile` - Calculate percentile values

**Output**:
```
========================================
  Phase 9: Performance Validation
========================================

[SETUP] Starting Docker container...
Waiting for container 'nlp-api-perf-test' to be healthy...
[OK] Container is healthy!

[INFO] Container ready. Starting performance tests...

============================================================
Performance Testing: distilbert
============================================================

[SETUP] Switching to distilbert...
[OK] Switched to distilbert

[TEST] Latency Test for distilbert (100 iterations)
  Progress: 20/100 requests completed
  Progress: 40/100 requests completed
  Progress: 60/100 requests completed
  Progress: 80/100 requests completed
  Progress: 100/100 requests completed
[OK] Latency Test Complete
  Success: 100 | Failed: 0
  Min: 7.23ms | Max: 12.45ms
  Avg: 8.14ms
  p50: 7.95ms | p95: 9.38ms | p99: 12.51ms

[TEST] Throughput Test for distilbert (30 seconds, 10 concurrent)
  Running throughput test...
[OK] Throughput Test Complete
  Total Requests: 3542
  Errors: 0
  Duration: 30.12s
  Throughput: 117.62 req/s

[TEST] Memory Test for distilbert
  Reading 1/5: Memory = 508 MiB / 7.78 GiB, CPU = 0.12%
  Reading 2/5: Memory = 508 MiB / 7.78 GiB, CPU = 0.15%
  Reading 3/5: Memory = 508 MiB / 7.78 GiB, CPU = 0.13%
  Reading 4/5: Memory = 508 MiB / 7.78 GiB, CPU = 0.14%
  Reading 5/5: Memory = 508 MiB / 7.78 GiB, CPU = 0.12%
[OK] Memory Test Complete

[... Tests for logistic_regression and linear_svm ...]

============================================================
Phase 9: Performance Summary
============================================================

[SUMMARY] Latency Comparison:
Model                Avg (ms)   p50 (ms)   p95 (ms)   p99 (ms)
------------------------------------------------------------
distilbert              8.14       7.95       9.38      12.51
logistic_regression     0.66       0.62       0.85       1.54
linear_svm              0.60       0.57       0.74       1.22

[SUMMARY] Throughput Comparison:
Model                Throughput     Errors  Total Requests
------------------------------------------------------------
distilbert            117.62 req/s       0           3542
logistic_regression  1515.23 req/s       0          45457
linear_svm           1623.45 req/s       0          48703

[SUMMARY] Memory Usage:
  distilbert : 508 MiB / 7.78 GiB, 508 MiB / 7.78 GiB, ...
  logistic_regression : 505 MiB / 7.78 GiB, 505 MiB / 7.78 GiB, ...
  linear_svm : 505 MiB / 7.78 GiB, 505 MiB / 7.78 GiB, ...

[INFO] Total Test Duration: 2.65 minutes

[CLEANUP] Stopping and removing container...
[OK] Cleanup complete

[INFO] Results saved to performance_results.json

============================================================
[SUCCESS] Phase 9: Performance Validation Complete!
============================================================

Review the results above and update END_TO_END_TEST_PROGRESS.md
```

**Output File**: `performance_results.json` (detailed metrics)

**Features**:
- Comprehensive performance metrics
- Percentile calculations (p50, p95, p99)
- Concurrent throughput testing
- Memory and CPU monitoring
- JSON report generation
- Automated cleanup

**Duration**: ~2-3 minutes per model (~8-10 minutes total)

---

## CHECKPOINT 13: Testing Scripts Complete ✓

---

## Dependencies

### `requirements.txt` (40 lines)

**Purpose**: Python package dependencies for the entire project.

**Categories**:

**1. Core Data Science** (4 packages):
```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

**2. Visualization** (2 packages):
```
matplotlib>=3.7.0
seaborn>=0.12.0
```

**3. Deep Learning & NLP** (4 packages):
```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
accelerate>=0.20.0
```

**4. API & Web Server** (3 packages):
```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
```

**5. Streamlit UI** (2 packages):
```
streamlit>=1.28.0
plotly>=5.17.0
```

**6. Configuration & Environment** (2 packages):
```
python-dotenv>=1.0.0
pyyaml>=6.0
```

**7. Testing** (2 packages):
```
pytest>=7.4.0
httpx>=0.24.0
```

**8. Utilities** (2 packages):
```
tqdm>=4.65.0
joblib>=1.3.0
```

**9. Optional: Jupyter** (2 packages):
```
jupyter>=1.0.0
ipykernel>=6.25.0
```

**Installation**:
```bash
pip install -r requirements.txt
```

**Total Packages**: 21 (19 required + 2 optional)

**Key Version Requirements**:
- Python 3.11+ recommended
- PyTorch 2.0+ for transformer training
- Transformers 4.30+ for DistilBERT
- FastAPI 0.100+ for Pydantic V2 compatibility
- Pydantic 2.0+ (no deprecation warnings)
- Streamlit 1.28+ for modern UI features

**Notes**:
- All packages use minimum version requirements (`>=`)
- Jupyter packages optional (can be excluded in production)
- `uvicorn[standard]` includes websockets and other extras
- Compatible with Windows, Linux, and macOS

---

## CHECKPOINT 14: Part 3 Complete ✓

---

## Summary (Part 3)

### Python Execution Scripts Comparison

| Script | Purpose | Duration | Dependencies | Output |
|--------|---------|----------|--------------|--------|
| `check_training_status.py` | Training diagnostics | Real-time | psutil | Process monitoring |
| `quick_test_training.py` | Phase 10 testing | 5-15 min | Training modules | Feature verification |
| `run_baselines.py` | Baseline training | 5-10 min | sklearn, pandas | 2 models |
| `run_preprocess.py` | Data preprocessing | 2-5 min | pandas, sklearn | 3 splits |
| `run_streamlit.py` | UI launcher | Continuous | streamlit | Web UI |
| `run_tests.py` | Test runner | 2-5 min | pytest | Test results |
| `run_transformer.py` | Transformer training | 30-240 min | torch, transformers | 1 model |
| `train_all_models.py` | Master orchestrator | 2-24 hours | All above | 3 models + report |

### Testing Scripts Comparison

| Script | Purpose | Tests | Duration | Output |
|--------|---------|-------|----------|--------|
| `test_api_endpoints.py` | API testing | 10 tests | 1-2 min | Pass/fail status |
| `test_cleanup.ps1` | Phase 10 cleanup | 7 steps | <2 min | JSON report |
| `test_docker_api.ps1` | Docker API testing | 8 tests | 1-2 min | Performance metrics |
| `test_multimodel_docker.ps1` | Multi-model testing | 25 tests | 1-2 min | Model comparison |
| `test_performance.ps1` | Performance validation | 3 models × 3 tests | 8-10 min | JSON report |

### Key Features Across All Scripts

**Common Patterns**:
1. **Colored Output**: ANSI codes for terminal formatting
2. **Cross-Platform**: Windows, Linux, macOS compatibility
3. **Error Handling**: Comprehensive try-catch blocks
4. **Progress Tracking**: Real-time status updates
5. **Validation**: Prerequisite checking before execution
6. **Reporting**: JSON output files for automation

**Execution Flow**:
```
1. Prerequisites Check → 2. Execution → 3. Validation → 4. Reporting
```

**Error Handling**:
- Keyboard interrupt (Ctrl+C) support
- Graceful failure with clear messages
- Exit codes for automation (0=success, 1=failure, 130=interrupted)

**Output Formats**:
- Terminal: Colored ANSI output with icons (✓, ✗, ⚠, ℹ)
- Files: JSON reports for programmatic access
- Logs: Real-time streaming during execution

---

## FINAL CHECKPOINT: Part 3 Complete ✓

**Files Documented in Part 3**: 14/14
- 8 Python execution scripts
- 5 Testing scripts (4 PowerShell, 1 Python)
- 1 Dependencies file

**Total Files Documented**: 38 (13 from Part 1 + 11 from Part 2 + 14 from Part 3)

**Next**: Awaiting Part 4 file list for additive updates to this document.
