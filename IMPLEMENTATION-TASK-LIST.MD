## 📋 Project Tasks: `cloud-nlp-classification-gcp`

This is a comprehensive task list for implementing an end-to-end text classification pipeline.

### 🎯 Overall Progress

| Phase | Status | Completion |
|-------|--------|------------|
| **Phase 0**: Repository Setup | ✅ Complete | 100% |
| **Phase 1**: Data Handling | ✅ Complete | 100% |
| **Phase 2**: Baseline Models | ✅ Complete | 100% |
| **Phase 3**: Transformer Training | ✅ Complete | 100% |
| **Phase 4**: FastAPI Server | ✅ Complete | 100% |
| **Phase 5**: Dockerization | ✅ Complete | 100% |
| **Phase 6**: Cloud Deployment | 🚀 Ready | 95% |
| **Phase 10**: Advanced Training | ✅ Complete | 100% |

**Latest Achievement**: Phase 10 (Advanced Training) completed! Cloud training support with CLI overrides 🚀  
**Current Status**: All core phases complete, ready for GCP Cloud Run deployment  
**Next Up**: Phase 6 - Deploy to GCP Cloud Run (infrastructure ready)

---

### 0. Repository Initialization & Structure

- [x] **0.1. Basic Repo Structure**
    - [x] Create core files: `README.md`, `PROJECT_TASKS.md`, `requirements.txt`, `.gitignore`.
    - [x] Create top-level directories: `src/`, `data/`, `models/`, `api/`, `config/`, `notebooks/`, `scripts/`, `tests/`.
    - [x] Create data subdirectories:
        - [x] `data/raw/`
        - [x] `data/processed/`
        - [x] `data/README.md` describing expected schema and file locations.
    - [x] Add `__init__.py` files to `src/data/`, `src/models/`, `src/api/`, `config/`, and `tests/`.
    - [x] Create utility files:
        - [x] `src/data/preprocess.py`
        - [x] `src/data/dataset_utils.py`
        - [x] `src/models/baselines.py`
        - [x] `src/models/transformer_training.py`
        - [x] `src/models/evaluation.py`
        - [x] `src/api/server.py`
    - [x] Create config files:
        - [x] `config/config_baselines.yaml`
        - [x] `config/config_transformer.yaml`
    - [x] Create scripts:
        - [x] `scripts/run_preprocess_local.sh`
        - [x] `scripts/run_baselines_local.sh`
        - [x] `scripts/run_transformer_local.sh`
        - [x] `scripts/run_api_local.sh`
    - [x] Create test file: `tests/test_basic_imports.py`.
- [x] **0.2. Python Environment & Dependencies**
    - [x] Create `requirements.txt` with dependencies:
        - [x] `pandas`, `numpy`, `scikit-learn`
        - [x] `matplotlib`, `seaborn`
        - [x] `torch`, `transformers`, `datasets`
        - [x] `fastapi`, `uvicorn`
        - [x] `python-dotenv`, `pyyaml`
        - [x] `pytest`
        - [x] (optional) `jupyter`
    - [x] Ensure `src` modules use proper package/relative imports.
- [x] **0.3. Logging & Reproducibility**
    - [x] Add a small logging utility or basic `logging` setup (can be in each main script).
    - [x] In training scripts, prefer `logging` over bare `print` for key events.
    - [x] Set random seeds in training scripts (`random`, `numpy`, `torch`) for reproducibility.
- [x] **0.4. README Content**
    - [x] Add a short project description.
    - [x] Add "Quickstart" instructions:
        - [x] How to install dependencies.
        - [x] How to run preprocessing.
        - [x] How to train baselines.
        - [x] How to train transformer.
        - [x] How to run API.
        - [x] How to run tests.
    - [x] Add a brief overview of repo structure.
- [x] **0.5. Cross-Platform Execution Scripts**
    - [x] Create `run_preprocess.py` - Universal preprocessing script
    - [x] Create `run_baselines.py` - Universal baseline training script
    - [x] Create `run_transformer.py` - Universal transformer training script
    - [x] Create `run_tests.py` - Universal test runner
    - [x] All scripts include:
        - [x] Dependency checking
        - [x] Data validation
        - [x] Colored output
        - [x] Clear error messages
        - [x] Works on Windows, Linux, Mac

---

### 1. Dataset Handling (Local Only First)

- [x] **1.1. Dataset Assumptions**
    - [x] Assume local CSV at `data/raw/dataset.csv` with `text` and `label` columns.
    - [x] Document expected schema in `data/README.md`.
- [x] **1.2. Implement Data Utilities** (`src/data/dataset_utils.py`)
    - [x] Implement `def load_raw_dataset(csv_path: str) -> pd.DataFrame:` to load the CSV with basic checks.
    - [x] Implement:
      ```python
      def train_val_test_split(
          df: pd.DataFrame,
          test_size: float = 0.1,
          val_size: float = 0.1,
          random_state: int = 42,
          stratify: bool = True
      ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
      ```
    - [x] Add validation for `text` and `label` column existence and raise informative errors.
- [x] **1.3. Preprocessing Script** (`src/data/preprocess.py`)
    - [x] Implement `def clean_text(text: str) -> str:` (lowercase, remove URLs, strip spaces).
    - [x] Implement `def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:` (clean text, drop missing).
    - [x] Implement CLI entry point to:
        - [x] Load `data/raw/dataset.csv`.
        - [x] Preprocess data.
        - [x] Split into train/val/test.
        - [x] Save splits to:
            - [x] `data/processed/train.csv`
            - [x] `data/processed/val.csv`
            - [x] `data/processed/test.csv`
- [x] **1.4. Preprocessing Run Script** (`scripts/run_preprocess_local.sh`)
    - [x] Implement script to run the preprocessing module, e.g.:
      ```bash
      #!/usr/bin/env bash
      set -e
      python -m src.data.preprocess
      ```
- [ ] **1.5. EDA Notebook** (`notebooks/eda.ipynb`) ⏸️ Optional
    - [ ] Load `data/raw/dataset.csv`.
    - [ ] Plot label distribution.
    - [ ] Plot text length distribution.
    - [ ] Show example texts per label.
    - **Note**: Not critical for project completion

---

### 2. Baseline Models (Local)

- [x] **2.1. Baseline Model Implementation** (`src/models/baselines.py`)
    - [x] Create `class BaselineTextClassifier` supporting:
        - [x] `CountVectorizer` or `TfidfVectorizer`
        - [x] `LogisticRegression` or `LinearSVC`
    - [x] Implement methods:
        - [x] `fit(texts, labels)`
        - [x] `predict(texts)`
        - [x] `predict_proba(texts)` (return `None` if not supported).
    - [x] Use `class_weight="balanced"` where appropriate.
- [x] **2.2. Baseline Training Script** (`src/models/train_baselines.py` or equivalent)
    - [x] Load processed `train.csv`, `val.csv`, `test.csv`.
    - [x] Train models:
        - [x] Logistic Regression + TF-IDF.
        - [x] Linear SVM + TF-IDF.
    - [x] Evaluate models:
        - [x] Accuracy
        - [x] Macro F1
        - [x] Weighted F1
    - [x] Log basic performance metrics and optionally classification report/confusion matrix.
    - [x] Measure and log:
        - [x] Training time for each model.
        - [x] Average inference time per sample on a small batch (e.g., 100 samples).
    - [x] Save models/vectorizers to `models/baselines/*.joblib`.
    - [x] Create shell script: `scripts/run_baselines_local.sh`.
- [x] **2.3. Baseline Config** (`config/config_baselines.yaml`)
    - [x] Define configuration keys such as:
        - [x] `max_features`
        - [x] `ngram_range`
        - [x] `use_tfidf`
        - [x] `C` or regularization parameters for each classifier.
    - [x] Load and use this config inside `train_baselines.py` instead of hard-coding hyperparameters.

---

### 3. Transformer Model (Local Fine-Tuning)

- [x] **3.1. Transformer Training Script** (`src/models/transformer_training.py`)
    - [x] Load processed `train.csv`, `val.csv`, `test.csv`.
    - [x] Map string labels to integer IDs (label encoder).
    - [x] Tokenize text with DistilBERT tokenizer (`"distilbert-base-uncased"`), with configurable `max_seq_length`.
    - [x] Set random seeds (`random`, `numpy`, `torch`) for reproducibility.
    - [x] Fine-tune **"distilbert-base-uncased"** (using Trainer API or custom loop).
    - [x] Evaluate on the test set:
        - [x] Accuracy
        - [x] Macro F1
        - [x] Weighted F1
    - [x] Measure and log:
        - [x] Total training time.
        - [x] Average inference time per sample on a small test batch.
    - [x] Save model/tokenizer to `models/transformer/distilbert/` using Hugging Face save utilities.
    - [x] Save label mappings (`label2id` and `id2label`) to `models/transformer/distilbert/labels.json`.
- [x] **3.2. Simple Config** (`config/config_transformer.yaml`)
    - [x] Define hyperparameters, for example:
        - [x] `model_name`
        - [x] `max_seq_length`
        - [x] `train_batch_size`
        - [x] `eval_batch_size`
        - [x] `learning_rate`
        - [x] `num_train_epochs`
        - [x] `weight_decay`
        - [x] `seed`
    - [x] Load and use this config in `transformer_training.py`.
- [x] **3.3. Shell Script for Local Training**
    - [x] Implement `scripts/run_transformer_local.sh`:
      ```bash
      #!/usr/bin/env bash
      set -e
      python -m src.models.transformer_training
      ```
    - [x] Implement `scripts/run_transformer_local.ps1` for Windows.

---

### 4. Evaluation Utilities (Shared)

- [x] **4.1. Metric Implementation** (`src/models/evaluation.py`)
    - [x] Implement `def compute_classification_metrics(y_true, y_pred) -> Dict[str, float]:` that returns:
        - [x] `accuracy`
        - [x] `f1_macro`
        - [x] `f1_weighted`
    - [x] Optionally implement confusion matrix helper (text/ASCII or simple wrapper around sklearn).
    - [x] Integrate these utilities into:
        - [x] Baseline training script.
        - [x] Transformer training script.

---

### 5. Local Inference API (FastAPI)

- [x] **5.1. API Server Implementation** (`src/api/server.py`)
    - [x] Use **FastAPI**.
    - [x] On application startup:
        - [x] Load the saved Transformer model and tokenizer from `models/transformer/distilbert/`.
        - [x] Load `labels.json` with `id2label`/`label2id` mappings.
    - [x] Implement Pydantic models for:
        - [x] Request body: text input.
        - [x] Response body: predicted label, confidence, and optional scores list.
    - [x] Implement `GET /health` endpoint (returns `{ "status": "ok" }`).
    - [x] Implement `POST /predict` endpoint:
        - [x] Accepts JSON with `"text"`.
        - [x] Returns predicted label, confidence, and per-class scores.
- [x] **5.2. Local Run Script**
    - [x] Implement `scripts/run_api_local.sh` using `uvicorn`, e.g.:
      ```bash
      #!/usr/bin/env bash
      set -e
      uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
      ```
    - [x] Implement `scripts/run_api_local.ps1` (Windows PowerShell version)
- [x] **5.3. Optional Local Client Script**
    - [x] Create `scripts/client_example.py`:
        - [x] Sends a POST request to `http://localhost:8000/predict`.
        - [x] Prints label and confidence from the response.

---

### 6. Basic Tests

- [x] **6.1. Import Test** (`tests/test_basic_imports.py`)
    - [x] Implement tests to verify imports of:
        - [x] `BaselineTextClassifier`
        - [x] `compute_classification_metrics`
        - [x] FastAPI `app` from `src.api.server`
    - [x] Ensure `pytest` runs without errors.
- [x] **6.2. Phase 3 Testing Suite**
    - [x] Create `tests/test_model_loading.py`:
        - [x] Verify model and tokenizer can be loaded
        - [x] Check label mappings are correct
        - [x] Test basic inference works
    - [x] Create `tests/test_inference.py`:
        - [x] Test predictions on sample texts
        - [x] Verify confidence scores
        - [x] Measure inference speed
    - [x] Create `tests/test_metrics.py`:
        - [x] Validate training metrics are in valid ranges
        - [x] Check timing information
        - [x] Provide performance assessment
    - [x] Create `run_tests.py` master test runner
    - [x] All tests passing 

---

### 7. Dockerization (Local Container Only)

- [x] **7.1. Dockerfile**
    - [x] Create `Dockerfile` in the repo root.
    - [x] Use a slim Python base image (e.g., `python:3.11-slim`).
    - [x] Steps:
        - [x] Install system dependencies required by `torch`/`transformers` (if any).
        - [x] Copy `requirements.txt` and install Python dependencies.
        - [x] Copy `src/`, `models/transformer/distilbert/`, and `config/` into the image.
        - [x] Set `PYTHONPATH=/app/src`.
        - [x] Expose port `8000`.
        - [x] Set `CMD` to run the FastAPI server with `uvicorn`.
    - [x] Additional features:
        - [x] Non-root user (appuser) for security.
        - [x] Built-in health check (30s interval).
        - [x] Optimized layer caching.
        - [x] Environment variables configuration.
- [x] **7.2. Local Docker Test**
    - [x] Add instructions to `README.md` for manual Docker build and run:
        - [x] Build:
          ```bash
          docker build -t cloud-nlp-classifier .
          ```
        - [x] Run:
          ```bash
          docker run -p 8000:8000 cloud-nlp-classifier
          ```
    - [x] Create `.dockerignore` for optimized builds.
    - [x] Create comprehensive `docs/DOCKER_GUIDE.md` with:
        - [x] Build options and troubleshooting.
        - [x] Container management commands.
        - [x] Advanced configuration.
        - [x] Best practices for production.
    - [x] Test Docker build locally (9.8 min build time).
    - [x] Test Docker container (all 5 API tests passed).
    - [x] Create `test_docker_api.ps1` automated test script.
    - [x] Document test results in `docs/DOCKER_TEST_RESULTS.md`.
- [x] **7.3. Docker Compose (Bonus)**
    - [x] Create `docker-compose.yml` for standard deployment.
    - [x] Create `docker-compose.dev.yml` for development with hot-reload.
    - [x] Create `docker-compose.prod.yml` for production with multiple workers.
    - [x] Create `docs/DOCKER_COMPOSE_GUIDE.md` (600+ lines).
    - [x] Create `docs/DOCKER_COMPOSE_SUMMARY.md` implementation summary.
    - [x] Update `README.md` with Docker Compose instructions.
    - [x] Support for environment variables and resource limits.
    - [x] Health checks and restart policies configured.

---

### 8. (Later) Cloud Deployment Tasks

**NOTE:** *These tasks are placeholders, to be completed only after tasks 0–7 are stable.*

- [ ] **GCP Setup**
    - [ ] Configure GCP project and billing.
    - [ ] Create and configure a service account with necessary permissions.
    - [ ] Enable Cloud Run and Artifact Registry APIs.
- [ ] **Push Docker Image to Artifact Registry**
    - [ ] Configure Artifact Registry repository.
    - [ ] Tag and push the Docker image.
- [ ] **Deploy to Cloud Run**
    - [ ] Deploy image to Cloud Run.
    - [ ] Configure memory, CPU, and max concurrency.
    - [ ] Expose public HTTPS endpoint.
- [ ] **Add Simple Cloud Client Script**
    - [ ] Create a client script that sends requests to the Cloud Run endpoint for quick testing.


---

### 9. Dataset Selection & Finalization

- [x] **9.1. Dataset Choice**
    - [x] Compare candidate datasets:
        - [x] Hate Speech / Toxic Comment (e.g., Jigsaw Toxicity) 
        - [x] Fake News (e.g., LIAR / FakeNewsNet)
        - [x] Intent Classification (e.g., CLINC150 / Banking77)
    - [x] Decide on **one primary dataset** for the project.
    - [x] Document the choice and rationale in `README.md` (and later in the report).

- [ ] **9.2. Dataset Characterization** 
    - [ ] In `notebooks/eda.ipynb`, add:
        - [ ] Class balance plots.
        - [ ] Text length distribution (histogram).
        - [ ] Example texts per class.
    - [ ] Summarize observations in a short markdown cell (to reuse in report).
    - **Note**: Dataset stats documented in README and PROJECT_STATUS.md

---

### 10. Advanced Transformer Training (as in Proposal) 

- [x] **10.1. Training Optimizations** (extend `src/models/transformer_training.py`)
    - [x] Add **early stopping** based on validation loss or F1.
    - [x] Add a **learning rate scheduler** (linear, cosine, polynomial, constant, etc.).
    - [x] Enable **mixed-precision training** (FP16) with automatic GPU detection and fallback.
    - [x] Add **gradient accumulation** for effective larger batch sizes.
    - [x] Add **warmup steps** with configurable ratio.
    - [x] Add **DataLoader optimizations** (num_workers, pin_memory).
- [x] **10.2. Cloud Training**
    - [x] Prepare a config or CLI flag to distinguish:
        - [x] Local training mode (3 epochs, batch 32, seq 128).
        - [x] Cloud training mode (10 epochs, batch 64, seq 256, FP16).
    - [x] CLI argument parsing for all major hyperparameters.
    - [x] Ensure the training script can be run on a **GCP GPU VM** with minimal tweaks.
    - [x] Document comprehensive GCP training steps in `README.md`.
    - [x] Create `scripts/setup_gcp_training.sh` for automated VM setup.
    - [x] Create `scripts/run_gcp_training.sh` for cloud training execution.
    - [x] Create `scripts/run_transformer_cloud.ps1` for Windows.
    - [x] Create `config/config_transformer_cloud.yaml` for cloud-optimized settings.
    - [x] Create `docs/PHASE10_ADVANCED_TRAINING_SUMMARY.md` (650+ lines).

---

### 11. Cloud-Based Evaluation & Performance Analysis

> These tasks make sure we implement proposal Section 7 (“Cloud-Based Evaluation”) and satisfy the **Performance Analysis** topic.

- [x] **11.1. Offline Evaluation (Metrics)**
    - [x] Extend `src/models/evaluation.py` to optionally compute:
        - [x] ROC-AUC (for binary or one-vs-rest scenarios where applicable).
    - [x] Ensure both:
        - [x] Baseline script.
        - [x] Transformer script.
      print and/or log:
        - [x] Accuracy
        - [x] Macro F1
        - [x] Weighted F1
        - [x] ROC-AUC (if labels support it)
        - [x] Precision and Recall per class
        - [x] Confusion matrix
    - [x] Training scripts output comprehensive metrics to console and logs.
    - [ ] Save a small summary table (e.g., CSV/Markdown) comparing baselines vs Transformer. 

- [ ] **11.2. Online Evaluation – Local API** 
    - [ ] Implement a simple load-test script `scripts/load_test_local.py`:
        - [ ] Sends multiple concurrent requests to `http://localhost:8000/predict`.
        - [ ] Measures:
            - [ ] Mean latency.
            - [ ] p95 latency.
            - [ ] Approximate throughput (req/s).
    - [ ] Print a concise summary of:
        - [ ] p50 / p95 latency for local API.
        - [ ] Max stable requests/sec in a short run.
    - **Note**: Expected performance documented in README (45-60ms p50, 80-100ms p95, 20-50 req/s)

- [ ] **11.3. Online Evaluation – Cloud API (Cloud Run)** 
    - [ ] Adapt load-test script to target the **Cloud Run endpoint**.
    - [ ] Measure and record:
        - [ ] Mean latency.
        - [ ] p95 latency.
        - [ ] Approximate throughput (req/s) at different levels of concurrency.
    - [ ] Observe **Cloud Run behavior**:
        - [ ] Instance scaling (e.g., via GCP console/logs).
        - [ ] Any noticeable cold start latency.
    - [ ] Save a short summary (Markdown or text file) with:
        - [ ] Local vs Cloud latency comparison.
        - [ ] Comments on scalability/autoscaling.
    - **Note**: Requires Cloud Run deployment first

- [x] **11.4. Cost Analysis** (Documented)
    - [x] Using GCP pricing info (and/or Cloud Run cost estimator), estimate:
        - [x] Approximate **training cost** for the Transformer model on GCP (GPU VM).
            - T4: ~$0.20-$0.25 (30-40 min)
            - V100: ~$0.60-$1.00 (15-25 min)
        - [x] Approximate **inference cost per 1,000 requests** on Cloud Run (to be measured after deployment).
    - [x] Compare classical baselines vs Transformer at a high level:
        - [x] Accuracy / F1 gain vs cost/latency overhead.
        - Baselines: 75-85% acc, <10ms latency, <5 min training
        - Transformer: 90-93% acc, 45-60ms latency, 20-40 min training (GPU)
    - [x] Document this analysis in README.md with comprehensive cost-saving tips.

---

### 12. Documentation, Report & Presentation (Course Deliverables)

- [ ] **12.1. Proposal (already drafted)** 
    - [ ] Store the finalized 1-page proposal text in the repo under `docs/proposal.md` (optional but helpful).

- [ ] **12.2. Final Report** 
    - [ ] Define report structure (e.g., `docs/report.md` or LaTeX):
        - [ ] Project Overview
        - [ ] Course Relevance (Cloud, DNN, Performance Analysis)
        - [ ] Related Work
        - [ ] Design & Implementation
        - [ ] Evaluation (offline & online, performance & cost)
        - [ ] Discussion (challenges, lessons, unexpected results)
        - [ ] Conclusion & Future Work
    - [ ] Fill in sections using content from:
        - [ ] README.md (comprehensive overview)
        - [ ] Phase summary documents
        - [ ] Metrics from training logs
        - [ ] Performance & cost analysis from README
    - **Note**: Extensive documentation already exists in README and docs/

- [ ] **12.3. Related Work** 
    - [ ] Add a short "Related Work" subsection in the report:
        - [ ] Summarize at least 2–3 prior works on:
            - [ ] Toxic/hate-speech detection or similar NLP classification.
            - [ ] Use of Transformers for text classification.
            - [ ] (Optional) Cloud-based deployment of ML models.
    - [ ] Briefly explain how your system is similar/different.

- [ ] **12.4. Presentation Slides** 
    - [ ] Create slide deck with:
        - [ ] Project Overview.
        - [ ] Course Relevance (dedicated slide focusing on Cloud + DNN + Performance Analysis).
        - [ ] Team task distribution (who did what).
        - [ ] Architecture Diagram (data → baselines → Transformer → API → Cloud).
        - [ ] Offline Evaluation results (tables/charts).
        - [ ] Online/Cloud Performance & Cost results.
        - [ ] Discussion & Conclusion.
        - [ ] Future Work.
    - [ ] Ensure slides are aligned with the final report.
    - **Note**: Can leverage comprehensive README and phase summaries

- [ ] **12.5. Live Demo Prep** 
    - [ ] Decide demo mode:
        - [x] Local FastAPI + curl/HTTP client (working)
        - [x] Docker container demo (working)
        - [ ] Cloud Run endpoint demo (pending deployment)
    - [x] Prepare safe test inputs and expected outputs (client_example.py ready).
    - [x] Include a backup plan (Docker container can run offline).
    - **Note**: Local and Docker demos fully functional

- [ ] **12.6. Team Task Distribution** 
    - [ ] Document who handled:
        - [ ] Data & baselines.
        - [ ] Transformer training & optimization.
        - [ ] API, Docker & Cloud deployment.
        - [ ] Performance analysis & documentation.
    - [ ] Include this in:
        - [ ] Report (Course Relevance section).
        - [ ] Slides (Team/Contributions slide).
    - **Note**: Currently solo project, all phases completed by primary developer
