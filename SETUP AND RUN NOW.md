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
Use the **single PowerShell script** to deploy the backend to a GCP VM and expose it publicly. This includes:
- Creating GCS bucket for model storage
- Uploading models with versioning
- Creating/configuring VM
- Building Docker image on VM
- Deploying API container

**Requirements before proceeding:**

- GCP project (e.g., `mnist-k8s-pipeline`) exists
- Billing enabled, Compute Engine API on
- `gcloud` authenticated: `gcloud auth login`, `gcloud config set project <PROJECT_ID>`
- You are on **Windows with PowerShell** (script is `.ps1`) or using PowerShell Core on another OS
- Models trained and present in `models/` directory

---

### STEP 5.a: Verify GCP configuration

**STEP [5.a]: Confirm active project & authentication**

**Run Command:**

```powershell
gcloud config get-value project
gcloud auth list
gcloud services enable compute.googleapis.com storage.googleapis.com
```

**Expected Result:**

- `gcloud config get-value project` prints your target project ID (e.g., `mnist-k8s-pipeline`)
- `gcloud auth list` shows your authenticated account with `*` (ACTIVE)
- Compute Engine and Cloud Storage APIs are enabled

---

### STEP 5.a.1: (Optional) Create VM if it doesn't exist

**STEP [5.a.1]: Create GCP VM for deployment**

**Run Command:**

```bash
gcloud compute instances create nlp-classifier-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --boot-disk-size=50GB \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server

# Create firewall rules for ports 8000 (API) and 8501 (UI)
gcloud compute firewall-rules create allow-nlp-api \
  --allow=tcp:8000,tcp:8501 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server
```

**Expected Result:**

- VM `nlp-classifier-vm` created with 2 vCPU, 8GB RAM, 50GB disk
- Firewall rules allow access to ports 8000 and 8501
- `gcloud compute instances list` shows the VM in RUNNING state

**Note:** If VM already exists, skip this step. The deployment script will use the existing VM.

---

### STEP 5.b: Run complete deployment (optimized, no checkpoints)

**STEP [5.b]: Deploy API to GCP VM with one command**

**Run Command (from repo root, PowerShell):**

```powershell
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

**Expected Result:**

- Script logs show sequential phases:

  1. **GCS Bucket Setup:**
     - Creates `gs://nlp-classifier-models/` bucket (if not exists)
     - Reads model prefix from `MODEL_VERSION.json` (e.g., `DPM-MODELS`)
     - Checks if models already uploaded (version comparison)

  2. **Model Upload:**
     - Uploads models to `gs://nlp-classifier-models/DPM-MODELS/models/`
     - Size: ~770 MB (with `-NoCheckpoints` flag)
     - Time: 2-3 minutes
     - Uploads: DistilBERT, baselines (LogReg, SVM), toxicity model

  3. **VM Setup:**
     - Verifies VM exists and is running
     - Installs Docker if needed
     - Creates project directories

  4. **Code Deployment:**
     - Clones/updates Git repository on VM
     - Downloads models from GCS to VM

  5. **Docker Build:**
     - Builds image on VM: `sudo docker build -t cloud-nlp-classifier:latest .`
     - Time: 15-20 minutes (includes PyTorch, transformers)
     - Image size: ~2.5 GB

  6. **Container Start:**
     - Runs container: `sudo docker run -d -p 8000:8000 --name nlp-api --restart unless-stopped cloud-nlp-classifier:latest`
     - Auto-restart enabled

  7. **Health Validation:**
     - Tests from inside VM (localhost)
     - Tests from external IP
     - Verifies all endpoints working

- Final summary similar to:

  ```text
  ============================================
    DEPLOYMENT COMPLETE!
  ============================================
  API Endpoints:
    Health:  http://35.232.76.140:8000/health
    Predict: http://35.232.76.140:8000/predict
    Docs:    http://35.232.76.140:8000/docs
    Models:  http://35.232.76.140:8000/models

  Available Models:
    - distilbert (96.57% acc, ~8-20ms)
    - logistic_regression (85-88% acc, ~0.66ms)
    - linear_svm (85-88% acc, ~0.60ms)
    - toxicity (multi-label, 6 categories)

  [OK] Your NLP API is now live!
  ```

**What the script does automatically:**
- ✅ Creates GCS bucket for model storage
- ✅ Uploads models with version tracking
- ✅ Clones code to VM via Git
- ✅ Downloads models from GCS to VM
- ✅ Builds Docker image on VM (includes all dependencies)
- ✅ Starts container with auto-restart policy
- ✅ Validates health from inside and outside VM

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

### STEP 5.d: Test multi-model switching

**STEP [5.d]: Switch between models dynamically (zero downtime)**

**Run Command:**

```bash
# List available models
curl http://<VM_IP>:8000/models

# Switch to fast model (Logistic Regression)
curl -X POST http://<VM_IP>:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'

# Test prediction with new model
curl -X POST http://<VM_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'

# Switch to ultra-fast model (Linear SVM)
curl -X POST http://<VM_IP>:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "linear_svm"}'

# Switch back to high-accuracy model (DistilBERT)
curl -X POST http://<VM_IP>:8000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "distilbert"}'
```

**Expected Result:**

- `/models` returns list of all 4 available models
- `/models/switch` successfully switches models without restarting container
- Predictions use the newly selected model
- Response includes `"model": "logistic_regression"` (or whichever is active)

**Model Selection Guide:**
- **distilbert**: Best accuracy (96.57%), slower (~8-20ms)
- **logistic_regression**: Balanced (85-88% acc, ~0.66ms) - 12x faster
- **linear_svm**: Ultra-fast (85-88% acc, ~0.60ms) - 13x faster
- **toxicity**: Multi-label classification (6 toxicity categories)

---

### STEP 5.e: Manage VM lifecycle (cost control)

**STEP [5.e]: Stop and start the VM as needed**

- **Stop VM – Run Command:**

  ```bash
  gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a
  ```

- **Start VM – Run Command:**

  ```bash
  gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
  ```

- **Check VM status – Run Command:**

  ```bash
  gcloud compute instances describe nlp-classifier-vm --zone=us-central1-a --format="get(status)"
  ```

**Expected Result:**

- When stopped, API is unreachable (no billing for compute, only storage)
- When started again, the `nlp-api` container automatically restarts (due to `--restart unless-stopped` policy)
- API becomes reachable within 30-60 seconds after VM starts

**Cost Savings:**
- Running: ~$0.07/hour (~$50/month)
- Stopped: ~$0.01/day (disk storage only)
- **Tip:** Stop VM when not in use to save costs!

---

## STAGE 5.5 – Deploy Streamlit UI to GCP (Optional)

**Summary:**
Deploy the interactive Streamlit UI alongside the API on the same GCP VM. This provides a user-friendly chat interface for testing the models.

**Requirements before proceeding:**

- Stage 5 completed (API deployed and running)
- VM accessible via SSH
- Port 8501 open in firewall (should be configured in Step 5.a.1)

---

### STEP 5.5.a: SSH into VM and build UI image

**STEP [5.5.a]: Connect to VM and build Streamlit Docker image**

**Run Command:**

```bash
# SSH into the VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Navigate to project directory
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Build Streamlit UI Docker image
sudo docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:latest .
```

**Expected Result:**

- Successfully connected to VM via SSH
- Docker build completes (takes 5-10 minutes)
- `sudo docker images` shows `cloud-nlp-classifier-ui:latest`

---

### STEP 5.5.b: Run UI container

**STEP [5.5.b]: Start Streamlit UI container**

**Run Command (on VM):**

```bash
sudo docker run -d -p 8501:8501 \
  --name nlp-ui \
  --restart unless-stopped \
  cloud-nlp-classifier-ui:latest
```

**Expected Result:**

- Container starts successfully
- `sudo docker ps` shows both `nlp-api` and `nlp-ui` running
- UI accessible at `http://<VM_IP>:8501`

---

### STEP 5.5.c: (Alternative) Use Docker Compose for full stack

**STEP [5.5.c]: Deploy both API and UI with Docker Compose**

**Run Command (on VM):**

```bash
# Stop individual containers if running
sudo docker stop nlp-api nlp-ui
sudo docker rm nlp-api nlp-ui

# Start full stack with Docker Compose
cd ~/CLOUD-NLP-CLASSIFIER-GCP
sudo docker-compose up -d --build
```

**Expected Result:**

- Both API and UI containers start together
- `sudo docker-compose ps` shows both services running
- API: `http://<VM_IP>:8000`
- UI: `http://<VM_IP>:8501`

---

### STEP 5.5.d: Test Streamlit UI

**STEP [5.5.d]: Access and test the UI**

**Run Command (from your local browser):**

```
Navigate to: http://<VM_IP>:8501
```

**Expected Result:**

- Streamlit UI loads with chat interface
- Can select different models from sidebar
- Can type messages and get predictions
- Results show:
  - Predicted label (Hate Speech / Regular Speech)
  - Confidence score
  - Probability distribution chart
  - Model used for prediction
  - Inference time

**UI Features:**
- 🎯 Model selection (DistilBERT, LogReg, SVM, Toxicity)
- 💬 Chat-style interface
- 📊 Visual probability charts
- ⚡ Real-time inference time display
- 🎨 Color-coded results (red=hate, green=safe)

---

## STAGE 6 – (Optional) Cloud Run Deployment

**Summary:**
Deploy to **Google Cloud Run** for serverless, auto-scaling infrastructure. Cloud Run automatically scales from 0 to N instances based on traffic.

**Requirements before proceeding:**

- Docker image built locally (from Stage 4)
- GCP project with billing enabled
- Cloud Run API enabled
- Artifact Registry or Container Registry configured

---

### STEP 6.a: Enable Cloud Run API

**STEP [6.a]: Enable required GCP services**

**Run Command:**

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

**Expected Result:**

- Cloud Run API enabled
- Artifact Registry API enabled

---

### STEP 6.b: Build and push Docker image to Artifact Registry

**STEP [6.b]: Push image to GCP container registry**

**Run Command:**

```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Build and push using Cloud Build (recommended)
gcloud builds submit --tag gcr.io/$PROJECT_ID/cloud-nlp-classifier

# Alternative: Build locally and push
# docker tag cloud-nlp-classifier:latest gcr.io/$PROJECT_ID/cloud-nlp-classifier
# docker push gcr.io/$PROJECT_ID/cloud-nlp-classifier
```

**Expected Result:**

- Image builds successfully (or uses local build)
- Image pushed to `gcr.io/<PROJECT_ID>/cloud-nlp-classifier`
- Build time: 10-15 minutes (if using Cloud Build)

---

### STEP 6.c: Deploy to Cloud Run

**STEP [6.c]: Deploy container to Cloud Run**

**Run Command:**

```bash
gcloud run deploy cloud-nlp-classifier \
  --image gcr.io/$PROJECT_ID/cloud-nlp-classifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 3Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --port 8000
```

**Expected Result:**

- Cloud Run service deployed
- Service URL provided (e.g., `https://cloud-nlp-classifier-xxxxx-uc.a.run.app`)
- Auto-scaling configured (0 to 10 instances)
- Memory: 3 GB per instance
- CPU: 2 vCPU per instance

---

### STEP 6.d: Test Cloud Run deployment

**STEP [6.d]: Verify Cloud Run service**

**Run Command:**

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe cloud-nlp-classifier \
  --region us-central1 \
  --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test prediction
curl -X POST $SERVICE_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Open API docs in browser
echo "API Docs: $SERVICE_URL/docs"
```

**Expected Result:**

- Service responds to health checks
- Predictions work correctly
- Interactive docs accessible
- Cold start: ~5-10 seconds (first request)
- Warm requests: <1 second

**Cloud Run Benefits:**
- ✅ Auto-scaling (0 to N instances)
- ✅ Pay only for requests (no idle costs)
- ✅ HTTPS by default
- ✅ No server management
- ✅ Global CDN

**Cloud Run Pricing:**
- First 2 million requests/month: FREE
- After: ~$0.40 per million requests
- Memory: ~$0.0000025 per GB-second
- CPU: ~$0.00001 per vCPU-second

---

### STEP 6.e: (Optional) Deploy Streamlit UI to Cloud Run

**STEP [6.e]: Deploy UI as separate Cloud Run service**

**Run Command:**

```bash
# Build and push UI image
gcloud builds submit --tag gcr.io/$PROJECT_ID/cloud-nlp-classifier-ui \
  -f Dockerfile.streamlit

# Deploy UI to Cloud Run
gcloud run deploy cloud-nlp-classifier-ui \
  --image gcr.io/$PROJECT_ID/cloud-nlp-classifier-ui \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --port 8501 \
  --set-env-vars API_URL=$SERVICE_URL
```

**Expected Result:**

- UI deployed as separate service
- UI URL provided (e.g., `https://cloud-nlp-classifier-ui-xxxxx-uc.a.run.app`)
- UI communicates with API service
- Both services auto-scale independently

---

## STAGE 7 – Advanced: Model Versioning & Updates

**Summary:**
Update models in production without downtime using the model versioning system.

---

### STEP 7.a: Update MODEL_VERSION.json

**STEP [7.a]: Increment version and update models**

**Edit `MODEL_VERSION.json`:**

```json
{
  "version": "1.1.0",
  "model_prefix": "DPM-MODELS",
  "models": {
    "distilbert": {
      "version": "1.1.0",
      "accuracy": 0.9657,
      "path": "models/transformer/distilbert"
    },
    "logistic_regression": {
      "version": "1.0.0",
      "accuracy": 0.88,
      "path": "models/baselines/logistic_regression_tfidf.joblib"
    }
  }
}
```

**Expected Result:**

- Version incremented (1.0.0 → 1.1.0)
- Model metadata updated

---

### STEP 7.b: Deploy updated models

**STEP [7.b]: Re-run deployment with new version**

**Run Command:**

```powershell
# Upload new models to GCS
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints

# Script detects version change and uploads new models
```

**Expected Result:**

- Script compares versions (1.0.0 vs 1.1.0)
- Detects change and uploads new models
- VM downloads updated models
- Rebuilds Docker image with new models
- Restarts container with updated models
- Zero downtime if using Cloud Run (gradual rollout)

---

## STAGE 8 – Monitoring & Maintenance

**Summary:**
Monitor your deployed API and perform routine maintenance.

---

### STEP 8.a: View container logs

**STEP [8.a]: Check API logs for errors**

**Run Command (VM deployment):**

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# View logs
sudo docker logs -f nlp-api

# View last 100 lines
sudo docker logs --tail 100 nlp-api
```

**Run Command (Cloud Run deployment):**

```bash
gcloud run logs read cloud-nlp-classifier \
  --region us-central1 \
  --limit 50
```

**Expected Result:**

- View API request logs
- See model loading messages
- Identify any errors or warnings

---

### STEP 8.b: Monitor performance

**STEP [8.b]: Check API performance metrics**

**Run Command:**

```bash
# Test latency for each model
for model in distilbert logistic_regression linear_svm; do
  echo "Testing $model..."
  time curl -X POST http://<VM_IP>:8000/models/switch \
    -H "Content-Type: application/json" \
    -d "{\"model_name\": \"$model\"}"
  
  time curl -X POST http://<VM_IP>:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "test message"}'
done
```

**Expected Result:**

- DistilBERT: ~8-20ms
- Logistic Regression: ~0.66ms
- Linear SVM: ~0.60ms

---

### STEP 8.c: Update deployment

**STEP [8.c]: Update code without retraining models**

**Run Command:**

```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Pull latest code
cd ~/CLOUD-NLP-CLASSIFIER-GCP
git pull origin main

# Rebuild and restart container
sudo docker build -t cloud-nlp-classifier:latest .
sudo docker stop nlp-api
sudo docker rm nlp-api
sudo docker run -d -p 8000:8000 \
  --name nlp-api \
  --restart unless-stopped \
  cloud-nlp-classifier:latest
```

**Expected Result:**

- Code updated from Git
- Container rebuilt with new code
- API restarts with updated logic
- Models remain unchanged (no retraining needed)

---

## 🎉 DEPLOYMENT COMPLETE!

You now have a **complete, production-ready ML system** with:

### ✅ **What You've Built:**

1. **Data Pipeline**: Automated preprocessing and splitting
2. **Multiple Models**: 4 models with different trade-offs
   - DistilBERT: 96.57% accuracy, ~8-20ms
   - Logistic Regression: 85-88% accuracy, ~0.66ms
   - Linear SVM: 85-88% accuracy, ~0.60ms
   - Toxicity: Multi-label, 6 categories
3. **REST API**: FastAPI with dynamic model switching
4. **Interactive UI**: Streamlit chat interface
5. **Docker Containers**: Portable, reproducible deployment
6. **Cloud Deployment**: GCP VM or Cloud Run
7. **Model Versioning**: Automated version tracking
8. **Monitoring**: Logs and performance metrics

### 🚀 **Deployment Options:**

| Option | Best For | Cost | Scaling |
|--------|----------|------|---------|
| **Local** | Development, testing | Free | Manual |
| **GCP VM** | Stable traffic, control | ~$50/month | Manual |
| **Cloud Run** | Variable traffic | Pay-per-use | Auto |

### 📊 **Performance Summary:**

- **Accuracy**: 96.57% (DistilBERT)
- **Latency**: 0.60ms - 20ms (depending on model)
- **Throughput**: 120-1600 req/s (depending on model)
- **Memory**: 508 MiB - 3 GB
- **Uptime**: 99.9%+ (with auto-restart)

### 🔧 **Next Steps:**

1. **Fine-tune models** with more data or different hyperparameters
2. **Add monitoring** with Prometheus + Grafana
3. **Set up CI/CD** for automated deployments
4. **Add authentication** for production use
5. **Scale horizontally** with load balancer + multiple VMs
6. **Implement caching** for frequently requested predictions
7. **Add rate limiting** to prevent abuse

### 📚 **Additional Resources:**

- **API Documentation**: `http://<VM_IP>:8000/docs`
- **Project README**: `README.md`
- **Docker Guide**: `docs/DOCKER_GUIDE.md`
- **Multi-Model Guide**: `docs/MULTI_MODEL_DOCKER_GUIDE.md`
- **Deployment Options**: `DEPLOYMENT_OPTIONS.md`

---

**Congratulations! Your NLP classifier is now live and ready for production use!** 🎊
