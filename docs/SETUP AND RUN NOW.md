````markdown
# CLOUD-NLP-CLASSIFIER-GCP – END-TO-END EXECUTION GUIDE

**Initialize → Train → Test → Deploy** :contentReference[oaicite:0]{index=0}

This document gives a **straight-line recipe** to get from a fresh machine to a **running cloud API**.

- Steps are grouped into **stages**.
- Each step has:
  - `STEP [x]:` – what you’re doing
  - `Run Command:` – the exact command
  - `Expected Result:` – what you should see

> **Note:** Commands assume you are in the project root: `CLOUD-NLP-CLASSIFIER-GCP/`.

---

## STAGE 0 – Prerequisites & Environment

**Summary:**  
Prepare your local machine with the right tools and create an isolated Python environment.

**Requirements before proceeding:**

- Python **3.10+** installed
- Git installed
- (For Docker steps) Docker installed and running
- (For cloud deploy) `gcloud` CLI installed and authenticated

---

### STEP 0.a: Clone the repository

**STEP [0.a]: Clone the repo to your local machine**  
**Run Command:**

```bash
git clone https://github.com/<YOUR_USERNAME>/CLOUD-NLP-CLASSIFIER-GCP.git
cd CLOUD-NLP-CLASSIFIER-GCP
```
````

**Expected Result:**
A new folder `CLOUD-NLP-CLASSIFIER-GCP/` exists, and you are inside it.

---

### STEP 0.b: Create and activate a virtual environment

**STEP [0.b]: Create & activate Python virtualenv**

- **Linux / Mac – Run Command:**

  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

- **Windows (PowerShell) – Run Command:**

  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

**Expected Result:**
Your shell prompt shows `(venv)` prefix, meaning the venv is active.

---

### STEP 0.c: Install Python dependencies

**STEP [0.c]: Install project dependencies**
**Run Command:**

```bash
pip install -r requirements.txt
```

**Expected Result:**
All required packages (FastAPI, Transformers, scikit-learn, Streamlit, etc.) are installed without errors.

---

## STAGE 1 – Data Initialization & Preprocessing

**Summary:**
Download and preprocess the hate/offensive speech dataset into train/val/test CSVs under `data/processed/`.

**Requirements before proceeding:**

- Stage 0 completed
- Network access to download dataset (if the scripts do so)

---

### STEP 1.a: Ensure raw data folder exists

**STEP [1.a]: Create data directories (if needed)**
**Run Command:**

```bash
mkdir -p data/raw data/processed
```

**Expected Result:**
`data/raw/` and `data/processed/` folders exist. If they already existed, nothing breaks.

---

### STEP 1.b: Run preprocessing pipeline

**STEP [1.b]: Preprocess dataset into train/val/test splits**

- **Linux / Mac – Run Command:**

  ```bash
  bash scripts/run_preprocess_local.sh
  ```

- **Windows (PowerShell) – Run Command:**

  ```powershell
  .\scripts\run_preprocess_local.ps1
  ```

**Expected Result:**

- Script finishes without errors.
- New CSV files appear:

  - `data/processed/train.csv`
  - `data/processed/val.csv`
  - `data/processed/test.csv`

- Logs mention:

  - Rows loaded
  - Rows after cleaning
  - Split sizes (train/val/test)

---

## STAGE 2 – Model Training (Baselines + DistilBERT)

**Summary:**
Train the **baseline models** (LogReg & Linear SVM) and the **DistilBERT hate classifier**.

**Requirements before proceeding:**

- Stage 1 completed – processed CSVs exist
- Enough disk space for models (~1 GB total if you skip checkpoints)

---

### STEP 2.a: Train baseline models

**STEP [2.a]: Train TF-IDF + Logistic Regression / Linear SVM**

- **Linux / Mac – Run Command:**

  ```bash
  bash scripts/run_baselines_local.sh
  ```

- **Windows (PowerShell) – Run Command:**

  ```powershell
  .\scripts\run_baselines_local.ps1
  ```

**Expected Result:**

- Training finishes with printed accuracy / F1 metrics.
- New files in `models/baselines/`:

  - `logistic_regression_tfidf.joblib`
  - `linear_svm_tfidf.joblib`

- Logs mention performance like:

  - Accuracy ≈ 0.93–0.95
  - Latency tests (sub-millisecond) when run in Docker later.

---

### STEP 2.b: Train DistilBERT hate classifier (dev mode)

**STEP [2.b]: Run quick DistilBERT training (dev config)**

- **Linux / Mac – Run Command:**

  ```bash
  bash scripts/run_transformer_local.sh
  ```

- **Windows (PowerShell) – Run Command:**

  ```powershell
  .\scripts\run_transformer_local.ps1
  ```

**Expected Result:**

- Script tokenizes data, then shows epoch-by-epoch training logs.
- On completion, it saves a model under e.g.:

  - `models/transformer/distilbert/`

- Files include:

  - `model.safetensors`
  - `config.json`
  - tokenizer files
  - `labels.json`
  - `training_info.json`

- Metrics show ≈96% accuracy (or better for full training runs).

---

### STEP 2.c: (Optional) Train full-scale DistilBERT / toxicity model

**STEP [2.c]: Run full-scale or toxicity training (optional)**

**Run Command (example full-scale DistilBERT):**

```bash
python -m src.models.transformer_training \
  --config config/config_transformer_cloud.yaml \
  --mode cloud \
  --epochs 10
```

**Run Command (toxicity multi-head, example):**

```bash
python -m src.models.train_toxicity \
  --config config/config_toxicity.yaml
```

**Expected Result:**

- Longer training (especially on CPU); on GPU with FP16 it completes faster.
- Models saved under:

  - `models/transformer/distilbert_fullscale/` (if configured)
  - `models/toxicity_multi_head/`

- Logs show per-label metrics for toxicity (toxic, severe_toxic, obscene, threat, insult, identity_hate).

---

## STAGE 3 – Testing & Validation

**Summary:**
Run unit, integration, and API tests to confirm models and pipelines are stable.

**Requirements before proceeding:**

- Stage 2 completed – models exist under `models/`
- Virtual environment still active

---

### STEP 3.a: Run Python tests with pytest

**STEP [3.a]: Execute the full test suite**

**Run Command:**

```bash
pytest -q
```

**Expected Result:**

- All tests run and finish with:

  - `N passed, 0 failed` (where N ≈ 326+ tests)

- No unhandled exceptions.
- Optional coverage report (if configured).

---

### STEP 3.b: Run API smoke test (local, non-Docker)

**STEP [3.b]: Start FastAPI server locally and test `/health`**

1. **Run Command – start API (one terminal):**

   ```bash
   bash scripts/run_api_local.sh
   ```

   _(Windows: `.\scripts\run_api_local.ps1`)_

2. **Run Command – test health (another terminal):**

   ```bash
   curl http://localhost:8000/health
   ```

**Expected Result:**

- Uvicorn logs show the server running on `http://127.0.0.1:8000`.
- `/health` returns JSON like:

  ```json
  {
    "status": "healthy",
    "model_loaded": true,
    "available_models": [...]
  }
  ```

- `/docs` is available in the browser at `http://localhost:8000/docs`.

---

## STAGE 4 – Local Serving (Docker + Optional UI)

**Summary:**
Package everything into Docker images and run the API (and optional Streamlit UI) locally.

**Requirements before proceeding:**

- Docker is installed and running
- Baseline + DistilBERT models present in `models/`
- Tests passing from Stage 3

---

### STEP 4.a: Build backend Docker image

**STEP [4.a]: Build Docker image for FastAPI backend**

**Run Command:**

```bash
docker build -t cloud-nlp-classifier:latest .
```

**Expected Result:**

- Docker build completes successfully, with no errors at the end.
- `docker images` shows `cloud-nlp-classifier:latest` present.

---

### STEP 4.b: Run backend container

**STEP [4.b]: Run the FastAPI container locally**

**Run Command:**

```bash
docker run -d -p 8000:8000 --name nlp-api cloud-nlp-classifier:latest
```

**Expected Result:**

- `docker ps` shows a running container `nlp-api` bound to port `8000->8000`.
- `curl http://localhost:8000/health` returns a healthy JSON response.
- `http://localhost:8000/docs` accessible in the browser.

---

### STEP 4.c: (Optional) Build and run Streamlit UI image

**STEP [4.c]: Run the Streamlit UI via Docker**

1. **Run Command – build UI image:**

   ```bash
   docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .
   ```

2. **Run Command – start UI container:**

   ```bash
   docker run -d -p 8501:8501 --name nlp-ui cloud-nlp-classifier-ui:latest
   ```

**Expected Result:**

- `docker ps` shows `nlp-ui` running on port `8501`.
- Browser at `http://localhost:8501` shows the chat-style UI.
- Sending a message triggers a prediction using the selected model.

---

### STEP 4.d: (Optional) Use Docker Compose for full stack

**STEP [4.d]: Start API + UI via docker-compose**

**Run Command:**

```bash
docker-compose up -d --build
```

**Expected Result:**

- Both API and UI containers start.
- `docker-compose ps` shows services up.
- `http://localhost:8000/docs` and `http://localhost:8501` are accessible.

---

## STAGE 5 – Cloud Deployment (GCP VM + Docker Script)

**Summary:**
Use the **single PowerShell script** to deploy the backend to a GCP VM and expose it publicly.

**Requirements before proceeding:**

- GCP project (e.g., `mnist-k8s-pipeline`) exists
- Billing enabled, Compute Engine API on
- `gcloud` authenticated: `gcloud auth login`, `gcloud config set project <PROJECT_ID>`
- A VM like `nlp-classifier-vm` created (or let the script handle it if configured)
- You are on **Windows with PowerShell** (script is `.ps1`) or using PowerShell Core on another OS

---

### STEP 5.a: Verify GCP configuration

**STEP [5.a]: Confirm active project & VM status**

**Run Command (examples):**

```powershell
gcloud config get-value project
gcloud compute instances list
```

**Expected Result:**

- `gcloud config get-value project` prints your target project ID.
- `gcloud compute instances list` shows `nlp-classifier-vm` (or you know you’ll let the script create one, depending on config).

---

### STEP 5.b: Run complete deployment (optimized, no checkpoints)

**STEP [5.b]: Deploy API to GCP VM with one command**

**Run Command (from repo root, PowerShell):**

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Expected Result:**

- Script logs show sequential phases:

  - Bucket creation / verification
  - Model upload (small, inference-only subset)
  - VM verification / creation
  - Repo clone/update on VM
  - Model download on VM
  - Docker build on VM
  - Container start
  - Health checks (internal + external)

- Final summary similar to:

  ```text
  ============================================
    DEPLOYMENT COMPLETE!
  ============================================
  API Endpoints:
    Health:  http://<VM_IP>:8000/health
    Predict: http://<VM_IP>:8000/predict
    Docs:    http://<VM_IP>:8000/docs
    Models:  http://<VM_IP>:8000/models

  [OK] Your NLP API is now live!
  ```

---

### STEP 5.c: Verify external API endpoints

**STEP [5.c]: Test production API from your local machine**

**Run Command:**

```bash
curl http://<VM_IP>:8000/health
curl -X POST http://<VM_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I hate you"}'
```

**Expected Result:**

- `/health` returns `"status": "healthy"` with models listed.
- `/predict` returns JSON with:

  - predicted label (e.g., "Hate")
  - confidence
  - model name (e.g., "distilbert")

- `/docs` is reachable at `http://<VM_IP>:8000/docs` in your browser.

---

### STEP 5.d: Manage VM lifecycle (cost control)

**STEP [5.d]: Stop and start the VM as needed**

- **Stop VM – Run Command:**

  ```bash
  gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a
  ```

- **Start VM – Run Command:**

  ```bash
  gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
  ```

**Expected Result:**

- When stopped, API is unreachable (no billing for compute).
- When started again, the `nlp-api` container comes back (if `--restart` policy is used), and the API becomes reachable once more.

---

## STAGE 6 – (Optional) Cloud Run / Future GKE

**Summary:**
If you prefer serverless or Kubernetes, use the Docker images built in Stage 4 to deploy to **Cloud Run** or later to **GKE**, following the detailed deployment docs.

**Requirements before proceeding:**

- Docker images pushed to GCR/Artifact Registry
- GCP project configured for Cloud Run or GKE

_(See `docs/deployment/` for full, step-by-step guides.)_

---

You now have a **clear, repeatable path**:

1. Initialize the environment
2. Preprocess data
3. Train baselines + DistilBERT (+ toxicity)
4. Run tests
5. Serve locally (Python or Docker)
6. Deploy to GCP with a **single script**

From here, you can tweak configs, plug in new models, or extend the UI knowing the full pipeline is solid.

```

```
