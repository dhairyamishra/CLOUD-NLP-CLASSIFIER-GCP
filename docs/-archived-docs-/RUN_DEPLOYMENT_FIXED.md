# Run Fixed Deployment Script

## Quick Start

```powershell
# Run the fixed deployment script
.\scripts\gcp-complete-deployment.ps1 -NoCheckpoints
```

---

## ✅ SUCCESSFUL DEPLOYMENT RESULTS (2025-12-10)

**Status**: ✅ **ALL 4 MODELS WORKING PERFECTLY**  
**API URL**: `http://35.232.76.140:8000`  
**Branch**: `dhairya/gcp-public-deployment`  
**Duration**: ~2-3 minutes (optimized)

### **Performance Results:**
- **Logistic Regression**: 1.84ms (~543 req/s)
- **Linear SVM**: 1.86ms (~537 req/s)  
- **DistilBERT**: 54.70ms (~18 req/s)
- **Toxicity**: 321.73ms (~3 req/s, multi-label)

### **All Models Working:**
- ✅ **DistilBERT** (transformer, best accuracy)
- ✅ **Logistic Regression** (baseline, 30x faster)
- ✅ **Linear SVM** (baseline, 29x faster)
- ✅ **Toxicity** (**FIXED** - now works with /predict endpoint!)

### **API Endpoints Verified:**
- ✅ `/health` - Returns all 4 models available
- ✅ `/predict` - Works with all models including toxicity
- ✅ `/models` - Lists model details and capabilities
- ✅ `/models/switch` - Dynamic switching between models
- ✅ `/docs` - Interactive API documentation

---

## What's Fixed

### ✅ All Critical Issues Resolved

1. **Git Clone** - Auto-detects branch (main/master/other)
2. **Directory Checks** - Verifies directory exists before cd
3. **Docker Permissions** - Uses sudo for all docker commands
4. **Error Handling** - Properly checks exit codes and fails fast
5. **Success Validation** - Only prints [OK] when actually successful

## Expected Output

### ✅ Successful Deployment

```
============================================
PHASE 1: Setup Cloud Storage
============================================
[1/3] Creating GCS bucket...
[OK] Bucket already exists

[2/3] Uploading models to GCS...
  [OK] Baseline models uploaded
  [OK] Toxicity model uploaded
  [OK] DistilBERT uploaded
  [OK] DistilBERT Fullscale uploaded

[3/3] Verifying uploads...
[OK] Models uploaded to GCS

============================================
PHASE 2: Setup Compute VM
============================================
[1/2] Checking VM status...
[OK] VM is already running

============================================
PHASE 3: Deploy Application
============================================
[1/5] Cloning repository...
Detected branch: main
[OK] Cloned with branch: main
[OK] Repository cloned successfully
[OK] Repository cloned

[2/5] Downloading models from GCS...
[INFO] Downloading models from GCS...
[OK] Models downloaded successfully
[OK] Models downloaded

[3/5] Building Docker image...
[INFO] Building Docker image...
[INFO] This may take 5-10 minutes...
[OK] Docker image built successfully
[OK] Docker image built

[4/5] Starting container...
[INFO] Stopping old container (if exists)...
[INFO] Starting new container...
[INFO] Waiting for container to start...
[OK] Container is running
[OK] Health check passed
[OK] Container started successfully
[OK] Container started

[5/5] Testing external access...
Testing http://35.232.76.140:8000/health
[OK] API accessible externally

============================================
  DEPLOYMENT COMPLETE!
============================================
Total Duration: 25:30

Resources Created:
  GCS Bucket: gs://nlp-classifier-models
  VM: nlp-classifier-vm (us-central1-a)
  External IP: 35.232.76.140

API Endpoints:
  Health:  http://35.232.76.140:8000/health
  Predict: http://35.232.76.140:8000/predict
  Docs:    http://35.232.76.140:8000/docs
  Models:  http://35.232.76.140:8000/models

[OK] Your NLP API is now live!
```

### ❌ Failed Deployment (Example)

```
[1/5] Cloning repository...
Detected branch: main
fatal: Remote branch main not found in upstream origin
[ERROR] Failed to clone repository (exit code: 1)

Possible issues:
  1. Branch 'main' does not exist in the repository
  2. Repository URL is incorrect: https://github.com/...
  3. Repository is private and VM cannot access it
```

**Script exits immediately - no false success messages!**

## Verify Deployment

### 1. Check Container Status
```powershell
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a --command="sudo docker ps"
```

Expected output:
```
CONTAINER ID   IMAGE                           STATUS         PORTS
abc123def456   cloud-nlp-classifier:latest     Up 2 minutes   0.0.0.0:8000->8000/tcp
```

### 2. Test Health Endpoint
```powershell
curl http://35.232.76.140:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "current_model": "distilbert",
  "available_models": ["distilbert", "logistic_regression", "linear_svm"],
  "classes": ["hate_speech", "offensive_language", "neither"]
}
```

### 3. Test Prediction
```powershell
curl -X POST http://35.232.76.140:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"text": "This is a test message"}'
```

Expected output:
```json
{
  "predicted_label": "neither",
  "confidence": 0.95,
  "model_name": "distilbert",
  "inference_time_ms": 8.14
}
```

### 4. Check Container Logs
```powershell
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a --command="sudo docker logs nlp-api"
```

Expected output:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Loading model: distilbert
INFO:     Model loaded successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Troubleshooting

### Issue: Git clone fails

**Error:**
```
fatal: Remote branch main not found in upstream origin
```

**Solution:**
1. Check your repository's default branch:
   ```powershell
   git ls-remote --heads https://github.com/dhairyamishra/CLOUD-NLP-CLASSIFIER-GCP.git
   ```

2. If it's `master` instead of `main`, the script will auto-detect and use it

3. If repository is private, make it public or set up SSH keys on VM

### Issue: Docker permission denied

**Error:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
The script now uses `sudo` for all docker commands. If you still see this error:

1. Verify Docker is running on VM:
   ```bash
   gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
   sudo systemctl status docker
   ```

2. If not running, start it:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

### Issue: Container not running

**Error:**
```
[ERROR] Container is not running
```

**Solution:**
1. Check container logs:
   ```bash
   gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
   sudo docker logs nlp-api
   ```

2. Common causes:
   - Model files missing or corrupted
   - Port 8000 already in use
   - Insufficient memory

3. Check disk space:
   ```bash
   df -h
   ```

4. Check memory:
   ```bash
   free -h
   ```

### Issue: Health check fails

**Error:**
```
[WARN] Health check not ready yet
```

**Solution:**
This is normal if the container is still loading the model. Wait 30-60 seconds and test again:

```powershell
curl http://35.232.76.140:8000/health
```

If it still fails after 2 minutes:
1. Check container is running: `sudo docker ps`
2. Check container logs: `sudo docker logs nlp-api`
3. Verify port 8000 is open in firewall

## Manual Deployment Steps (If Script Fails)

If the automated script fails, you can deploy manually:

### 1. SSH into VM
```powershell
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
```

### 2. Clone Repository
```bash
rm -rf ~/CLOUD-NLP-CLASSIFIER-GCP
git clone https://github.com/dhairyamishra/CLOUD-NLP-CLASSIFIER-GCP.git ~/CLOUD-NLP-CLASSIFIER-GCP
cd ~/CLOUD-NLP-CLASSIFIER-GCP
```

### 3. Download Models
```bash
mkdir -p models/baselines models/toxicity_multi_head models/transformer/distilbert models/transformer/distilbert_fullscale

gcloud storage cp gs://nlp-classifier-models/models/baselines/*.joblib models/baselines/ --recursive
gcloud storage cp gs://nlp-classifier-models/models/toxicity_multi_head/* models/toxicity_multi_head/ --recursive
gcloud storage cp gs://nlp-classifier-models/models/transformer/distilbert/* models/transformer/distilbert/ --recursive
gcloud storage cp gs://nlp-classifier-models/models/transformer/distilbert_fullscale/* models/transformer/distilbert_fullscale/ --recursive
```

### 4. Build Docker Image
```bash
sudo docker build -t cloud-nlp-classifier:latest .
```

### 5. Run Container
```bash
sudo docker stop nlp-api 2>/dev/null || true
sudo docker rm nlp-api 2>/dev/null || true

sudo docker run -d \
  --name nlp-api \
  -p 8000:8000 \
  --restart unless-stopped \
  cloud-nlp-classifier:latest
```

### 6. Verify
```bash
sudo docker ps
curl http://localhost:8000/health
```

## Cost Management

### Stop VM to Save Costs
```powershell
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a
```

### Start VM
```powershell
gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
```

### Delete Everything (Cleanup)
```powershell
# Delete VM
gcloud compute instances delete nlp-classifier-vm --zone=us-central1-a

# Delete GCS bucket
gcloud storage rm -r gs://nlp-classifier-models

# Release static IP (if you have one)
gcloud compute addresses delete nlp-classifier-ip --region=us-central1
```

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Try switching models via API
3. ✅ Run performance tests
4. ✅ Set up monitoring (optional)
5. ✅ Configure DNS (optional)
6. ✅ Add SSL/HTTPS (optional)

## Support

If you encounter issues not covered here:

1. Check `DEPLOYMENT_FIXES_SUMMARY.md` for detailed fix explanations
2. Check container logs: `sudo docker logs nlp-api`
3. Check VM logs: `gcloud compute ssh ... --command="journalctl -u docker"`
4. Verify firewall rules: `gcloud compute firewall-rules list`

---

**Ready to deploy!** Run: `.\scripts\gcp-complete-deployment.ps1`
