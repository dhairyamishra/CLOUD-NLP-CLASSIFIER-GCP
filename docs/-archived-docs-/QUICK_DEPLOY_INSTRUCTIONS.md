# Quick Deployment Instructions

## Issue Fixed
✅ **Fixed gsutil permission error** - Script now uses `gcloud storage` commands instead

## Prerequisites
Before running the deployment script, ensure:

1. ✅ **gcloud CLI authenticated**
   ```powershell
   gcloud auth list
   # Should show: dhairya28m@gmail.com (active)
   ```

2. ✅ **Project configured**
   ```powershell
   gcloud config get-value project
   # Should show: mnist-k8s-pipeline
   ```

3. ✅ **VM exists and is running**
   ```powershell
   gcloud compute instances describe nlp-classifier-vm --zone=us-central1-a
   # Should show: status: RUNNING
   ```

4. ✅ **Models exist locally**
   ```powershell
   ls C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP\models
   # Should show: baselines, toxicity_multi_head, transformer
   ```

## Run Complete Deployment

### Option 1: Full Deployment (Recommended for first time)
```powershell
.\scripts\gcp-complete-deployment.ps1
```

This will:
- ✅ Create GCS bucket (if not exists)
- ✅ Upload all models to GCS (~770 MB, 5-10 minutes)
- ✅ Verify VM is running
- ✅ Clone repository on VM
- ✅ Download models from GCS to VM
- ✅ Build Docker image (~10 minutes)
- ✅ Start container
- ✅ Test API endpoints

**Total Time:** 20-30 minutes

### Option 2: Skip Model Upload (if models already in GCS)
```powershell
.\scripts\gcp-complete-deployment.ps1 -SkipModelUpload
```

**Total Time:** 15-20 minutes

## What to Expect

### Phase 1: Cloud Storage Setup (5-10 min)
```
[1/3] Creating GCS bucket...
[OK] Bucket created (or already exists)

[2/3] Uploading models to GCS...
  > Uploading baseline models...
  [OK] Baseline models uploaded
  > Uploading toxicity model...
  [OK] Toxicity model uploaded
  > Uploading DistilBERT model...
  [OK] DistilBERT uploaded
  > Uploading DistilBERT Fullscale...
  [OK] DistilBERT Fullscale uploaded

[3/3] Verifying uploads...
[OK] Models uploaded to GCS
```

### Phase 2: VM Setup (1-2 min)
```
[1/2] Checking VM status...
[OK] VM is already running
```

### Phase 3: Application Deployment (15-20 min)
```
[1/5] Cloning repository...
[OK] Repository cloned

[2/5] Downloading models from GCS...
[OK] Models downloaded

[3/5] Building Docker image...
[OK] Docker image built

[4/5] Starting container...
[OK] Container started

[5/5] Testing external access...
[OK] API accessible externally
```

## After Deployment

### Access Your API
```
Health:  http://35.232.76.140:8000/health
Predict: http://35.232.76.140:8000/predict
Docs:    http://35.232.76.140:8000/docs
Models:  http://35.232.76.140:8000/models
```

### Test the API
```powershell
# Health check
curl http://35.232.76.140:8000/health

# Prediction with DistilBERT (default)
curl -X POST http://35.232.76.140:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"text": "This is a test message"}'

# List all models
curl http://35.232.76.140:8000/models

# Switch to ultra-fast Logistic Regression
curl -X POST http://35.232.76.140:8000/models/switch `
  -H "Content-Type: application/json" `
  -d '{"model_name": "logistic_regression"}'

# Make prediction with Logistic Regression (~30x faster!)
curl -X POST http://35.232.76.140:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"text": "This should be much faster!"}'
```

### Performance Results
**All 4 models working perfectly:**
- **Logistic Regression**: 1.84ms (~543 req/s)
- **Linear SVM**: 1.86ms (~537 req/s)
- **DistilBERT**: 54.70ms (~18 req/s)
- **Toxicity**: 321.73ms (~3 req/s, multi-label)

---

## Stop VM to Save Costs
```powershell
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
```

### View Container Logs
```bash
# On VM
docker logs -f nlp-api
```

### Check Container Status
```bash
# On VM
docker ps
docker stats nlp-api
```

## Troubleshooting

### If deployment fails at any phase:

1. **Check VM is running:**
   ```powershell
   gcloud compute instances describe nlp-classifier-vm --zone=us-central1-a
   ```

2. **Check GCS bucket:**
   ```powershell
   gcloud storage ls gs://nlp-classifier-models/models/
   ```

3. **SSH and check manually:**
   ```powershell
   gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
   cd ~/CLOUD-NLP-CLASSIFIER-GCP
   docker ps -a
   docker logs nlp-api
   ```

4. **Re-run specific phase:**
   - Phase 1 only: Use `-SkipVMCreation` flag
   - Skip uploads: Use `-SkipModelUpload` flag

## Cost Tracking

- **VM (e2-standard-2):** ~$0.07/hour = ~$49/month
- **Static IP:** ~$0.24/day = ~$7/month
- **GCS Storage (770 MB):** ~$0.02/month
- **GCS Network (egress):** ~$0.12/GB (one-time for download)

**Total Monthly:** ~$56

## Stop VM to Save Costs
```powershell
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a
```

## Restart VM
```powershell
gcloud compute instances start nlp-classifier-vm --zone=us-central1-a

# Wait 30 seconds, then check
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a --command="docker ps"
```

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Try switching between models
3. ✅ Run performance tests
4. ✅ Set up monitoring (optional)
5. ✅ Configure DNS (optional)
6. ✅ Add SSL/HTTPS (optional)

## Support

If you encounter issues:
1. Check `GCP_DEPLOYMENT_PROGRESS.md` for detailed status
2. Review `DEPLOYMENT_SUMMARY.md` for configuration
3. Check VM logs: `docker logs nlp-api`
4. Verify firewall rules allow ports 8000, 8501

---

**Ready to deploy!** Run: `.\scripts\gcp-complete-deployment.ps1`
