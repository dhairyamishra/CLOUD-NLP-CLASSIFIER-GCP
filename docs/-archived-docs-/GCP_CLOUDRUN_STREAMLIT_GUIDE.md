# ☁️ GCP Cloud Run Deployment Guide - Streamlit UI

## 📋 Overview

This guide covers deploying the Streamlit UI to Google Cloud Run for production use.

**Note**: Cloud Run is serverless and scales automatically, but Streamlit UI requires persistent connections, so consider costs carefully.

---

## 🎯 Prerequisites

### 1. GCP Account & Project

```bash
# Install gcloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Docker & Models

```bash
# Ensure models are trained
ls -la models/transformer/distilbert/

# Test Docker build locally
docker build -f Dockerfile.streamlit -t cloud-nlp-ui:test .
docker run -p 8501:8501 cloud-nlp-ui:test
```

---

## 🚀 Deployment Options

### Option 1: Deploy from Local Docker Image (Recommended)

#### Step 1: Build and Tag Image

```bash
# Set variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE_NAME="nlp-classifier-ui"

# Build image
docker build -f Dockerfile.streamlit \
  -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest .

# Or use Artifact Registry
docker build -f Dockerfile.streamlit \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run/${SERVICE_NAME}:latest .
```

#### Step 2: Push to Container Registry

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Push to GCR
docker push gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest

# Or push to Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run/${SERVICE_NAME}:latest
```

#### Step 3: Deploy to Cloud Run

```bash
# Deploy with recommended settings
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 80 \
  --set-env-vars="STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_HEADLESS=true"

# Get service URL
gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format 'value(status.url)'
```

### Option 2: Deploy from Source (Cloud Build)

#### Step 1: Create cloudbuild.yaml

```yaml
# cloudbuild.streamlit.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-f'
      - 'Dockerfile.streamlit'
      - '-t'
      - 'gcr.io/$PROJECT_ID/nlp-classifier-ui:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/nlp-classifier-ui:latest'
      - '.'

  # Push the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/nlp-classifier-ui:$SHORT_SHA'

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'nlp-classifier-ui'
      - '--image'
      - 'gcr.io/$PROJECT_ID/nlp-classifier-ui:$SHORT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/nlp-classifier-ui:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/nlp-classifier-ui:latest'

timeout: 1200s
```

#### Step 2: Deploy with Cloud Build

```bash
# Submit build
gcloud builds submit \
  --config cloudbuild.streamlit.yaml \
  --timeout 20m

# Build time: ~10-15 minutes
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Set environment variables
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --set-env-vars="
STREAMLIT_SERVER_PORT=8501,
STREAMLIT_SERVER_HEADLESS=true,
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false,
STREAMLIT_SERVER_ENABLE_CORS=false,
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
"
```

### Resource Allocation

```bash
# Update resources
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 80
```

**Recommended Settings:**
- **Memory**: 2Gi (Streamlit + models)
- **CPU**: 2 (for faster inference)
- **Timeout**: 300s (5 minutes)
- **Concurrency**: 80 (Streamlit handles multiple users)
- **Min Instances**: 0 (cost-effective)
- **Max Instances**: 10 (prevent runaway costs)

### Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service ${SERVICE_NAME} \
  --domain ui.your-domain.com \
  --region ${REGION}

# Follow DNS instructions
```

---

## 🔒 Security

### Authentication

```bash
# Require authentication
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --no-allow-unauthenticated

# Access with auth
gcloud run services proxy ${SERVICE_NAME} \
  --region ${REGION} \
  --port 8501
```

### IAM Permissions

```bash
# Allow specific users
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
  --region ${REGION} \
  --member="user:user@example.com" \
  --role="roles/run.invoker"

# Allow service account
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
  --region ${REGION} \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### VPC Connector (Optional)

```bash
# Create VPC connector for private resources
gcloud compute networks vpc-access connectors create nlp-connector \
  --region ${REGION} \
  --range 10.8.0.0/28

# Use connector
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --vpc-connector nlp-connector
```

---

## 💰 Cost Optimization

### Pricing Factors

```
Cloud Run Pricing (us-central1):
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests
- Networking: $0.12 per GB egress

Example Monthly Cost (moderate usage):
- 10,000 requests/month
- 2 vCPU, 2Gi memory
- 30s average request time
- ~$15-25/month
```

### Cost-Saving Tips

1. **Use Min Instances = 0**
   ```bash
   --min-instances 0  # Scale to zero when idle
   ```

2. **Set Max Instances**
   ```bash
   --max-instances 10  # Prevent runaway costs
   ```

3. **Optimize Timeout**
   ```bash
   --timeout 60  # Shorter timeout = lower costs
   ```

4. **Use Smaller Resources**
   ```bash
   --memory 1Gi --cpu 1  # If models are small
   ```

5. **Monitor Usage**
   ```bash
   # View metrics
   gcloud monitoring dashboards list
   ```

---

## 📊 Monitoring

### View Logs

```bash
# Stream logs
gcloud run services logs tail ${SERVICE_NAME} \
  --region ${REGION}

# View in Cloud Console
https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/logs
```

### Metrics

```bash
# View metrics
gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format yaml

# Key metrics:
# - Request count
# - Request latency
# - Container instance count
# - CPU/Memory utilization
```

### Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

---

## 🔄 Updates & Rollbacks

### Update Service

```bash
# Build new image
docker build -f Dockerfile.streamlit -t gcr.io/${PROJECT_ID}/${SERVICE_NAME}:v2 .
docker push gcr.io/${PROJECT_ID}/${SERVICE_NAME}:v2

# Deploy update
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:v2

# Gradual rollout (traffic splitting)
gcloud run services update-traffic ${SERVICE_NAME} \
  --region ${REGION} \
  --to-revisions=LATEST=50,PREVIOUS=50
```

### Rollback

```bash
# List revisions
gcloud run revisions list \
  --service ${SERVICE_NAME} \
  --region ${REGION}

# Rollback to previous
gcloud run services update-traffic ${SERVICE_NAME} \
  --region ${REGION} \
  --to-revisions=PREVIOUS=100
```

---

## 🐛 Troubleshooting

### Issue 1: Container Fails to Start

```bash
# Check logs
gcloud run services logs tail ${SERVICE_NAME} --region ${REGION}

# Common causes:
# 1. Port mismatch (must be 8501)
# 2. Missing models
# 3. Insufficient memory
```

### Issue 2: High Latency

```bash
# Increase resources
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --memory 4Gi \
  --cpu 4

# Use min instances to keep warm
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --min-instances 1
```

### Issue 3: Timeout Errors

```bash
# Increase timeout
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --timeout 600

# Max timeout: 3600s (1 hour)
```

---

## 🎯 Production Checklist

- [ ] Models are optimized and < 500MB
- [ ] Docker image builds successfully
- [ ] Health check endpoint works
- [ ] Environment variables are set
- [ ] Resource limits are appropriate
- [ ] Authentication is configured
- [ ] Custom domain is mapped (optional)
- [ ] Monitoring and alerts are set up
- [ ] Cost budget alerts are configured
- [ ] Backup/rollback plan is documented

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Streamlit on Cloud Run](https://docs.streamlit.io/knowledge-base/tutorials/deploy/gcp)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)

---

## 🚨 Important Notes

### Limitations

1. **Cold Starts**: First request after idle may take 10-30s
2. **WebSocket**: Streamlit uses WebSockets, ensure they're not blocked
3. **Session State**: Each instance has its own state (not shared)
4. **File System**: Ephemeral, don't store data in container

### Alternatives

If Cloud Run doesn't meet your needs:

1. **GCP Compute Engine**: Full VM control, persistent storage
2. **GKE (Kubernetes)**: Better for complex deployments
3. **App Engine**: Simpler but less flexible
4. **Streamlit Cloud**: Managed Streamlit hosting (free tier)

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-09  
**Status**: Ready for Deployment ✅
