# 🚀 Cloud NLP Text Classification on GCP

An end-to-end text classification pipeline for hate speech detection, demonstrating cloud computing, deep neural networks, and performance analysis.

## 📋 Project Overview

This project implements a production-grade hate speech classification system with:

- **Classical ML Baselines**: TF-IDF + Logistic Regression/SVM
- **Transformer Model**: Fine-tuned DistilBERT
- **REST API**: FastAPI server for inference
- **Containerization**: Docker for deployment
- **Cloud Deployment**: Google Cloud Platform (Cloud Run)
- **Performance Analysis**: Offline metrics, online latency/throughput, cost analysis

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

```bash
# Cross-platform Python script (Recommended)
python run_transformer.py

# Or run directly:
python -m src.models.transformer_training

# Or use the shell script:
bash scripts/run_transformer_local.sh
```

**Note:** Transformer training requires a GPU for reasonable speed. Set `device: "cpu"` in `config/config_transformer.yaml` if GPU is unavailable.

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
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_basic_imports.py
```

## 🐳 Docker Deployment

### Prerequisites

Before building the Docker image, ensure you have:

1. **Docker installed**: [Install Docker](https://docs.docker.com/get-docker/)
2. **Trained model**: The transformer model must be trained and saved at `models/transformer/distilbert/`
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

```bash
# Run in foreground (see logs in terminal)
docker run -p 8000:8000 cloud-nlp-classifier

# Run in background (detached mode)
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier

# Run with custom port mapping
docker run -p 9000:8000 cloud-nlp-classifier

# Run with environment variables (if needed)
docker run -p 8000:8000 -e LOG_LEVEL=debug cloud-nlp-classifier
```

### Test the Containerized API

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
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
```

Health states:
- `starting`: Container is starting up (first 40 seconds)
- `healthy`: API is responding correctly
- `unhealthy`: API failed to respond to health checks

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

## ☁️ GCP Deployment

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

### Baseline Models
- **Accuracy**: 75-85%
- **Training Time**: <5 minutes
- **Inference Latency**: <10ms per sample

### Transformer Model
- **Accuracy**: 85-95%
- **Training Time**: 30-60 minutes (GPU)
- **Inference Latency**: 50-100ms per sample

## 🧪 Development Workflow

1. **Data Exploration**: Use `notebooks/eda.ipynb` for EDA
2. **Experiment**: Modify configs in `config/`
3. **Train**: Run training scripts
4. **Evaluate**: Check metrics and logs
5. **Deploy**: Test locally → Docker → GCP
6. **Monitor**: Track performance and costs

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

- **Dataset**: Hate Speech Offensive dataset from Hugging Face
- **Model**: DistilBERT from Hugging Face Transformers
- **Framework**: FastAPI, PyTorch, scikit-learn

## 📞 Contact

For questions or issues, please open an issue in the repository.

---

**Built with ❤️ for cloud-based NLP classification**
