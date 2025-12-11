# Phase 1: GCP Project Setup Script
# Project: mnist-k8s-pipeline
# Deployment: VM + Docker Compose

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 1: GCP Project Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "mnist-k8s-pipeline"
$REGION = "us-central1"
$ZONE = "us-central1-a"

Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host "Zone: $ZONE" -ForegroundColor Green
Write-Host ""

# Step 1: Set default project
Write-Host "[1/5] Setting default project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to set project" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Project set successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Set default region and zone
Write-Host "[2/5] Setting default region and zone..." -ForegroundColor Yellow
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE
Write-Host "OK - Region and zone set successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Enable Compute Engine API
Write-Host "[3/5] Enabling Compute Engine API..." -ForegroundColor Yellow
Write-Host "This may take 1-2 minutes..." -ForegroundColor Gray
gcloud services enable compute.googleapis.com
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to enable Compute Engine API" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Compute Engine API enabled" -ForegroundColor Green
Write-Host ""

# Step 4: Reserve static external IP
Write-Host "[4/5] Reserving static external IP address..." -ForegroundColor Yellow
Write-Host "This will cost about 7 dollars per month" -ForegroundColor Gray

$existingIP = gcloud compute addresses describe nlp-classifier-ip --region=$REGION 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "WARNING - Static IP already exists" -ForegroundColor Yellow
    $STATIC_IP = gcloud compute addresses describe nlp-classifier-ip --region=$REGION --format="get(address)"
    Write-Host "Using existing IP: $STATIC_IP" -ForegroundColor Cyan
}
else {
    gcloud compute addresses create nlp-classifier-ip --region=$REGION
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create static IP" -ForegroundColor Red
        exit 1
    }
    $STATIC_IP = gcloud compute addresses describe nlp-classifier-ip --region=$REGION --format="get(address)"
    Write-Host "OK - Static IP created: $STATIC_IP" -ForegroundColor Green
}
Write-Host ""

# Step 5: Display summary
Write-Host "[5/5] Phase 1 Setup Summary" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project ID:        $PROJECT_ID" -ForegroundColor Green
Write-Host "Region:            $REGION" -ForegroundColor Green
Write-Host "Zone:              $ZONE" -ForegroundColor Green
Write-Host "Static IP:         $STATIC_IP" -ForegroundColor Green
Write-Host "Compute API:       Enabled" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Save configuration to file
$configFile = "gcp-deployment-config.txt"
$configContent = @"
PROJECT_ID=$PROJECT_ID
REGION=$REGION
ZONE=$ZONE
STATIC_IP=$STATIC_IP
VM_NAME=nlp-classifier-vm
MACHINE_TYPE=e2-standard-2
BOOT_DISK_SIZE=50GB
"@

$configContent | Out-File -FilePath $configFile -Encoding UTF8
Write-Host "OK - Configuration saved to: $configFile" -ForegroundColor Green
Write-Host ""

# Display next steps
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 1 COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Static IP Address: $STATIC_IP" -ForegroundColor Cyan
Write-Host "Save this IP - you will use it to access your application!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review the configuration above" -ForegroundColor White
Write-Host "  2. Confirm everything looks correct" -ForegroundColor White
Write-Host "  3. Proceed to Phase 2: Create VM" -ForegroundColor White
Write-Host ""
Write-Host "Estimated Monthly Cost:" -ForegroundColor Yellow
Write-Host "  - VM (e2-standard-2):  50 dollars per month" -ForegroundColor White
Write-Host "  - 50GB SSD Disk:       8 dollars per month" -ForegroundColor White
Write-Host "  - Static IP:           7 dollars per month" -ForegroundColor White
Write-Host "  - Total:               65-75 dollars per month" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to proceed to Phase 2?" -ForegroundColor Yellow
