# 🚀 GCP Deployment Guide

## 📋 **Quick Answer to Your Questions**

### **Q: How are we creating and running the VM in the cloud?**
**A:** The VM is created using `gcloud compute instances create` (already done in Phase 1-3). The VM is a **Linux virtual machine** running in Google Cloud.

### **Q: Are we using Docker for that?**
**A:** **No!** Docker does NOT create the VM. Here's the hierarchy:
```
GCP Cloud
  └─ VM (Linux machine - created by gcloud)
      └─ Docker (runs inside VM)
          └─ Container (your FastAPI app)
```

### **Q: Can we set it up to first create the VM and then clone the repo and make a bucket?**
**A:** **Yes!** That's exactly what the new `gcp-complete-deployment.ps1` script does!

---

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────┐
│  YOUR LOCAL MACHINE                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │  1. Run deployment script                          │ │
│  │  2. Upload models to GCS                           │ │
│  │  3. Configure VM                                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  GOOGLE CLOUD PLATFORM                                   │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Cloud Storage   │         │  Compute Engine  │     │
│  │  (GCS Bucket)    │         │  (VM)            │     │
│  │                  │         │                  │     │
│  │  models/         │────────>│  Docker Engine   │     │
│  │  - baselines/    │         │  ┌────────────┐  │     │
│  │  - transformer/  │         │  │ Container  │  │     │
│  │  - toxicity/     │         │  │            │  │     │
│  └──────────────────┘         │  │  FastAPI   │  │     │
│                                │  │  :8000     │  │     │
│  ┌──────────────────┐         │  └────────────┘  │     │
│  │  GitHub          │────────>│                  │     │
│  │  (Your Repo)     │         │  ~/CLOUD-NLP-    │     │
│  │  - Source Code   │         │  CLASSIFIER-GCP  │     │
│  └──────────────────┘         └──────────────────┘     │
│                                         │               │
│                                         ▼               │
│                                ┌──────────────────┐     │
│                                │  External IP     │     │
│                                │  35.232.76.140   │     │
│                                │  Port: 8000      │     │
│                                └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 **Deployment Options**

### **Option 1: Complete Deployment (Recommended)**

Use this if you want **everything automated**:

```powershell
# Edit the script first:
# 1. Update line 16: GitRepo URL
# 2. Verify other parameters

# Run complete deployment
.\scripts\gcp-complete-deployment.ps1
```

**What it does:**
1. ✅ Creates GCS bucket
2. ✅ Uploads models (~770 MB)
3. ✅ Verifies VM is running
4. ✅ Clones your GitHub repo
5. ✅ Downloads models from GCS
6. ✅ Builds Docker image
7. ✅ Runs container
8. ✅ Tests API

**Time:** ~15-20 minutes

---

### **Option 2: Step-by-Step Deployment**

If you prefer **manual control**:

#### **Step 1: Upload Models to GCS**
```powershell
.\scripts\gcp-phase4a-upload-models-to-gcs.ps1
```

#### **Step 2: Deploy Application**
```powershell
# Edit line 13: Update GitRepo URL
.\scripts\gcp-phase4b-deploy-with-gcs-models.ps1
```

---

## 📦 **What Each Component Does**

### **1. GCS Bucket (Cloud Storage)**
- **Purpose:** Store trained models
- **Why:** Separates code from models
- **Cost:** ~$0.02/month for 770 MB
- **Location:** `gs://nlp-classifier-models/models/`

### **2. VM (Virtual Machine)**
- **Purpose:** Run your application
- **Specs:** e2-standard-2 (2 vCPU, 8GB RAM, 50GB SSD)
- **OS:** Debian Linux with Docker pre-installed
- **Cost:** ~$49/month
- **Created:** Already done in Phase 1-3

### **3. Docker (Inside VM)**
- **Purpose:** Containerize your application
- **Why:** Consistent environment, easy deployment
- **Image:** Includes Python, PyTorch, FastAPI, models
- **Size:** ~2-3 GB

### **4. Container (Inside Docker)**
- **Purpose:** Run your FastAPI application
- **Port:** 8000
- **Auto-restart:** Yes (unless-stopped)
- **Contains:** Your code + models + dependencies

---

## 🔄 **Deployment Flow**

```
1. LOCAL: Upload models to GCS
   └─> gsutil cp models/* gs://bucket/

2. LOCAL: Trigger VM deployment
   └─> gcloud compute ssh VM

3. VM: Clone code from GitHub
   └─> git clone https://github.com/...

4. VM: Download models from GCS
   └─> gsutil cp gs://bucket/* ~/models/

5. VM: Build Docker image
   └─> docker build -t app .

6. VM: Run container
   └─> docker run -p 8000:8000 app

7. EXTERNAL: Access API
   └─> curl http://35.232.76.140:8000/health
```

---

## 🛠️ **Common Operations**

### **Update Code**
```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Update code
cd ~/CLOUD-NLP-CLASSIFIER-GCP
git pull

# Rebuild and restart
docker build -t cloud-nlp-classifier:latest .
docker stop nlp-api && docker rm nlp-api
docker run -d --name nlp-api -p 8000:8000 --restart unless-stopped cloud-nlp-classifier:latest
```

### **Update Models**
```powershell
# 1. Upload new models from local
.\scripts\gcp-phase4a-upload-models-to-gcs.ps1

# 2. On VM, download and rebuild
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a
cd ~/CLOUD-NLP-CLASSIFIER-GCP
gsutil -m cp -r gs://nlp-classifier-models/models/* models/
docker build -t cloud-nlp-classifier:latest .
docker restart nlp-api
```

### **View Logs**
```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# View container logs
docker logs -f nlp-api

# View last 100 lines
docker logs --tail 100 nlp-api
```

### **Stop/Start VM**
```powershell
# Stop VM (saves money)
gcloud compute instances stop nlp-classifier-vm --zone=us-central1-a

# Start VM
gcloud compute instances start nlp-classifier-vm --zone=us-central1-a
```

---

## 💰 **Cost Breakdown**

| Resource | Specs | Cost/Month |
|----------|-------|------------|
| VM | e2-standard-2 (2 vCPU, 8GB RAM) | ~$49 |
| Static IP | 1 IP address | ~$7 |
| GCS Storage | 770 MB models | ~$0.02 |
| **Total** | | **~$56/month** |

**Cost Savings:**
- Stop VM when not in use: $0/hour (only pay for storage)
- Use preemptible VM: ~$15/month (but can be terminated)

---

## 🔧 **Troubleshooting**

### **Issue: VM doesn't exist**
```powershell
# The VM should have been created in Phase 1-3
# Check if it exists:
gcloud compute instances list

# If not, you need to create it first
# (Run the Phase 1-3 scripts from previous session)
```

### **Issue: Models not uploading**
```powershell
# Check if models exist locally
ls models/

# Check GCS bucket
gsutil ls gs://nlp-classifier-models/

# Manually upload if needed
gsutil -m cp -r models/* gs://nlp-classifier-models/models/
```

### **Issue: Docker build fails**
```bash
# SSH into VM
gcloud compute ssh nlp-classifier-vm --zone=us-central1-a

# Check Docker
docker --version

# Check disk space
df -h

# Check logs
cd ~/CLOUD-NLP-CLASSIFIER-GCP
docker build -t cloud-nlp-classifier:latest . 2>&1 | tee build.log
```

### **Issue: Can't access API externally**
```bash
# Check firewall rules
gcloud compute firewall-rules list | grep 8000

# Check container is running
docker ps | grep nlp-api

# Check from inside VM
curl http://localhost:8000/health

# Get external IP
gcloud compute instances describe nlp-classifier-vm --zone=us-central1-a --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

---

## ✅ **Pre-Deployment Checklist**

Before running the deployment:

- [ ] VM exists and is running (from Phase 1-3)
- [ ] Models are trained locally in `models/` directory
- [ ] GitHub repo URL is updated in script
- [ ] GitHub repo is public (or VM has access)
- [ ] `gcloud` CLI is authenticated
- [ ] `gsutil` is working
- [ ] Docker is installed on VM

---

## 🎯 **Next Steps After Deployment**

1. **Test the API:**
   ```bash
   curl http://35.232.76.140:8000/health
   curl http://35.232.76.140:8000/models
   ```

2. **Test predictions:**
   ```bash
   curl -X POST http://35.232.76.140:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"text": "This is a test message"}'
   ```

3. **Access Swagger docs:**
   ```
   http://35.232.76.140:8000/docs
   ```

4. **Monitor performance:**
   ```bash
   docker stats nlp-api
   ```

5. **Set up monitoring** (Optional - Phase 9)

---

## 📚 **Additional Resources**

- **Docker Guide:** `docs/DOCKER_GUIDE.md`
- **Multi-Model Guide:** `docs/MULTI_MODEL_DOCKER_GUIDE.md`
- **API Documentation:** `src/api/README.md`
- **Resume Deployment:** `RESUME_DEPLOYMENT.md`

---

## 🆘 **Need Help?**

1. Check logs: `docker logs nlp-api`
2. SSH into VM: `gcloud compute ssh nlp-classifier-vm --zone=us-central1-a`
3. Review this guide
4. Check GCP Console: https://console.cloud.google.com

---

**Status:** Ready to deploy! 🚀
