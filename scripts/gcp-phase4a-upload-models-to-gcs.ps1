# ============================================
# GCP Deployment - Phase 4A: Upload Models to GCS
# ============================================
# Description: Upload trained models to Google Cloud Storage
# This is a ONE-TIME setup - models persist in GCS
# ============================================

param(
    [string]$ProjectId = "mnist-k8s-pipeline",
    [string]$BucketName = "nlp-classifier-models",
    [string]$Region = "us-central1",
    [string]$ModelsPath = "C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP\models"
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Phase 4A: Upload Models to GCS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "Bucket: $BucketName" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "Models Path: $ModelsPath" -ForegroundColor Yellow
Write-Host ""

# ============================================
# Step 1: Create GCS Bucket
# ============================================
Write-Host "[Step 1/3] Creating GCS bucket..." -ForegroundColor Cyan

try {
    # Check if bucket exists
    $bucketExists = gsutil ls -b gs://$BucketName 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating new bucket: $BucketName" -ForegroundColor Yellow
        gsutil mb -p $ProjectId -c STANDARD -l $Region gs://$BucketName
        Write-Host "[OK] Bucket created" -ForegroundColor Green
    } else {
        Write-Host "[OK] Bucket already exists" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to create bucket: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Step 2: Upload Models (Selective)
# ============================================
Write-Host "[Step 2/3] Uploading models to GCS..." -ForegroundColor Cyan
Write-Host "This will upload ONLY inference-ready models (no checkpoints)" -ForegroundColor Yellow
Write-Host ""

# Upload baseline models
Write-Host "  > Uploading baseline models..." -ForegroundColor Gray
try {
    gsutil -m cp -r "$ModelsPath\baselines\*.joblib" gs://$BucketName/models/baselines/
    Write-Host "  [OK] Baseline models uploaded" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Baseline models upload had issues" -ForegroundColor Yellow
}

# Upload toxicity model
Write-Host "  > Uploading toxicity model..." -ForegroundColor Gray
try {
    gsutil -m cp -r "$ModelsPath\toxicity_multi_head\*" gs://$BucketName/models/toxicity_multi_head/
    Write-Host "  [OK] Toxicity model uploaded" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Toxicity model upload had issues" -ForegroundColor Yellow
}

# Upload DistilBERT (main files only, no checkpoints)
Write-Host "  > Uploading DistilBERT model (excluding checkpoints)..." -ForegroundColor Gray
try {
    Get-ChildItem "$ModelsPath\transformer\distilbert" -File | ForEach-Object {
        gsutil cp $_.FullName gs://$BucketName/models/transformer/distilbert/
    }
    Write-Host "  [OK] DistilBERT uploaded" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] DistilBERT upload had issues" -ForegroundColor Yellow
}

# Upload DistilBERT Fullscale (main files only, no checkpoints)
Write-Host "  > Uploading DistilBERT Fullscale (excluding checkpoints)..." -ForegroundColor Gray
try {
    Get-ChildItem "$ModelsPath\transformer\distilbert_fullscale" -File | ForEach-Object {
        gsutil cp $_.FullName gs://$BucketName/models/transformer/distilbert_fullscale/
    }
    Write-Host "  [OK] DistilBERT Fullscale uploaded" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] DistilBERT Fullscale upload had issues" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 3: Verify Upload
# ============================================
Write-Host "[Step 3/3] Verifying uploaded files..." -ForegroundColor Cyan

try {
    $bucketContents = gsutil ls -lh gs://$BucketName/models/**
    Write-Host $bucketContents
    Write-Host ""
    Write-Host "[OK] Models uploaded successfully" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not verify upload" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Summary
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Phase 4A Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor Yellow
Write-Host "Bucket: gs://$BucketName" -ForegroundColor Yellow
Write-Host ""
Write-Host "Models Location:" -ForegroundColor Cyan
Write-Host "  gs://$BucketName/models/baselines/" -ForegroundColor White
Write-Host "  gs://$BucketName/models/toxicity_multi_head/" -ForegroundColor White
Write-Host "  gs://$BucketName/models/transformer/distilbert/" -ForegroundColor White
Write-Host "  gs://$BucketName/models/transformer/distilbert_fullscale/" -ForegroundColor White
Write-Host ""
Write-Host "Next Step:" -ForegroundColor Cyan
Write-Host "  Run Phase 4B to deploy on VM with models from GCS" -ForegroundColor White
Write-Host "  .\scripts\gcp-phase4b-deploy-with-gcs-models.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] Models are now in cloud storage!" -ForegroundColor Green
Write-Host ""
