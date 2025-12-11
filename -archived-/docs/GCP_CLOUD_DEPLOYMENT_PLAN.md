# 🚀 GCP Cloud Deployment Plan - NLP Classifier Application

## 📋 Executive Summary

**Project**: Cloud NLP Text Classification System  
**Current Status**: ✅ Production Ready (10/10 phases complete, 326+ tests passing)  
**Deployment Goal**: Deploy to GCP with external IP access and persistent storage for models  
**Target Date**: TBD  
**Estimated Cost**: $20-150/month (depending on deployment option)

---

## 🎯 Deployment Requirements

### Functional Requirements
- ✅ **External IP Access**: Public URL accessible from anywhere
- ✅ **Persistent Storage**: PVC/volume mount for model files (~3-5 GB)
- ✅ **Multi-Model Support**: All 3 models (DistilBERT, LogReg, LinearSVM)
- ✅ **API + UI**: Both FastAPI backend and Streamlit frontend
- ✅ **High Availability**: Auto-scaling and health checks
- ✅ **Security**: HTTPS, authentication options, IAM controls

### Technical Requirements
- **Memory**: 2-4 GB per instance
- **CPU**: 2-4 vCPUs
- **Storage**: 10-50 GB persistent disk for models
- **Network**: External load balancer with static IP
- **Performance**: <100ms API latency, <2s UI load time

---

## 🏗️ Deployment Architecture Options

We have **3 primary deployment options** on GCP, each with different trade-offs:

### Option 1: Google Kubernetes Engine (GKE) ⭐ **RECOMMENDED**
**Best for**: Production workloads, scalability, persistent storage

**Pros:**
- ✅ Full Kubernetes control with PVC support
- ✅ Easy persistent volume management
- ✅ Horizontal pod autoscaling
- ✅ Load balancer with static external IP
- ✅ Rolling updates and zero-downtime deployments
- ✅ Best for long-running services

**Cons:**
- ❌ More complex setup (but most flexible)
- ❌ Higher minimum cost (~$70-100/month for cluster)
- ❌ Requires Kubernetes knowledge

**Cost Estimate**: $70-150/month
- GKE cluster: $70-100/month (e1-medium nodes)
- Persistent disk: $2-5/month (50GB SSD)
- Load balancer: $18/month
- Egress: $5-10/month

---

### Option 2: Cloud Run with Cloud Storage
**Best for**: Serverless, cost-effective, simple deployment

**Pros:**
- ✅ Serverless (pay per use)
- ✅ Auto-scaling to zero
- ✅ Simple deployment (single command)
- ✅ HTTPS by default
- ✅ Lowest cost for low/medium traffic

**Cons:**
- ❌ No true persistent volumes (use Cloud Storage instead)
- ❌ Cold start latency (10-30s)
- ❌ Models must be in container or loaded from GCS
- ❌ Limited to 4GB memory per instance

**Cost Estimate**: $15-50/month
- Cloud Run: $10-30/month (compute)
- Cloud Storage: $2-5/month (model storage)
- Egress: $3-10/month

---

### Option 3: Compute Engine VM with Docker
**Best for**: Simple setup, full control, persistent storage

**Pros:**
- ✅ Full VM control
- ✅ Easy persistent disk mounting
- ✅ Simple Docker Compose deployment
- ✅ No cold starts
- ✅ Predictable costs

**Cons:**
- ❌ Manual scaling (no auto-scaling)
- ❌ Manual updates and maintenance
- ❌ Always-on costs (even when idle)
- ❌ Single point of failure (unless using instance groups)

**Cost Estimate**: $50-100/month
- VM (e2-standard-2): $50-60/month
- Persistent disk: $2-5/month (50GB SSD)
- Static IP: $7/month (if reserved)
- Egress: $5-10/month

---

## 📊 Deployment Option Comparison

| Feature | GKE (Kubernetes) | Cloud Run | Compute Engine |
|---------|------------------|-----------|----------------|
| **Setup Complexity** | High | Low | Medium |
| **Persistent Storage** | ✅ Native PVC | ⚠️ Cloud Storage | ✅ Persistent Disk |
| **Auto-Scaling** | ✅ HPA | ✅ Built-in | ❌ Manual |
| **External IP** | ✅ Load Balancer | ✅ Automatic | ✅ Static IP |
| **Cold Starts** | ❌ None | ⚠️ 10-30s | ❌ None |
| **Min Cost** | $70/month | $15/month | $50/month |
| **Max Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Production Ready** | ✅ Best | ✅ Good | ✅ Good |
| **Maintenance** | Medium | Low | High |

---

## 🎯 RECOMMENDED: GKE Deployment Plan

Based on your requirements (external IP + persistent volumes), **GKE is the best option**.

---

## 📝 DETAILED TASK LIST - GKE DEPLOYMENT

### **PHASE 1: Pre-Deployment Setup** (Est. 1-2 hours)

#### Task 1.1: GCP Project Setup
- [ ] Create/select GCP project
- [ ] Enable billing on project
- [ ] Set up billing alerts ($50, $100, $150)
- [ ] Install/update `gcloud` CLI
- [ ] Authenticate: `gcloud auth login`
- [ ] Set default project: `gcloud config set project PROJECT_ID`

**Commands:**
```bash
# Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable billing alerts
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="NLP Classifier Budget" \
  --budget-amount=150USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

#### Task 1.2: Enable Required GCP APIs
- [ ] Enable Kubernetes Engine API
- [ ] Enable Container Registry API
- [ ] Enable Artifact Registry API
- [ ] Enable Compute Engine API
- [ ] Enable Cloud Storage API
- [ ] Enable Cloud Build API

**Commands:**
```bash
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### Task 1.3: Create Artifact Registry Repository
- [ ] Create Docker repository in Artifact Registry
- [ ] Configure Docker authentication
- [ ] Test push/pull access

**Commands:**
```bash
# Create repository
gcloud artifacts repositories create nlp-classifier \
  --repository-format=docker \
  --location=us-central1 \
  --description="NLP Classifier Docker Images"

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev
```

#### Task 1.4: Prepare Docker Images
- [ ] Verify all models are trained and present
- [ ] Test Docker builds locally
- [ ] Optimize Docker images (multi-stage builds)
- [ ] Tag images for Artifact Registry

**Commands:**
```bash
# Verify models
ls -la models/transformer/distilbert/
ls -la models/baselines/
ls -la models/toxicity_multi_head/

# Build and tag API image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:latest -f Dockerfile .

# Build and tag UI image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:latest -f Dockerfile.streamlit .

# Test locally
docker-compose up -d
# Test endpoints, then stop
docker-compose down
```

---

### **PHASE 2: GKE Cluster Creation** (Est. 30-60 min)

#### Task 2.1: Create GKE Cluster
- [ ] Choose cluster configuration (Standard or Autopilot)
- [ ] Select region/zone (us-central1 recommended)
- [ ] Configure node pool (e2-standard-2, 2-4 nodes)
- [ ] Enable autoscaling
- [ ] Create cluster

**Commands:**
```bash
# Option A: Standard GKE Cluster (more control)
gcloud container clusters create nlp-classifier-cluster \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --num-nodes=2 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=4 \
  --disk-size=50 \
  --disk-type=pd-standard \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-ip-alias \
  --network="default" \
  --subnetwork="default" \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

# Option B: Autopilot GKE (simpler, more expensive)
gcloud container clusters create-auto nlp-classifier-cluster \
  --region=us-central1

# Get credentials
gcloud container clusters get-credentials nlp-classifier-cluster \
  --zone=us-central1-a
```

**Cluster Specs:**
- **Machine Type**: e2-standard-2 (2 vCPU, 8GB RAM)
- **Nodes**: 2-4 (autoscaling)
- **Disk**: 50GB per node
- **Cost**: ~$70-100/month

#### Task 2.2: Verify Cluster Access
- [ ] Test kubectl connectivity
- [ ] Verify node status
- [ ] Check cluster info

**Commands:**
```bash
# Test kubectl
kubectl cluster-info
kubectl get nodes
kubectl get namespaces

# Should see 2 nodes in Ready state
```

---

### **PHASE 3: Persistent Storage Setup** (Est. 30 min)

#### Task 3.1: Create Persistent Volume Claims
- [ ] Create PVC for model storage (10-50GB)
- [ ] Create PVC for logs (optional, 5-10GB)
- [ ] Verify PVC creation

**Create file: `k8s/persistent-volumes.yaml`**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nlp-models-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard-rwo
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nlp-logs-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard-rwo
```

**Commands:**
```bash
# Apply PVCs
kubectl apply -f k8s/persistent-volumes.yaml

# Verify
kubectl get pvc
# Should show Bound status
```

#### Task 3.2: Upload Models to Persistent Volume
- [ ] Create temporary pod to mount PVC
- [ ] Copy model files to PVC
- [ ] Verify files are accessible

**Create file: `k8s/model-uploader-pod.yaml`**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: model-uploader
spec:
  containers:
  - name: uploader
    image: busybox
    command: ['sh', '-c', 'sleep 3600']
    volumeMounts:
    - name: models
      mountPath: /models
  volumes:
  - name: models
    persistentVolumeClaim:
      claimName: nlp-models-pvc
```

**Commands:**
```bash
# Create uploader pod
kubectl apply -f k8s/model-uploader-pod.yaml

# Wait for pod to be ready
kubectl wait --for=condition=ready pod/model-uploader --timeout=60s

# Copy models to PVC
kubectl cp models/transformer/distilbert model-uploader:/models/transformer/distilbert
kubectl cp models/baselines model-uploader:/models/baselines
kubectl cp models/toxicity_multi_head model-uploader:/models/toxicity_multi_head

# Verify
kubectl exec model-uploader -- ls -la /models

# Delete uploader pod
kubectl delete pod model-uploader
```

---

### **PHASE 4: Push Docker Images** (Est. 15-30 min)

#### Task 4.1: Build and Push API Image
- [ ] Build optimized API image
- [ ] Push to Artifact Registry
- [ ] Verify image in registry

**Commands:**
```bash
# Build API image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:v1.0 -f Dockerfile .
docker tag us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:v1.0 \
  us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:latest

# Push
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:v1.0
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:latest

# Verify
gcloud artifacts docker images list us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier
```

#### Task 4.2: Build and Push UI Image
- [ ] Build optimized UI image
- [ ] Push to Artifact Registry
- [ ] Verify image in registry

**Commands:**
```bash
# Build UI image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:v1.0 -f Dockerfile.streamlit .
docker tag us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:v1.0 \
  us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:latest

# Push
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:v1.0
docker push us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:latest
```

---

### **PHASE 5: Kubernetes Manifests Creation** (Est. 1-2 hours)

#### Task 5.1: Create API Deployment
- [ ] Create API deployment YAML
- [ ] Configure resource limits
- [ ] Mount persistent volumes
- [ ] Set environment variables
- [ ] Configure health checks

**Create file: `k8s/api-deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nlp-api
  labels:
    app: nlp-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nlp-api
  template:
    metadata:
      labels:
        app: nlp-api
    spec:
      containers:
      - name: api
        image: us-central1-docker.pkg.dev/PROJECT_ID/nlp-classifier/api:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DEFAULT_MODEL
          value: "distilbert"
        - name: LOG_LEVEL
          value: "info"
        - name: WORKERS
          value: "1"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "3Gi"
            cpu: "2000m"
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: nlp-models-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: nlp-logs-pvc
```

#### Task 5.2: Create API Service
- [ ] Create ClusterIP service for internal access
- [ ] Configure port mapping

**Create file: `k8s/api-service.yaml`**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nlp-api-service
  labels:
    app: nlp-api
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: nlp-api
```

#### Task 5.3: Create UI Deployment
- [ ] Create UI deployment YAML
- [ ] Configure resource limits
- [ ] Mount models volume (read-only)
- [ ] Set Streamlit environment variables

**Create file: `k8s/ui-deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nlp-ui
  labels:
    app: nlp-ui
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nlp-ui
  template:
    metadata:
      labels:
        app: nlp-ui
    spec:
      containers:
      - name: ui
        image: us-central1-docker.pkg.dev/PROJECT_ID/nlp-classifier/ui:latest
        ports:
        - containerPort: 8501
          name: http
        env:
        - name: STREAMLIT_SERVER_PORT
          value: "8501"
        - name: STREAMLIT_SERVER_HEADLESS
          value: "true"
        - name: STREAMLIT_BROWSER_GATHER_USAGE_STATS
          value: "false"
        resources:
          requests:
            memory: "1.5Gi"
            cpu: "500m"
          limits:
            memory: "2.5Gi"
            cpu: "1500m"
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: nlp-models-pvc
```

#### Task 5.4: Create UI Service
- [ ] Create ClusterIP service for UI

**Create file: `k8s/ui-service.yaml`**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nlp-ui-service
  labels:
    app: nlp-ui
spec:
  type: ClusterIP
  ports:
  - port: 8501
    targetPort: 8501
    protocol: TCP
    name: http
  selector:
    app: nlp-ui
```

#### Task 5.5: Create Ingress with External IP
- [ ] Reserve static external IP
- [ ] Create Ingress resource
- [ ] Configure path-based routing
- [ ] Enable HTTPS (optional)

**Commands to reserve IP:**
```bash
# Reserve static IP
gcloud compute addresses create nlp-classifier-ip \
  --global

# Get the IP address
gcloud compute addresses describe nlp-classifier-ip \
  --global \
  --format="get(address)"
```

**Create file: `k8s/ingress.yaml`**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nlp-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "nlp-classifier-ip"
    networking.gke.io/managed-certificates: "nlp-cert"
    # Optional: Force HTTPS redirect
    # ingress.gcp.kubernetes.io/pre-shared-cert: "nlp-cert"
spec:
  rules:
  - http:
      paths:
      - path: /api/*
        pathType: ImplementationSpecific
        backend:
          service:
            name: nlp-api-service
            port:
              number: 8000
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: nlp-ui-service
            port:
              number: 8501
```

#### Task 5.6: Create HorizontalPodAutoscaler
- [ ] Configure autoscaling for API
- [ ] Configure autoscaling for UI

**Create file: `k8s/hpa.yaml`**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nlp-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nlp-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nlp-ui-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nlp-ui
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### **PHASE 6: Deploy to GKE** (Est. 30 min)

#### Task 6.1: Apply All Kubernetes Manifests
- [ ] Apply PVCs
- [ ] Apply API deployment and service
- [ ] Apply UI deployment and service
- [ ] Apply Ingress
- [ ] Apply HPA

**Commands:**
```bash
# Update PROJECT_ID in all YAML files
export PROJECT_ID="your-project-id"
find k8s/ -name "*.yaml" -exec sed -i "s/PROJECT_ID/$PROJECT_ID/g" {} \;

# Apply in order
kubectl apply -f k8s/persistent-volumes.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/ui-deployment.yaml
kubectl apply -f k8s/ui-service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

#### Task 6.2: Verify Deployments
- [ ] Check pod status
- [ ] Check service endpoints
- [ ] Check ingress status
- [ ] Verify external IP assignment

**Commands:**
```bash
# Check pods
kubectl get pods -w
# Wait for all pods to be Running

# Check services
kubectl get services

# Check ingress
kubectl get ingress nlp-ingress
# Note: External IP may take 5-10 minutes to provision

# Check HPA
kubectl get hpa

# View logs
kubectl logs -l app=nlp-api --tail=50
kubectl logs -l app=nlp-ui --tail=50
```

---

### **PHASE 7: Configure DNS and HTTPS** (Est. 30-60 min)

#### Task 7.1: Configure DNS (Optional)
- [ ] Get external IP from Ingress
- [ ] Create A record in DNS provider
- [ ] Point domain to external IP

**Commands:**
```bash
# Get external IP
kubectl get ingress nlp-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Configure DNS (example for Cloud DNS)
gcloud dns record-sets create nlp.yourdomain.com \
  --zone=your-dns-zone \
  --type=A \
  --ttl=300 \
  --rrdatas=EXTERNAL_IP
```

#### Task 7.2: Enable HTTPS with Managed Certificate (Optional)
- [ ] Create ManagedCertificate resource
- [ ] Update Ingress to use certificate
- [ ] Wait for certificate provisioning (15-60 min)

**Create file: `k8s/managed-cert.yaml`**
```yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: nlp-cert
spec:
  domains:
    - nlp.yourdomain.com
```

**Commands:**
```bash
# Apply certificate
kubectl apply -f k8s/managed-cert.yaml

# Check certificate status
kubectl describe managedcertificate nlp-cert
# Wait for Status: Active (can take 15-60 minutes)
```

---

### **PHASE 8: Testing and Validation** (Est. 1-2 hours)

#### Task 8.1: Test API Endpoints
- [ ] Test health endpoint
- [ ] Test predict endpoint
- [ ] Test model switching
- [ ] Test all 3 models

**Commands:**
```bash
# Get external IP
export EXTERNAL_IP=$(kubectl get ingress nlp-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health
curl http://$EXTERNAL_IP/api/health

# Test prediction
curl -X POST http://$EXTERNAL_IP/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message"}'

# Test model list
curl http://$EXTERNAL_IP/api/models

# Test model switching
curl -X POST http://$EXTERNAL_IP/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "logistic_regression"}'
```

#### Task 8.2: Test UI Access
- [ ] Access UI in browser
- [ ] Test all UI features
- [ ] Test model selection
- [ ] Test batch predictions

**Access:**
```
http://EXTERNAL_IP/
```

#### Task 8.3: Load Testing
- [ ] Run performance tests
- [ ] Verify autoscaling works
- [ ] Check resource utilization

**Create file: `scripts/load_test.sh`**
```bash
#!/bin/bash
# Simple load test
for i in {1..100}; do
  curl -X POST http://$EXTERNAL_IP/api/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "Test message '$i'"}' &
done
wait

# Watch autoscaling
kubectl get hpa -w
```

#### Task 8.4: Verify Persistent Storage
- [ ] Check model files are accessible
- [ ] Verify logs are being written
- [ ] Test pod restart (data persists)

**Commands:**
```bash
# Check models in pod
kubectl exec -it $(kubectl get pod -l app=nlp-api -o jsonpath='{.items[0].metadata.name}') \
  -- ls -la /app/models

# Check logs
kubectl exec -it $(kubectl get pod -l app=nlp-api -o jsonpath='{.items[0].metadata.name}') \
  -- ls -la /app/logs

# Restart pod and verify data persists
kubectl delete pod -l app=nlp-api
kubectl wait --for=condition=ready pod -l app=nlp-api --timeout=120s
```

---

### **PHASE 9: Monitoring and Logging** (Est. 1-2 hours)

#### Task 9.1: Set Up Cloud Monitoring
- [ ] Enable Cloud Monitoring
- [ ] Create custom dashboard
- [ ] Configure metrics collection

**Commands:**
```bash
# View metrics in Cloud Console
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"

# Create custom dashboard (via UI or API)
```

#### Task 9.2: Configure Logging
- [ ] Enable Cloud Logging
- [ ] Create log-based metrics
- [ ] Set up log exports (optional)

**Commands:**
```bash
# View logs
gcloud logging read "resource.type=k8s_container AND resource.labels.cluster_name=nlp-classifier-cluster" \
  --limit 50 \
  --format json

# Or use kubectl
kubectl logs -l app=nlp-api --tail=100 -f
```

#### Task 9.3: Set Up Alerts
- [ ] Create alert for high error rate
- [ ] Create alert for high latency
- [ ] Create alert for pod crashes
- [ ] Create alert for high costs

**Example Alert Policy (via gcloud):**
```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High API Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

---

### **PHASE 10: Security Hardening** (Est. 1-2 hours)

#### Task 10.1: Configure Network Policies
- [ ] Create network policies to restrict traffic
- [ ] Allow only necessary pod-to-pod communication

**Create file: `k8s/network-policy.yaml`**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nlp-api-netpol
spec:
  podSelector:
    matchLabels:
      app: nlp-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nlp-ui
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

#### Task 10.2: Enable Workload Identity
- [ ] Create service account
- [ ] Bind to Kubernetes service account
- [ ] Configure pods to use workload identity

#### Task 10.3: Configure IAM Roles
- [ ] Set up least-privilege IAM roles
- [ ] Create service accounts for different components
- [ ] Enable audit logging

#### Task 10.4: Enable Binary Authorization (Optional)
- [ ] Set up Binary Authorization policy
- [ ] Sign container images
- [ ] Enforce signed images only

---

### **PHASE 11: Cost Optimization** (Est. 1 hour)

#### Task 11.1: Right-Size Resources
- [ ] Analyze actual resource usage
- [ ] Adjust CPU/memory requests and limits
- [ ] Optimize replica counts

**Commands:**
```bash
# View resource usage
kubectl top pods
kubectl top nodes

# Adjust resources in deployment YAMLs based on actual usage
```

#### Task 11.2: Configure Cluster Autoscaler
- [ ] Verify cluster autoscaler is enabled
- [ ] Set appropriate min/max node counts
- [ ] Configure scale-down policies

#### Task 11.3: Use Preemptible Nodes (Optional)
- [ ] Create preemptible node pool
- [ ] Configure pod disruption budgets
- [ ] Test failover behavior

**Commands:**
```bash
# Add preemptible node pool
gcloud container node-pools create preemptible-pool \
  --cluster=nlp-classifier-cluster \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --preemptible \
  --num-nodes=1 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=3
```

#### Task 11.4: Set Up Budget Alerts
- [ ] Create budget alerts at $50, $100, $150
- [ ] Configure email notifications
- [ ] Review costs weekly

---

### **PHASE 12: CI/CD Setup** (Est. 2-3 hours, Optional)

#### Task 12.1: Set Up Cloud Build Triggers
- [ ] Connect GitHub/GitLab repository
- [ ] Create build trigger for main branch
- [ ] Configure automated testing

**Create file: `cloudbuild.yaml`**
```yaml
steps:
  # Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pytest tests/ -v

  # Build API image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:$SHORT_SHA'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:latest'
      - '-f'
      - 'Dockerfile'
      - '.'

  # Build UI image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:$SHORT_SHA'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:latest'
      - '-f'
      - 'Dockerfile.streamlit'
      - '.'

  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui']

  # Deploy to GKE
  - name: 'gcr.io/cloud-builders/kubectl'
    args:
      - 'set'
      - 'image'
      - 'deployment/nlp-api'
      - 'api=us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:$SHORT_SHA'
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'
      - 'CLOUDSDK_CONTAINER_CLUSTER=nlp-classifier-cluster'

  - name: 'gcr.io/cloud-builders/kubectl'
    args:
      - 'set'
      - 'image'
      - 'deployment/nlp-ui'
      - 'ui=us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:$SHORT_SHA'
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'
      - 'CLOUDSDK_CONTAINER_CLUSTER=nlp-classifier-cluster'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/api:$SHORT_SHA'
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/nlp-classifier/ui:$SHORT_SHA'

timeout: 1800s
```

#### Task 12.2: Set Up Staging Environment
- [ ] Create staging namespace
- [ ] Deploy to staging first
- [ ] Run integration tests
- [ ] Promote to production

---

### **PHASE 13: Documentation and Handoff** (Est. 2-3 hours)

#### Task 13.1: Document Deployment
- [ ] Create deployment runbook
- [ ] Document troubleshooting steps
- [ ] Create architecture diagram
- [ ] Document rollback procedures

#### Task 13.2: Create Operational Procedures
- [ ] Document scaling procedures
- [ ] Document update procedures
- [ ] Document backup/restore procedures
- [ ] Document incident response

#### Task 13.3: Train Team Members
- [ ] Conduct walkthrough of deployment
- [ ] Share access credentials
- [ ] Review monitoring dashboards
- [ ] Review alert procedures

---

## 📊 Cost Breakdown - GKE Deployment

### Monthly Cost Estimate

| Component | Specification | Monthly Cost |
|-----------|--------------|--------------|
| **GKE Cluster** | Management fee | $74.40 |
| **Compute Nodes** | 2x e2-standard-2 (2 vCPU, 8GB) | $48-60 |
| **Persistent Disk** | 25GB SSD (models + logs) | $4-5 |
| **Load Balancer** | External HTTP(S) LB | $18 |
| **External IP** | Static IP (reserved) | $7 |
| **Egress** | 10-50GB/month | $5-10 |
| **Artifact Registry** | Storage for images | $1-2 |
| **Cloud Logging** | Log storage | $2-5 |
| **Cloud Monitoring** | Metrics and dashboards | Free tier |
| **TOTAL** | | **$159-181/month** |

### Cost Optimization Options

1. **Use Autopilot GKE**: ~$100-120/month (simpler, but less control)
2. **Use Preemptible Nodes**: Save 60-80% on compute (~$70-100/month total)
3. **Scale to Zero**: Use min-instances=0 for HPA (save during idle)
4. **Use Spot VMs**: Save up to 91% on compute costs
5. **Regional vs Zonal**: Zonal cluster saves ~$30/month

### Cost Comparison

| Deployment Option | Monthly Cost | Best For |
|-------------------|--------------|----------|
| **GKE Standard** | $150-180 | Production, high availability |
| **GKE Autopilot** | $100-150 | Simpler management |
| **Cloud Run** | $15-50 | Low traffic, serverless |
| **Compute Engine** | $50-100 | Simple setup, predictable |

---

## 🚨 Risk Assessment

### High Risks
1. **Cost Overrun**: GKE cluster running 24/7
   - **Mitigation**: Set budget alerts, use autoscaling, monitor daily
   
2. **Model Size**: Large models (3-5GB) slow startup
   - **Mitigation**: Use persistent volumes, optimize model loading

3. **Cold Start**: Initial requests may be slow
   - **Mitigation**: Set min replicas to 2, use readiness probes

### Medium Risks
1. **Complexity**: Kubernetes has learning curve
   - **Mitigation**: Use provided YAML files, follow documentation

2. **Ingress Provisioning**: Can take 10-15 minutes
   - **Mitigation**: Be patient, check status regularly

3. **Certificate Provisioning**: HTTPS can take 15-60 minutes
   - **Mitigation**: Start with HTTP, add HTTPS later

### Low Risks
1. **Node Failures**: Nodes may crash
   - **Mitigation**: Use multiple replicas, enable auto-repair

2. **Storage Failures**: Persistent disks may fail
   - **Mitigation**: Use regional disks, backup models to GCS

---

## ✅ Success Criteria

### Deployment Success
- [ ] All pods are Running and Ready
- [ ] External IP is assigned and accessible
- [ ] API endpoints return 200 status
- [ ] UI loads in browser
- [ ] All 3 models are accessible
- [ ] Health checks are passing
- [ ] Autoscaling is working
- [ ] Logs are being collected
- [ ] Monitoring is active

### Performance Success
- [ ] API latency < 100ms (p50)
- [ ] API latency < 500ms (p99)
- [ ] UI load time < 2s
- [ ] Model switching < 5s
- [ ] Uptime > 99.5%

### Cost Success
- [ ] Monthly cost < $200
- [ ] Budget alerts configured
- [ ] Cost tracking enabled
- [ ] No unexpected charges

---

## 📚 Additional Resources

### GKE Documentation
- [GKE Quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstart)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Persistent Volumes](https://cloud.google.com/kubernetes-engine/docs/concepts/persistent-volumes)
- [Ingress for External HTTP(S) Load Balancing](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress)

### Kubernetes Documentation
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

### Cost Management
- [GKE Pricing](https://cloud.google.com/kubernetes-engine/pricing)
- [Cost Optimization Best Practices](https://cloud.google.com/architecture/best-practices-for-running-cost-effective-kubernetes-applications-on-gke)

---

## 🎯 Next Steps

1. **Review this plan** with your team
2. **Choose deployment option** (GKE recommended)
3. **Set up GCP project** and billing
4. **Start with Phase 1** (Pre-Deployment Setup)
5. **Follow phases sequentially**
6. **Test thoroughly** at each phase
7. **Monitor costs** daily for first week
8. **Optimize** based on actual usage

---

## 📞 Support and Troubleshooting

### Common Issues

**Issue: Pods stuck in Pending**
- Check: `kubectl describe pod POD_NAME`
- Solution: Increase node pool size or adjust resource requests

**Issue: Ingress not getting external IP**
- Check: `kubectl describe ingress nlp-ingress`
- Solution: Wait 10-15 minutes, check GCP quotas

**Issue: Models not loading**
- Check: `kubectl logs POD_NAME`
- Solution: Verify PVC is mounted, check model files exist

**Issue: High costs**
- Check: GCP billing dashboard
- Solution: Scale down replicas, use preemptible nodes

### Getting Help
- GCP Support: https://cloud.google.com/support
- Kubernetes Slack: https://kubernetes.slack.com
- Stack Overflow: Tag with `google-kubernetes-engine`

---

## 📝 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-10 | Initial deployment plan created |

---

**Document Status**: ✅ Ready for Review  
**Estimated Total Time**: 15-25 hours  
**Estimated Total Cost**: $150-180/month (GKE)  
**Recommended Start Date**: After plan review and approval

---

**END OF DEPLOYMENT PLAN**
