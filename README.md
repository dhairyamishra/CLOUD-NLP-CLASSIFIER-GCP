PS C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP> .\scripts\gcp-phase2-create-vm.ps1
========================================
Phase 2: Create and Configure VM
========================================
Verbose logging enabled

Reading configuration from gcp-deployment-config.txt...
  Loaded: PROJECT_ID = mnist-k8s-pipeline
  Loaded: REGION = us-central1
  Loaded: ZONE = us-central1-a
  Loaded: STATIC_IP = 35.232.76.140
  Loaded: VM_NAME = nlp-classifier-vm
  Loaded: MACHINE_TYPE = e2-standard-2
  Loaded: BOOT_DISK_SIZE = 50GB

Configuration loaded:
  Project:      mnist-k8s-pipeline
  VM Name:      nlp-classifier-vm
  Machine Type: e2-standard-2
  Disk Size:    50GB
  Static IP:    35.232.76.140

[1/4] Checking if VM already exists...
  Running: gcloud compute instances describe nlp-classifier-vm --zone=us-central1-a
  Exit code: 1
OK - No existing VM found

[2/4] Creating firewall rules...
  Checking firewall rule: allow-nlp-api
  - allow-nlp-api already exists (port 8000)
  Checking firewall rule: allow-nlp-ui
  - allow-nlp-ui already exists (port 8501)
  Checking firewall rule: allow-http
  - allow-http already exists (port 80)
  Checking firewall rule: allow-https
  - allow-https already exists (port 443)
OK - Firewall rules configured

[3/4] Creating VM instance...
This will take 2-3 minutes...

Saving startup script to: C:\Users\dhair\AppData\Local\Temp\tmpCC2F.tmp
Startup script saved (762 bytes)

Creating VM with command:
  gcloud compute instances create nlp-classifier-vm
    --zone=us-central1-a
    --machine-type=e2-standard-2
    --image-family=ubuntu-2204-lts
    --boot-disk-size=50GB
    --boot-disk-type=pd-ssd
    --address=35.232.76.140
    --tags=http-server,https-server,allow-nlp-api,allow-nlp-ui

Executing VM creation...
Created [https://www.googleapis.com/compute/v1/projects/mnist-k8s-pipeline/zones/us-central1-a/instances/nlp-classifier-vm].
WARNING: Some requests generated warnings:
 - Disk size: '50 GB' is larger than image size: '10 GB'. You might need to resize the root repartition manually if the operating system does not support automatic resizing. See https://cloud.google.com/compute/docs/disks/add-persistent-disk#resize_pd for details.

NAME               ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
nlp-classifier-vm  us-central1-a  e2-standard-2               10.128.0.12  35.232.76.140  RUNNING
VM creation command completed with exit code: 0
Cleaning up temporary startup script...
OK - VM created successfully!

[4/4] Waiting for VM to be ready...
Waiting for startup script to complete (2-3 minutes)...
  Attempt 1/30...
OK - SSH connection established

========================================
PHASE 2 COMPLETE!
========================================

VM Details:
  Name:        nlp-classifier-vm
  Zone:        us-central1-a
  External IP: 35.232.76.140
  Machine:     e2-standard-2 (2 vCPU, 8GB RAM)
  Disk:        50GB SSD

Access URLs (after deployment):
  API:  http://
  UI:   http://
  Docs: http:///docs

SSH Command:
  gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

Firewall Rules Created:
  - Port 22:   SSH (default)
  - Port 80:   HTTP
  - Port 443:  HTTPS
  - Port 8000: API
  - Port 8501: UI

Next Steps:
  1. Wait 2-3 minutes for startup script to complete
  2. SSH into VM to verify Docker installation
  3. Proceed to Phase 3: Setup VM Environment

Ready to proceed to Phase 3?
PS C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP> # 🚀 Cloud NLP Text Classification on GCP

An end-to-end text classification pipeline for hate speech detection, demonstrating cloud computing, deep neural networks, and performance analysis.

## 🎉 **NEW: GCP Cloud Deployment In Progress!** 

🚀 **Cloud Deployment Status:** Phase 2/14 Complete (14%)  
☁️ **GCP VM Created:** nlp-classifier-vm  
🌐 **External IP:** 35.232.76.140  
✅ **Local Testing:** 100% Complete (326+ tests passed)  
📊 **Model Accuracy:** 96.57% (DistilBERT)

**Deployment Progress:**
- ✅ Phase 1: GCP Project Setup (Complete)
- ✅ Phase 2: VM Creation & Firewall (Complete)
- 🔄 Phase 3: VM Environment Setup (In Progress)
- 📖 [View Full Progress](GCP_DEPLOYMENT_PROGRESS.md) - Detailed deployment status

**Quick Start:**
- 📖 [GCP Deployment Plan](GCP_VM_DOCKER_DEPLOYMENT_PLAN.md) - Complete deployment guide
- 📊 [Deployment Progress](GCP_DEPLOYMENT_PROGRESS.md) - Real-time progress tracking
- 📚 [Local Usage Guide](docs/USING_YOUR_TRAINED_MODELS.md) - Local deployment options

---

## 📋 Project Overview

This project implements a production-grade hate speech classification system with:

- **Classical ML Baselines**: TF-IDF + Logistic Regression/SVM (85-88% accuracy, <2ms inference)
- **Transformer Model**: Fine-tuned DistilBERT (96.29% accuracy, 17-20ms inference)
- **Multi-Model API**: FastAPI server with dynamic model switching (zero downtime!)
- **Containerization**: Docker with all 3 models included
- **Cloud Training**: GCP GPU VM support for efficient model training
- **Cloud Deployment**: Google Cloud Platform (Cloud Run) - Ready for deployment
- **Performance Analysis**: Offline metrics, online latency/throughput, cost analysis
- **Testing Suite**: Comprehensive unit and integration tests (326+ tests, 100% pass rate)

### 🎯 Project Status

#### **Local Development & Testing** ✅
| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1**: Data Pipeline | ✅ Complete | Dataset download, preprocessing, train/val/test splits |
| **Phase 2**: Baseline Models | ✅ Complete | TF-IDF + LogReg/SVM with full evaluation |
| **Phase 3**: Transformer Training | ✅ Complete | DistilBERT fine-tuning (96.57% accuracy!) |
| **Phase 4**: FastAPI Server | ✅ Complete | Multi-model API with dynamic switching |
| **Phase 5**: Dockerization | ✅ Complete | Production-ready Docker with all models |
| **Phase 6**: End-to-End Testing | ✅ Complete | 326+ tests, 100% pass rate |

**Local Progress**: ✅ **10/10 Phases Complete (100%)** - **PRODUCTION READY!**

#### **GCP Cloud Deployment** 🔄
| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1**: GCP Project Setup | ✅ Complete | APIs enabled, static IP reserved (35.232.76.140) |
| **Phase 2**: VM Creation | ✅ Complete | e2-standard-2 VM running, firewall configured |
| **Phase 3**: VM Environment Setup | 🔄 In Progress | Docker installation, directory setup |
| **Phase 4**: File Transfer | ⏳ Pending | Upload code and models (3-5GB) |
| **Phase 5**: Docker Compose Config | ⏳ Pending | Production compose file with volumes |
| **Phase 6**: Build & Deploy | ⏳ Pending | Build images, start services |
| **Phase 7**: External Testing | ⏳ Pending | Test API/UI from internet |
| **Phase 8+**: Operations | ⏳ Pending | Auto-start, monitoring, backups, security |

**Cloud Progress**: 🔄 **2/14 Phases Complete (14%)** - **IN PROGRESS**

## 🏗️ Architecture

```
Data Pipeline → Model Training → Evaluation → API Deployment → Cloud
     ↓              ↓               ↓            ↓              ↓
  Raw CSV    Baselines +      Accuracy      FastAPI      GCP Cloud Run
             Transformer      F1 Score      + Docker
```

## 📁 Project Structure

```
cloud-nlp-classification-gcp/
├── src/
│   ├── data/              # Data processing modules
│   ├── models/            # Model training & evaluation
│   └── api/               # FastAPI server
├── data/
│   ├── raw/               # Original datasets
│   └── processed/         # Train/val/test splits
├── models/
│   ├── baselines/         # Saved baseline models
│   └── transformer/       # Saved DistilBERT model
├── config/                # YAML configuration files
├── scripts/               # Executable scripts
├── notebooks/             # Jupyter notebooks (EDA)
├── tests/                 # Unit & integration tests
├── Dockerfile             # Container definition
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Dataset

```bash
# Download hate speech dataset from Hugging Face
python scripts/download_dataset.py
```

This will download and prepare the hate speech dataset at `data/raw/dataset.csv`.

### 3. Preprocess Data

```bash
# Cross-platform Python script (Recommended)
python run_preprocess.py

# Or run directly:
python -m src.data.preprocess

# Or use platform-specific scripts:
# Windows: .\scripts\run_preprocess_local.ps1
# Linux/Mac: bash scripts/run_preprocess_local.sh
```

This creates train/val/test splits in `data/processed/`.

### 4. Train Baseline Models

```bash
# Cross-platform Python script (Recommended)
python run_baselines.py

# Or run directly:
python -m src.models.train_baselines

# Or use platform-specific scripts:
# Windows: .\scripts\run_baselines_local.ps1
# Linux/Mac: bash scripts/run_baselines_local.sh
```

### 5. Train Transformer Model

#### Local Training (Quick Testing - 3 epochs)

```bash
# Cross-platform Python script (Recommended)
python run_transformer.py

# Or run directly:
python -m src.models.transformer_training

# Or use platform-specific scripts:
# Windows: .\scripts\run_transformer_local.ps1
# Linux/Mac: bash scripts/run_transformer_local.sh
```

**Local Training Specs:**
- Epochs: 3 (quick testing)
- Batch Size: 32
- Max Sequence Length: 128
- Expected Accuracy: 85-88%
- Training Time: 1-2 hours (CPU), 15-25 min (GPU)

**Note:** Transformer training requires a GPU for reasonable speed. Set `device: "cpu"` in `config/config_transformer.yaml` if GPU is unavailable.

#### Cloud Training (Production - 10 epochs)

For production-quality models with optimized settings:

```bash
# Using cloud configuration locally (if you have a GPU)
python -m src.models.transformer_training \
  --config config/config_transformer_cloud.yaml \
  --mode cloud \
  --fp16

# Or use the cloud training script:
# Windows: .\scripts\run_transformer_cloud.ps1
# Linux/Mac: bash scripts/run_gcp_training.sh
```

**Cloud Training Specs:**
- Epochs: 10 (production quality)
- Batch Size: 64
- Max Sequence Length: 256
- FP16: Enabled (mixed precision)
- LR Scheduler: Cosine with warmup
- Expected Accuracy: 90-93%
- Training Time: 20-40 min (T4 GPU), 15-25 min (V100)

#### Advanced Training Options

```bash
# Override specific parameters
python -m src.models.transformer_training \
  --config config/config_transformer.yaml \
  --mode local \
  --epochs 5 \
  --batch-size 32 \
  --learning-rate 3e-5 \
  --fp16 \
  --output-dir models/transformer/custom

# Disable early stopping
python -m src.models.transformer_training \
  --no-early-stopping

# Use different learning rate scheduler
# Edit config YAML: lr_scheduler.type = "cosine" | "linear" | "polynomial"
```

**Advanced Training Features:**
- ✅ **Early Stopping**: Configurable patience based on validation F1/loss
- ✅ **LR Schedulers**: Linear, cosine, cosine_with_restarts, polynomial, constant, constant_with_warmup
- ✅ **Mixed Precision (FP16)**: Faster GPU training with automatic fallback
- ✅ **Gradient Accumulation**: Effective larger batch sizes on limited memory
- ✅ **Warmup Steps**: Configurable warmup ratio or fixed steps
- ✅ **DataLoader Optimizations**: Multi-worker loading with pin_memory
- ✅ **CLI Overrides**: Override any config parameter via command line
- ✅ **Automatic Best Model Selection**: Saves best checkpoint based on validation metrics
- ✅ **Comprehensive Logging**: Training progress, metrics, and timing information

### 6. Run API Server (Local)

```bash
# Start FastAPI server
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

# Or use the shell script:
bash scripts/run_api_local.sh
```

Test the API:

```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'
```

### 7. Run Tests

```bash
# Run all tests with the universal test runner
python run_tests.py

# Or use pytest directly
pytest tests/ -v

# Run specific test categories
pytest tests/test_basic_imports.py      # Import tests
pytest tests/test_api.py                # API tests
pytest tests/test_baseline_inference.py # Baseline model tests
pytest tests/test_advanced_training.py  # Training configuration tests

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Suite Coverage:**
- ✅ Import validation (6 tests)
- ✅ API endpoints (health, predict, docs)
- ✅ Model loading and inference
- ✅ Configuration validation
- ✅ Error handling
- ✅ Pydantic V2 compliance (zero deprecation warnings)

## 🐳 Docker Deployment

### Multi-Model Support 🎯

The Docker image now includes **3 models** with dynamic switching:

| Model | Type | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| **distilbert** | Transformer | ~50ms | 90-93% | Best accuracy |
| **logistic_regression** | Baseline | ~5ms | 85-88% | Fast inference |
| **linear_svm** | Baseline | ~5ms | 85-88% | Robust predictions |

**Key Features:**
- ✅ All models included in single Docker image
- ✅ Switch models via API without restarting container
- ✅ Choose default model via environment variable
- ✅ Production-ready with health checks and monitoring

### Prerequisites

Before building the Docker image, ensure you have:

1. **Docker installed**: [Install Docker](https://docs.docker.com/get-docker/)
2. **Trained models**: 
   - Transformer: `models/transformer/distilbert/`
   - Baselines: `models/baselines/*.joblib`
3. **Sufficient disk space**: ~2-3 GB for the Docker image

### Build Docker Image

```bash
# Build the image (this may take 5-10 minutes)
docker build -t cloud-nlp-classifier .

# Optional: Build with a specific tag
docker build -t cloud-nlp-classifier:v1.0 .

# Optional: Build with no cache (for clean rebuild)
docker build --no-cache -t cloud-nlp-classifier .
```

**Build Details:**
- Base image: `python:3.11-slim`
- Image size: ~2 GB (includes PyTorch, transformers, and model weights)
- Build time: 5-10 minutes (depending on network speed)

### Run Docker Container

**Option 1: Using Docker Compose (Recommended)**

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Option 2: Using Docker CLI**

```bash
# Run with default model (DistilBERT - best accuracy)
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier

# Run with fast model (Logistic Regression - 10x faster)
docker run -d -p 8000:8000 -e DEFAULT_MODEL=logistic_regression --name nlp-api cloud-nlp-classifier

# Run with Linear SVM model
docker run -d -p 8000:8000 -e DEFAULT_MODEL=linear_svm --name nlp-api cloud-nlp-classifier

# Run with custom port mapping
docker run -d -p 9000:8000 --name nlp-api cloud-nlp-classifier

# Run with debug logging
docker run -d -p 8000:8000 -e LOG_LEVEL=debug --name nlp-api cloud-nlp-classifier
```

**Environment Variables:**
- `DEFAULT_MODEL`: Choose startup model (`distilbert`, `logistic_regression`, `linear_svm`)
- `LOG_LEVEL`: Logging level (`INFO`, `DEBUG`, `WARNING`, `ERROR`)
```

**Docker Compose Configurations:**
- `docker-compose.yml` - Standard deployment with health checks and resource limits
- `docker-compose.dev.yml` - Development with hot-reload, debug logging, and volume mounts
- `docker-compose.prod.yml` - Production with 4 workers, optimized resources, and restart policies

**Docker Compose Usage:**
```bash
# Standard deployment
docker-compose up -d

# Development mode (with hot-reload)
docker-compose -f docker-compose.dev.yml up

# Production mode (multiple workers)
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Test the Containerized API

```bash
# Health check (shows current model and available models)
curl http://localhost:8000/health

# List all available models
curl http://localhost:8000/models

# Make a prediction with current model
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Switch to a different model (without restarting container!)
curl -X POST http://localhost:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# Make prediction with new model
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Access interactive API documentation
# Open in browser: http://localhost:8000/docs
```

### Docker Management Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs nlp-api

# Follow logs in real-time
docker logs -f nlp-api

# Stop the container
docker stop nlp-api

# Start a stopped container
docker start nlp-api

# Remove the container
docker rm nlp-api

# Remove the image
docker rmi cloud-nlp-classifier

# View image details
docker inspect cloud-nlp-classifier

# Check image size
docker images cloud-nlp-classifier
```

### Docker Health Check

The container includes a built-in health check that runs every 30 seconds:

```bash
# Check container health status
docker inspect --format='{{.State.Health.Status}}' nlp-api

# View health check logs
docker inspect --format='{{json .State.Health}}' nlp-api | python -m json.tool
```

Health states:
- `starting`: Container is starting up (first 40 seconds grace period)
- `healthy`: API is responding correctly to /health endpoint
- `unhealthy`: API failed 3 consecutive health checks

**Health Check Configuration:**
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start Period: 40 seconds (allows model loading time)

### Troubleshooting

**Container won't start:**
```bash
# Check logs for errors
docker logs nlp-api

# Run interactively to see startup issues
docker run -it -p 8000:8000 cloud-nlp-classifier
```

**Port already in use:**
```bash
# Use a different port
docker run -p 8001:8000 cloud-nlp-classifier
```

**Out of memory:**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or run with memory limit
docker run -p 8000:8000 --memory="2g" cloud-nlp-classifier
```

**Model not found error:**
```bash
# Ensure the model is trained before building the image
python run_transformer.py

# Verify model files exist
ls -la models/transformer/distilbert/
```

## ☁️ GCP Cloud Training

### Why Train on GCP?

Training transformer models on cloud GPUs offers significant advantages:
- **Speed**: 10-50x faster than CPU training
- **Scalability**: Access to powerful GPUs (T4, V100, A100)
- **Cost-Effective**: Pay only for training time (~$0.35-$2.50/hour)
- **No Local Setup**: No need for expensive local GPU hardware

### GCP GPU VM Setup

#### 1. Create a GCP GPU VM Instance

```bash
# Set your GCP project
export PROJECT_ID=your-gcp-project-id
gcloud config set project $PROJECT_ID

# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Create a GPU VM instance (NVIDIA T4 GPU)
gcloud compute instances create nlp-training-vm \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --boot-disk-size=100GB \
  --maintenance-policy=TERMINATE \
  --metadata="install-nvidia-driver=True"

# Alternative: Use V100 for faster training (more expensive)
# --machine-type=n1-standard-8 \
# --accelerator=type=nvidia-tesla-v100,count=1
```

**GPU Options & Pricing (us-central1):**
- **T4** (16GB): ~$0.35/hour - Good for DistilBERT
- **V100** (16GB): ~$2.48/hour - Faster training
- **A100** (40GB): ~$3.67/hour - Largest models

#### 2. SSH into the VM

```bash
# SSH into the instance
gcloud compute ssh nlp-training-vm --zone=us-central1-a

# Verify GPU is available
nvidia-smi
```

#### 3. Setup Training Environment

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git
cd CLOUD-NLP-CLASSIFIER-GCP

# Run the setup script (installs dependencies, downloads data)
bash scripts/setup_gcp_training.sh

# This script will:
# - Install Python 3.11 and dependencies
# - Install CUDA drivers (if needed)
# - Create virtual environment
# - Install PyTorch with GPU support
# - Download and preprocess dataset
```

#### 4. Start Training

```bash
# Activate virtual environment
source venv/bin/activate

# Start training with cloud configuration
bash scripts/run_gcp_training.sh

# Or run directly with custom settings
python -m src.models.transformer_training \
  --config config/config_transformer_cloud.yaml \
  --mode cloud \
  --fp16 \
  --epochs 10 \
  --batch-size 64
```

**Training will:**
- Use optimized cloud settings (FP16, larger batches)
- Save model to `models/transformer/distilbert_cloud/`
- Log training progress to `training.log`
- Take approximately 20-40 minutes on T4 GPU

#### 5. Monitor Training

```bash
# In another terminal, SSH and monitor
gcloud compute ssh nlp-training-vm --zone=us-central1-a

# Watch GPU usage
watch -n 1 nvidia-smi

# Follow training logs
tail -f models/transformer/distilbert_cloud/training.log
```

#### 6. Download Trained Model

```bash
# From your local machine, download the trained model
gcloud compute scp --recurse \
  nlp-training-vm:~/CLOUD-NLP-CLASSIFIER-GCP/models/transformer/distilbert_cloud \
  ./models/transformer/ \
  --zone=us-central1-a

# Or use Google Cloud Storage (recommended for large models)
# On VM: Upload to GCS
gsutil -m cp -r models/transformer/distilbert_cloud gs://your-bucket-name/models/

# On local: Download from GCS
gsutil -m cp -r gs://your-bucket-name/models/distilbert_cloud ./models/transformer/
```

#### 7. Stop/Delete VM (Important!)

```bash
# Stop the VM (can restart later, still charges for disk)
gcloud compute instances stop nlp-training-vm --zone=us-central1-a

# Delete the VM (no charges, but need to recreate)
gcloud compute instances delete nlp-training-vm --zone=us-central1-a
```

**💡 Cost Saving Tips:**
- Delete VM immediately after training completes
- Use preemptible instances for 60-80% cost savings (may be interrupted)
- Use Cloud Storage for model artifacts instead of large boot disks
- Monitor training with early stopping to avoid unnecessary epochs
- Use T4 GPUs for DistilBERT (V100/A100 overkill for this model size)
- Set up billing alerts to avoid unexpected charges

**Estimated Training Costs (10 epochs):**
- T4 GPU (30-40 min): ~$0.20-$0.25
- V100 GPU (15-25 min): ~$0.60-$1.00
- A100 GPU (10-15 min): ~$0.60-$0.90

### Local vs Cloud Configuration Comparison

| Setting | Local (Testing) | Cloud (Production) |
|---------|----------------|-------------------|
| **Batch Size** | 32 | 64 |
| **Epochs** | 3 | 10 |
| **Max Seq Length** | 128 | 256 |
| **FP16** | Optional | Enabled |
| **Gradient Accumulation** | 1 | 2 |
| **LR Scheduler** | Linear | Cosine |
| **Early Stopping** | 3 patience | 5 patience |
| **Training Time** | 1-2 hours (CPU) | 20-40 min (T4 GPU) |
| **Expected Accuracy** | 85-88% | 90-93% |
| **Expected F1 Score** | 0.82-0.85 | 0.88-0.91 |

## ☁️ GCP Deployment (Inference)

### Prerequisites

1. GCP project with billing enabled
2. `gcloud` CLI installed and authenticated
3. Enable required APIs:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

### Deploy to Cloud Run

```bash
# Set project ID
export PROJECT_ID=your-gcp-project-id

# Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/$PROJECT_ID/cloud-nlp-classifier

# Deploy to Cloud Run
gcloud run deploy cloud-nlp-classifier \
  --image gcr.io/$PROJECT_ID/cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

## 📊 Performance Analysis

### Offline Evaluation

Models are evaluated on:
- **Accuracy**: Overall correctness
- **F1 Score**: Macro and weighted F1
- **Precision/Recall**: Per-class performance
- **ROC-AUC**: For binary classification

### Online Evaluation

API performance metrics:
- **Latency**: p50, p95, p99 response times
- **Throughput**: Requests per second
- **Cold Start**: Initial request latency

### Cost Analysis

- **Training Cost**: GPU VM hours
- **Inference Cost**: Cloud Run pricing per 1K requests
- **Storage Cost**: Model artifacts in Artifact Registry

## 🔧 Configuration

### Baseline Models (`config/config_baselines.yaml`)

```yaml
vectorizer:
  type: "tfidf"
  max_features: 10000
  ngram_range: [1, 2]

logistic_regression:
  C: 1.0
  max_iter: 1000
  class_weight: "balanced"
```

### Transformer Model (`config/config_transformer.yaml`)

```yaml
model:
  name: "distilbert-base-uncased"
  max_seq_length: 128

training:
  train_batch_size: 16
  learning_rate: 2.0e-5
  num_train_epochs: 3
  early_stopping:
    enabled: true
    patience: 3
```

## 📈 Expected Results

### Baseline Models (TF-IDF + LogReg/SVM)
- **Accuracy**: 75-85%
- **F1 Score**: 0.70-0.80 (macro)
- **Training Time**: <5 minutes
- **Inference Latency**: <10ms per sample
- **Model Size**: <50 MB

### Transformer Model (DistilBERT)

**Local Training (3 epochs):**
- **Accuracy**: 85-88%
- **F1 Score**: 0.82-0.85 (macro)
- **Training Time**: 1-2 hours (CPU), 15-25 min (GPU)
- **Inference Latency**: 45-60ms (p50), 80-100ms (p95)
- **Model Size**: ~250 MB

**Cloud Training (10 epochs):**
- **Accuracy**: 90-93%
- **F1 Score**: 0.88-0.91 (macro)
- **Training Time**: 20-40 min (T4 GPU)
- **Inference Latency**: 45-60ms (p50), 80-100ms (p95)
- **Model Size**: ~250 MB

### API Performance
- **Startup Time**: 5-8 seconds (model loading)
- **Memory Usage**: ~1.2 GB (active inference)
- **Throughput**: 20-50 requests/second (single worker)
- **Cold Start**: <10 seconds (Docker container)

## 🧪 Development Workflow

1. **Data Exploration**: Use `notebooks/eda.ipynb` for EDA (optional)
2. **Experiment**: Modify configs in `config/` or use CLI overrides
3. **Train Locally**: Quick iteration with 3 epochs
4. **Train on Cloud**: Production training with 10 epochs on GCP GPU VM
5. **Evaluate**: Check metrics, logs, and model performance
6. **Test API**: Run locally with `uvicorn` or Docker
7. **Run Tests**: Validate with comprehensive test suite
8. **Deploy**: Docker → GCP Cloud Run
9. **Monitor**: Track performance, latency, and costs

## 🛠️ Development Tools

### Cross-Platform Scripts
All major operations have universal Python scripts that work on Windows, Linux, and Mac:
- `run_preprocess.py` - Data preprocessing
- `run_baselines.py` - Baseline model training
- `run_transformer.py` - Transformer training
- `run_tests.py` - Test suite execution

### Platform-Specific Scripts
Alternative scripts for shell/PowerShell users:
- `scripts/*.sh` - Bash scripts (Linux/Mac)
- `scripts/*.ps1` - PowerShell scripts (Windows)

### Configuration Files
- `config/config_baselines.yaml` - Baseline model hyperparameters
- `config/config_transformer.yaml` - Local training config (3 epochs)
- `config/config_transformer_cloud.yaml` - Cloud training config (10 epochs)

## 📝 Course Relevance

### Cloud Computing ☁️
- GCP services (Cloud Run, Artifact Registry)
- Containerization and orchestration
- Auto-scaling and load balancing

### Deep Neural Networks 🧠
- Transformer architecture (DistilBERT)
- Transfer learning and fine-tuning
- Optimization techniques (early stopping, LR scheduling)

### Performance Analysis 📊
- Offline metrics (accuracy, F1, ROC-AUC)
- Online metrics (latency, throughput)
- Cost-benefit analysis

## 🤝 Contributing

This is a course project. For team collaboration:

1. Create feature branches
2. Make changes and test locally
3. Submit pull requests for review
4. Merge after approval

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- **Dataset**: Hate Speech Offensive dataset from Hugging Face (24,783 samples)
- **Model**: DistilBERT from Hugging Face Transformers
- **Frameworks**: FastAPI, PyTorch, Transformers, scikit-learn
- **Infrastructure**: Docker, GCP (Cloud Run, Compute Engine)
- **Testing**: pytest, Pydantic V2

## 📚 Additional Documentation

Comprehensive guides available in the `docs/` directory:
- `MULTI_MODEL_DOCKER_GUIDE.md` - **NEW!** Multi-model Docker deployment (500+ lines)
- `DOCKER_GUIDE.md` - Complete Docker documentation (650+ lines)
- `DOCKER_COMPOSE_GUIDE.md` - Docker Compose best practices (600+ lines)
- `PHASE10_ADVANCED_TRAINING_SUMMARY.md` - Advanced training features
- `CROSS_PLATFORM_GUIDE.md` - Cross-platform development guide
- `PROJECT_STATUS.md` - Current project status and metrics

## 📞 Contact

For questions or issues, please open an issue in the repository.

---

**Built with ❤️ for cloud-based NLP classification**
