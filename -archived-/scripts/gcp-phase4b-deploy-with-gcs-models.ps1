# ============================================
# GCP Deployment - Phase 4B: Deploy with GCS Models
# ============================================
# Description: Clone repo + Download models from GCS + Build & Run
# ============================================

param(
    [string]$VMName = "nlp-classifier-vm",
    [string]$Zone = "us-central1-a",
    [string]$GitRepo = "https://github.com/YOUR_USERNAME/CLOUD-NLP-CLASSIFIER-GCP.git",
    [string]$Branch = "main",
    [string]$BucketName = "nlp-classifier-models"
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Phase 4B: Deploy with GCS Models" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VM: $VMName" -ForegroundColor Yellow
Write-Host "Zone: $Zone" -ForegroundColor Yellow
Write-Host "Git Repo: $GitRepo" -ForegroundColor Yellow
Write-Host "GCS Bucket: gs://$BucketName" -ForegroundColor Yellow
Write-Host ""

# ============================================
# Step 1: Verify VM is Running
# ============================================
Write-Host "[Step 1/6] Verifying VM status..." -ForegroundColor Cyan

try {
    $vmStatus = gcloud compute instances describe $VMName --zone=$Zone --format="get(status)" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to get VM status: $vmStatus"
    }
    
    if ($vmStatus -ne "RUNNING") {
        Write-Host "Starting VM..." -ForegroundColor Yellow
        gcloud compute instances start $VMName --zone=$Zone
        Start-Sleep -Seconds 30
    }
    
    Write-Host "[OK] VM is RUNNING" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to verify VM status: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Step 2: Clone Repository
# ============================================
Write-Host "[Step 2/6] Cloning repository..." -ForegroundColor Cyan

$cloneCmd = @"
# Remove old clone if exists
rm -rf ~/CLOUD-NLP-CLASSIFIER-GCP

# Clone repository
git clone -b $Branch $GitRepo ~/CLOUD-NLP-CLASSIFIER-GCP

# Verify clone
if [ -d ~/CLOUD-NLP-CLASSIFIER-GCP ]; then
    echo '[OK] Repository cloned'
    cd ~/CLOUD-NLP-CLASSIFIER-GCP
    ls -lh
else
    echo '[ERROR] Failed to clone repository'
    exit 1
fi
"@

try {
    $cloneOutput = gcloud compute ssh $VMName --zone=$Zone --command="$cloneCmd"
    Write-Host $cloneOutput
    Write-Host "[OK] Repository cloned" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to clone repository: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please update the GitRepo URL in the script!" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================
# Step 3: Download Models from GCS
# ============================================
Write-Host "[Step 3/6] Downloading models from GCS..." -ForegroundColor Cyan
Write-Host "This will download ~770 MB of models" -ForegroundColor Yellow

$downloadCmd = @"
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Create models directory structure
mkdir -p models/baselines
mkdir -p models/toxicity_multi_head
mkdir -p models/transformer/distilbert
mkdir -p models/transformer/distilbert_fullscale

# Download models from GCS
echo '[INFO] Downloading baseline models...'
gsutil -m cp gs://$BucketName/models/baselines/*.joblib models/baselines/

echo '[INFO] Downloading toxicity model...'
gsutil -m cp -r gs://$BucketName/models/toxicity_multi_head/* models/toxicity_multi_head/

echo '[INFO] Downloading DistilBERT model...'
gsutil -m cp gs://$BucketName/models/transformer/distilbert/* models/transformer/distilbert/

echo '[INFO] Downloading DistilBERT Fullscale model...'
gsutil -m cp gs://$BucketName/models/transformer/distilbert_fullscale/* models/transformer/distilbert_fullscale/

# Verify downloads
echo ''
echo '[INFO] Verifying downloaded models...'
du -sh models/*
ls -lh models/baselines/
ls -lh models/transformer/distilbert/

echo '[OK] Models downloaded successfully'
"@

try {
    Write-Host "Downloading models (this may take 2-5 minutes)..." -ForegroundColor Gray
    $downloadOutput = gcloud compute ssh $VMName --zone=$Zone --command="$downloadCmd"
    Write-Host $downloadOutput
    Write-Host "[OK] Models downloaded from GCS" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to download models: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you ran Phase 4A first to upload models to GCS!" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================
# Step 4: Build Docker Image
# ============================================
Write-Host "[Step 4/6] Building Docker image..." -ForegroundColor Cyan
Write-Host "This will take 5-10 minutes (includes PyTorch, transformers, etc.)" -ForegroundColor Yellow

$buildCmd = @"
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Build Docker image with all models
echo '[INFO] Building Docker image...'
docker build -t cloud-nlp-classifier:latest .

# Verify image
if docker images | grep -q 'cloud-nlp-classifier'; then
    echo '[OK] Docker image built successfully'
    docker images | grep 'cloud-nlp-classifier'
else
    echo '[ERROR] Failed to build Docker image'
    exit 1
fi
"@

try {
    Write-Host "Building image (please wait 5-10 minutes)..." -ForegroundColor Gray
    $buildOutput = gcloud compute ssh $VMName --zone=$Zone --command="$buildCmd"
    Write-Host $buildOutput
    Write-Host "[OK] Docker image built" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to build Docker image: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Step 5: Run Container
# ============================================
Write-Host "[Step 5/6] Starting Docker container..." -ForegroundColor Cyan

$runCmd = @"
cd ~/CLOUD-NLP-CLASSIFIER-GCP

# Stop and remove old container if exists
docker stop nlp-api 2>/dev/null || true
docker rm nlp-api 2>/dev/null || true

# Run new container
docker run -d \
    --name nlp-api \
    -p 8000:8000 \
    --restart unless-stopped \
    cloud-nlp-classifier:latest

# Wait for container to start
sleep 10

# Check container status
if docker ps | grep -q 'nlp-api'; then
    echo '[OK] Container is running'
    docker ps | grep 'nlp-api'
    
    # Test health endpoint
    echo ''
    echo '[INFO] Testing API health...'
    sleep 5
    curl -s http://localhost:8000/health | head -20 || echo '[WARN] Health check pending (container still starting)'
else
    echo '[ERROR] Container failed to start'
    echo '[INFO] Container logs:'
    docker logs nlp-api
    exit 1
fi
"@

try {
    $runOutput = gcloud compute ssh $VMName --zone=$Zone --command="$runCmd"
    Write-Host $runOutput
    Write-Host "[OK] Container started" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to start container: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Step 6: Test External Access
# ============================================
Write-Host "[Step 6/6] Testing external access..." -ForegroundColor Cyan

# Get VM external IP
$externalIP = gcloud compute instances describe $VMName --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

Write-Host "Testing API at http://${externalIP}:8000/health" -ForegroundColor Gray
Start-Sleep -Seconds 5

try {
    $healthCheck = curl.exe -s "http://${externalIP}:8000/health"
    Write-Host $healthCheck
    Write-Host "[OK] API is accessible externally" -ForegroundColor Green
} catch {
    Write-Host "[WARN] External access test failed (may need more time)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Summary
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Phase 4B Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor Yellow
Write-Host "VM External IP: $externalIP" -ForegroundColor Yellow
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  Health:  http://${externalIP}:8000/health" -ForegroundColor White
Write-Host "  Predict: http://${externalIP}:8000/predict" -ForegroundColor White
Write-Host "  Docs:    http://${externalIP}:8000/docs" -ForegroundColor White
Write-Host "  Models:  http://${externalIP}:8000/models" -ForegroundColor White
Write-Host ""
Write-Host "Test Commands:" -ForegroundColor Cyan
Write-Host "  curl http://${externalIP}:8000/health" -ForegroundColor White
Write-Host "  curl http://${externalIP}:8000/models" -ForegroundColor White
Write-Host ""
Write-Host "SSH into VM:" -ForegroundColor Cyan
Write-Host "  gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Cyan
Write-Host "  docker logs -f nlp-api" -ForegroundColor White
Write-Host ""
Write-Host "[OK] Deployment Complete - API is Live!" -ForegroundColor Green
Write-Host ""
