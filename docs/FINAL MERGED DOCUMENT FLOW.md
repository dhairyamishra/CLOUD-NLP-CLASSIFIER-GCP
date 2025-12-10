# CLOUD-NLP-CLASSIFIER-GCP

**Cloud NLP Hate & Toxicity Classifier – Production-Ready, Cloud-Deployable**

This repo implements a **multi-model text classification service** for hate speech and toxicity detection, with:

* **Baselines**: TF-IDF + Logistic Regression / Linear SVM (≈93–95% accuracy, sub-millisecond latency)
* **Transformer**: Fine-tuned DistilBERT (≈96.5% accuracy)
* **Toxicity Extension**: Multi-label DistilBERT with 6 Jigsaw toxicity heads
* **FastAPI Backend**: Multi-model API with runtime model switching
* **Streamlit UI**: Chat-style web interface with charts and visual indicators
* **Docker & Docker Compose**: Single/multi-container images for API + UI
* **GCP Deployment**: Fully automated VM + Docker deployment script, plus Cloud Run / GKE plans
* **Testing & Performance**: 10-phase test plan, 326+ tests, latency & memory validated in Docker

This README is synced with the canonical `PROJECT_FLOW.md` documents that narrate the end-to-end architecture, training, deployment, and testing of the system.

---

## 1. Final Status Snapshot

### 1.1 Local System

From the consolidated project flow and test reports:

* ✅ **Data pipeline**: preprocessing + train/val/test splits
* ✅ **Baselines**: Logistic Regression & Linear SVM (TF-IDF)
* ✅ **Transformer**: DistilBERT hate classifier
* ✅ **Toxicity Model**: DistilBERT multi-head (6 labels)
* ✅ **FastAPI**: multi-model API with `/predict`, `/models`, `/models/switch`
* ✅ **Docker & Docker Compose**: backend + UI images and stacks
* ✅ **Streamlit UI**: chat-style interface on top of API
* ✅ **Testing**: 10-phase plan, 326+ tests, 100% passing
* ✅ **Performance**: all latency/memory targets exceeded with margin

Local project status: **fully implemented & production-ready**.

### 1.2 Cloud System (GCP)

Current production deployment (as of the latest docs):

* **Project**: `mnist-k8s-pipeline`
* **VM**: `nlp-classifier-vm` (e2-standard-2, 2 vCPU, 8 GB RAM, 50 GB SSD)
* **Region / Zone**: `us-central1 / us-central1-a`
* **Bucket**: `gs://nlp-classifier-models`
* **Primary script**: `scripts/gcp-complete-deployment.ps1`
* **Container**: `nlp-api` (FastAPI + multi-model inference) on port **8000**

**Final verification:**

* Bucket created and populated (inference-only model subset)
* VM created & configured (Docker installed, dirs under `/opt/nlp-classifier`)
* Repo cloned & kept up to date on VM
* Models downloaded from GCS
* Docker image built on VM
* Container running and healthy
* External `/health`, `/predict`, `/models`, `/docs` all verified

The script can now deploy (or re-deploy) the API in a **single PowerShell command**.

---

## 2. High-Level Architecture

```mermaid
graph TD
    subgraph Data & Training
        A[Raw Dataset<br/>data/raw] --> B[Preprocessing<br/>run_preprocess.py]
        B --> C1[Baselines<br/>LogReg & Linear SVM]
        B --> C2[DistilBERT Hate Classifier]
        B --> C3[Multi-Head Toxicity Model]
        C1 --> D1[models/baselines/]
        C2 --> D2[models/transformer/distilbert/]
        C3 --> D3[models/toxicity_multi_head/]
    end

    subgraph Serving
        D1 --> E[FastAPI Server<br/>src/api/server.py]
        D2 --> E
        D3 --> E
        E --> F[/predict,<br/>/models,<br/>/models/switch]
    end

    subgraph Packaging
        E --> G[Backend Docker Image<br/>Dockerfile]
        H[Streamlit UI<br/>src/ui/streamlit_app.py] --> I[UI Docker Image<br/>Dockerfile.streamlit]
    end

    subgraph Deployment
        G --> J1[GCP VM + Docker/Compose]
        G --> J2[Cloud Run (API)]
        I --> J3[Cloud Run (UI)]
    end

    subgraph UI
        F --> H
        H --> User[End User]
    end

    User --> H
```

This mirrors the canonical `PROJECT_FLOW.md` variants, unifying data, training, APIs, Docker, and cloud deployment into a single story.

---

## 3. Project Structure

> Exact filenames may vary slightly; this is the conceptual layout.

```text
CLOUD-NLP-CLASSIFIER-GCP/
├── src/
│   ├── data/
│   │   ├── preprocess.py
│   │   └── dataset_utils.py
│   ├── models/
│   │   ├── baselines.py
│   │   ├── transformer_training.py
│   │   ├── train_toxicity.py
│   │   └── multi_head_model.py
│   ├── api/
│   │   └── server.py           # FastAPI app
│   └── ui/
│       ├── streamlit_app.py
│       ├── components/
│       └── utils/
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   ├── baselines/
│   ├── transformer/
│   │   └── distilbert/
│   └── toxicity_multi_head/
├── config/
│   ├── config_baselines.yaml
│   ├── config_transformer.yaml
│   ├── config_transformer_cloud.yaml
│   └── config_toxicity.yaml
├── scripts/
│   ├── run_preprocess_local.{sh,ps1}
│   ├── run_baselines_local.{sh,ps1}
│   ├── run_transformer_local.{sh,ps1}
│   ├── run_gcp_training.sh
│   ├── run_api_local.{sh,ps1}
│   ├── run_streamlit_local.{sh,ps1}
│   ├── run_streamlit.py
│   └── gcp-complete-deployment.ps1
├── tests/
│   ├── test_data_*.py
│   ├── test_baselines_*.py
│   ├── test_transformer_*.py
│   ├── test_api_*.py
│   └── docker_*_tests.py
├── Dockerfile
├── Dockerfile.streamlit
├── docker-compose*.yml
├── MODEL_VERSION.json
├── PROJECT_FLOW.md
└── docs/
    ├── training/
    ├── docker/
    ├── deployment/
    └── testing/
```

---

## 4. Models & Training

### 4.1 Data & Preprocessing

* Raw hate/offensive speech dataset downloaded into `data/raw/`
* `src/data/preprocess.py` cleans text, validates labels, and produces:

  * `data/processed/train.csv`
  * `data/processed/val.csv`
  * `data/processed/test.csv`
* Splits are stratified and reproducible via seeded random splits.

Run:

```bash
# Linux / Mac
bash scripts/run_preprocess_local.sh

# Windows
.\scripts\run_preprocess_local.ps1
```

Or use the cross-platform Python entrypoint if provided (`run_preprocess.py`).

---

### 4.2 Baseline Models (Logistic Regression & Linear SVM)

* Implemented as `BaselineTextClassifier` (TF-IDF + scikit-learn classifiers). 
* Two main models:

  * Logistic Regression (`logistic_regression_tfidf.joblib`)
  * Linear SVM (`linear_svm_tfidf.joblib`)
* Typical performance (final tests):

  * Accuracy: ≈93–95%
  * Macro-F1: ≈0.89–0.91
  * Latency in Docker: ~0.6–0.7 ms per request.

Train:

```bash
# Linux / Mac
bash scripts/run_baselines_local.sh

# Windows
.\scripts\run_baselines_local.ps1
```

Artifacts are saved under `models/baselines/`.

---

### 4.3 DistilBERT Hate Speech Classifier

* Base model: `distilbert-base-uncased`
* Labels: **Hate** vs **Non-Hate**
* Script: `src/models/transformer_training.py`
* Configs:

  * `config/config_transformer.yaml` – local / quick experiments
  * `config/config_transformer_cloud.yaml` – cloud / advanced training
* Features: early stopping, warmup + schedulers, gradient accumulation, optional FP16.

Typical training modes:

* **Fast / Dev**:

  * Shorter max sequence length, fewer epochs (~1–3)
  * Goal: full pipeline smoke test in minutes
* **Full-scale / Production**:

  * Longer sequences (e.g. 256–512 tokens)
  * 10+ epochs with early stopping
  * GPU + FP16 for speed and cost efficiency

Reported performance:

* Accuracy: ≈96.3–96.6%
* Latency in container: ≈8–10 ms avg locally, ≈50–60 ms on the GCP CPU VM.

Train locally:

```bash
# Linux / Mac
bash scripts/run_transformer_local.sh

# Windows
.\scripts\run_transformer_local.ps1
```

Train on GCP GPU (example):

```bash
# On GPU VM, after setup
python -m src.models.transformer_training \
  --config config/config_transformer_cloud.yaml \
  --mode cloud \
  --fp16 \
  --epochs 10
```

---

### 4.4 Multi-Head Toxicity Model

* Architecture: DistilBERT encoder + **6 binary heads**:

  * `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`
* Implemented in `models/multi_head_model.py`
* Training script: `src/models/train_toxicity.py`
* Loss: BCEWithLogits per head, averaged across labels
* Artifacts saved under `models/toxicity_multi_head/`

This model is integrated into the multi-model Docker image and accessible via the API as the **toxicity** model option.

---

## 5. FastAPI Inference API

Main entrypoint: `src/api/server.py`

### 5.1 Endpoints

* `GET /`

  * Basic info: version, active model, available models
* `GET /health`

  * Health/readiness probe: verifies models loaded and API responsive
* `GET /models`

  * Lists all models known to the API with metadata (name, type, speed hints)
* `POST /models/switch`

  * Changes the **active model** in memory without restarting the container
* `POST /predict`

  * Request: `{"text": "..."}` (may support batch variants)
  * Response includes:

    * predicted label(s)
    * confidence score(s)
    * per-class probabilities
    * model used and inference time
* `GET /docs`, `GET /redoc`

  * Auto-generated API docs (OpenAPI / Swagger & ReDoc)

### 5.2 Multi-Model Serving

All four models are loaded and managed by a **ModelManager**:

* `distilbert` – high-accuracy primary model
* `toxicity` – 6-label toxicity classifier
* `logistic_regression` – fast baseline
* `linear_svm` – ultra-fast baseline

You can:

* Start with a default (via `DEFAULT_MODEL` env var), and
* Switch at runtime via `/models/switch`.

---

## 6. Streamlit UI

The Streamlit UI is a **chat-style frontend** on top of the API or directly on the models.

### 6.1 Features

* Sidebar:

  * Model selector (Baselines, DistilBERT, Toxicity)
  * Toggles: show probabilities, show inference time
  * Clear chat / reset state
* Main area:

  * Header with title and small stats
  * Conversation history (user vs model bubbles, timestamps)
  * Result cards:

    * Label badge (e.g., Non-Hate vs Hate)
    * Confidence + inference time
  * Probability bar charts (Plotly) for:

    * Binary hate vs non-hate
    * Toxicity heads (when using toxicity model)

UI fixes include:

* Stable chart label ordering (no jumping bars)
* Proper HTML escaping for labels, messages, and timestamps
* Clean bubble HTML structure and robust color/emoji mapping 

### 6.2 Running the UI

Local:

```bash
# Direct
streamlit run src/ui/streamlit_app.py --server.port 8501

# or via helper script
python run_streamlit.py
```

Docker (UI only):

```bash
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .
docker run -d -p 8501:8501 --name nlp-ui cloud-nlp-classifier-ui:latest
```

Or run via `docker-compose.ui.yml` to mount local models into the container.

---

## 7. Docker & Docker Compose

### 7.1 Backend Docker Image

**Dockerfile** builds the FastAPI backend with **all four models** baked in:

* Base: `python:3.11-slim`
* Installs system + Python dependencies
* Copies `src/`, `config/`, `models/`
* Creates non-root `appuser`
* Sets `PYTHONPATH=/app/src`
* Exposes port `8000`
* Adds `HEALTHCHECK` calling `/health`

Build & run:

```bash
docker build -t cloud-nlp-classifier:latest .
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier:latest
```

### 7.2 UI Docker Image

**Dockerfile.streamlit**:

* Base: `python:3.11-slim`
* Copies `src/ui` and `models/`
* Exposes port `8501`
* Healthcheck hitting Streamlit’s internal endpoint
* Entry script runs diagnostics (e.g., `check_models.py`) then starts Streamlit

Build & run:

```bash
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .
docker run -d -p 8501:8501 --name nlp-ui cloud-nlp-classifier-ui:latest
```

### 7.3 Docker Compose Stacks

Compose files support different scenarios:

* `docker-compose.yml` or `docker-compose.full.yml`

  * API + UI full stack
* `docker-compose.api-only.yml`

  * API container only
* `docker-compose.ui.yml`

  * UI only (assumes API at `http://localhost:8000`)
* `docker-compose.dev.yml`

  * Dev-focused stack with hot-reload and mounted code
* `docker-compose.prod.yml`

  * Production stack with multiple workers and tighter resource limits

Example full stack:

```bash
docker-compose up -d --build
# API: http://localhost:8000/docs
# UI:  http://localhost:8501
```

---

## 8. Model Versioning & GCS Layout

A small versioning system makes model pushes & deployments repeatable.

* `MODEL_VERSION.json` tracks:

  * Global version (semver)
  * Per-model versions and expected files
  * `model_prefix` used for GCS layout
* GCS structure:

```text
gs://nlp-classifier-models/
  <PREFIX>/
    MODEL_VERSION.json
    baselines/...
    transformer/distilbert/...
    toxicity_multi_head/...
```

The deployment script:

* Compares local and remote `MODEL_VERSION.json`
* Skips model upload if versions match (`-SkipModelUpload`)
* Uses `-ModelPrefix` and an optional auto-prefix mode for per-user or per-team segregation

---

## 9. GCP Deployment

There are **three** conceptual deployment paths; the main one implemented end-to-end is **VM + Docker**.

### 9.1 Option A – GCP VM + Docker (Current Production)

Primary script: **`scripts/gcp-complete-deployment.ps1`**.

Pipeline:

1. **Bucket Phase**

   * Create GCS bucket if missing
   * Upload models (optionally without checkpoints)
   * Verify files

2. **VM Phase**

   * Ensure VM exists and is running
   * Optionally create VM if absent (via phase-2 script)

3. **App Phase (on VM)**

   * SSH into VM
   * Clone or pull repo
   * Download models from GCS into `models/`
   * Build Docker image on VM
   * Stop/remove old container
   * Run new `nlp-api` container
   * Run health checks (localhost + external IP)

Flags:

* `-NoCheckpoints` – only upload final models (~770 MB instead of 12+ GB)
* `-SkipModelUpload` – reuse existing models in GCS
* `-SkipVMCreation` – assume VM already exists
* `-ProjectId`, `-BucketName`, `-ModelPrefix` – override defaults

Typical usage:

```powershell
# One-shot optimized deployment from local machine
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

Final status message includes external endpoints, e.g.:

* `http://<VM_IP>:8000/health`
* `http://<VM_IP>:8000/predict`
* `http://<VM_IP>:8000/docs`
* `http://<VM_IP>:8000/models`

### 9.2 Option B – Cloud Run (API and/or UI)

Using the same Docker images, you can deploy to Cloud Run:

```bash
# API
gcloud builds submit --tag gcr.io/$PROJECT_ID/cloud-nlp-classifier
gcloud run deploy cloud-nlp-api \
  --image gcr.io/$PROJECT_ID/cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi

# UI
gcloud builds submit -f Dockerfile.streamlit --tag gcr.io/$PROJECT_ID/cloud-nlp-ui
gcloud run deploy cloud-nlp-ui \
  --image gcr.io/$PROJECT_ID/cloud-nlp-ui \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

Cloud Run gives HTTPS, autoscaling, and “scale to zero” for cost efficiency.

### 9.3 Option C – GKE (Planned)

A detailed 13-phase GKE plan exists in the docs (PVCs, deployments, services, ingress, HPA, monitoring, security), but is not yet fully implemented. The current VM path is designed so the migration to GKE is **mechanical**, not a redesign.

---

## 10. Testing & Performance

### 10.1 10-Phase Test Plan

The project follows a 10-phase end-to-end testing plan: 

1. Environment setup
2. Data pipeline
3. Baseline models
4. Transformer training
5. Local API testing
6. Unit & integration tests
7. Docker build & container tests
8. Multi-model testing
9. Performance validation
10. Cleanup & verification

Each phase has clear entry/exit criteria and troubleshooting guidance.

### 10.2 Test Coverage

* 326+ tests (unit, integration, API, Docker)
* All passing in the final run
* Includes:

  * Model loading & inference
  * API response formats and error handling
  * Multi-model switching
  * Docker containers (startup, health, shutdown)
  * Performance scripts

### 10.3 Performance (Inside Docker)

Final latency and stability results in the container:

| Model               | Avg Lat (ms) | p95 (ms) | p99 (ms) | Notes                   |
| ------------------- | -----------: | -------: | -------: | ----------------------- |
| DistilBERT          |         ~8.1 |     ~9.4 |    ~12.5 | 5–7× better than target |
| Logistic Regression |        ~0.66 |    ~0.85 |    ~1.54 | Sub-millisecond         |
| Linear SVM          |        ~0.60 |    ~0.74 |    ~1.22 | Fastest                 |

* Memory: ~505–508 MiB with all three core models loaded
* 300/300 requests succeeded, no crashes, no leaks

The system over-delivers on performance targets for all model types.

---

## 11. Quick Start Cheat-Sheet

### 11.1 Local Dev (Minimal Path)

```bash
# 1) Create & activate venv, install deps
python -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2) Preprocess data
bash scripts/run_preprocess_local.sh

# 3) Train baselines
bash scripts/run_baselines_local.sh

# 4) Train DistilBERT (quick config)
bash scripts/run_transformer_local.sh

# 5) Run API locally
bash scripts/run_api_local.sh
# -> http://localhost:8000/docs

# 6) Optional: Run Streamlit UI
bash scripts/run_streamlit_local.sh
# -> http://localhost:8501
```

### 11.2 Full Stack via Docker Compose

```bash
# Build & start API + UI
docker-compose up -d --build

# Stop everything
docker-compose down
```

### 11.3 One-Shot Cloud Deployment (VM + Docker)

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

---

## 12. Documentation Map

For deeper dives, see:

* `PROJECT_FLOW.md` – canonical architectural story (this README syncs with its latest consolidated version)
* `docs/training/` – detailed training modes (fast vs full-scale), cloud training, hyperparameter notes
* `docs/docker/` – Docker & Docker Compose guides, test results, troubleshooting
* `docs/deployment/` – GCP VM deployment plan, Cloud Run guides, model transfer analysis, script docs
* `docs/testing/` – end-to-end test plan, intermediate progress reports, final test report 
* `docs/ui/` – Streamlit UI design, bugfix logs and visual summaries for the front-end 

---

## 13. Roadmap & Extensions

The current system is **complete and deployed**, but it is designed to be extensible:

* Plug in new transformer architectures (e.g., RoBERTa, DeBERTa) into the same API
* Extend toxicity model with more labels or new datasets
* Add explanation surfaces (e.g., SHAP, attention visualizations) in the UI
* Complete the GKE deployment plan (PVCs, Ingress, HPA, CI/CD)
* Integrate authentication / rate-limiting for production APIs

---

**TL;DR:**

You can clone this repo, follow the Quick Start, and in under an hour have:

1. Trained models (or loaded existing artifacts)
2. A local API and UI running via Docker or bare Python
3. A one-command path to deploy the API to GCP and expose it publicly

All with a thoroughly tested, well-documented pipeline behind it.
