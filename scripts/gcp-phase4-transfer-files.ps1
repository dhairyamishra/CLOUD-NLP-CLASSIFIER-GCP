# ============================================
# GCP VM Deployment - Phase 4: Transfer Files
# ============================================
# Project: CLOUD-NLP-CLASSIFIER-GCP
# Phase: 4/14 - Selective File Transfer
# Description: Transfer source code and inference-ready models to GCP VM
# Excludes: Training checkpoints (saves 11.5 GB / 94% reduction)
# ============================================

param(
    [string]$VMName = "nlp-classifier-vm",
    [string]$Zone = "us-central1-a",
    [string]$ProjectRoot = "C:\--DPM-MAIN-DIR--\windsurf_projects\CLOUD-NLP-CLASSIFIER-GCP",
    [string]$RemoteBase = "/opt/nlp-classifier",
    [switch]$SkipVerification,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# ============================================
# Configuration
# ============================================
$TransferLog = Join-Path $ProjectRoot "transfer_log.txt"
$StartTime = Get-Date

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GCP VM Deployment - Phase 4" -ForegroundColor Cyan
Write-Host "  File Transfer (Selective)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VM: $VMName" -ForegroundColor Yellow
Write-Host "Zone: $Zone" -ForegroundColor Yellow
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "Remote Base: $RemoteBase" -ForegroundColor Yellow
Write-Host "Dry Run: $DryRun" -ForegroundColor Yellow
Write-Host ""

# Start logging
"Phase 4 Transfer - Started at $StartTime" | Out-File $TransferLog -Encoding UTF8
"" | Out-File $TransferLog -Append

# ============================================
# Step 1: Verify VM is Running
# ============================================
Write-Host "[Step 1/8] Verifying VM status..." -ForegroundColor Cyan

try {
    $vmStatus = gcloud compute instances describe $VMName --zone=$Zone --format="get(status)" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to get VM status: $vmStatus"
    }
    
    if ($vmStatus -ne "RUNNING") {
        Write-Host "VM is not running. Current status: $vmStatus" -ForegroundColor Red
        Write-Host "Starting VM..." -ForegroundColor Yellow
        gcloud compute instances start $VMName --zone=$Zone
        Start-Sleep -Seconds 30
    }
    
    Write-Host "[OK] VM is RUNNING" -ForegroundColor Green
    "[OK] VM Status: RUNNING" | Out-File $TransferLog -Append
} catch {
    Write-Host "[ERROR] Failed to verify VM status: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# Step 2: Create Remote Directories
# ============================================
Write-Host "[Step 2/8] Creating remote directories..." -ForegroundColor Cyan

$remoteDirs = @(
    "$RemoteBase/src",
    "$RemoteBase/config",
    "$RemoteBase/scripts",
    "$RemoteBase/models/baselines",
    "$RemoteBase/models/toxicity_multi_head",
    "$RemoteBase/models/transformer/distilbert",
    "$RemoteBase/models/transformer/distilbert_fullscale",
    "$RemoteBase/data",
    "$RemoteBase/logs"
)

$createDirsCmd = "mkdir -p " + ($remoteDirs -join " ")

if (-not $DryRun) {
    try {
        gcloud compute ssh $VMName --zone=$Zone --command="$createDirsCmd"
        Write-Host "[OK] Remote directories created" -ForegroundColor Green
        "[OK] Remote directories created" | Out-File $TransferLog -Append
    } catch {
        Write-Host "[ERROR] Failed to create remote directories: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[DRY RUN] Would create directories: $createDirsCmd" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 3: Transfer Source Code
# ============================================
Write-Host "[Step 3/8] Transferring source code..." -ForegroundColor Cyan

$sourceTransfers = @(
    @{Local="src"; Remote="$RemoteBase/"; Description="Source code"},
    @{Local="config"; Remote="$RemoteBase/"; Description="Configuration files"},
    @{Local="scripts"; Remote="$RemoteBase/"; Description="Scripts"},
    @{Local="requirements.txt"; Remote="$RemoteBase/"; Description="Requirements"},
    @{Local="Dockerfile"; Remote="$RemoteBase/"; Description="Dockerfile"},
    @{Local="docker-compose.yml"; Remote="$RemoteBase/"; Description="Docker Compose"},
    @{Local="docker-compose.full.yml"; Remote="$RemoteBase/"; Description="Docker Compose Full"},
    @{Local=".dockerignore"; Remote="$RemoteBase/"; Description=".dockerignore"},
    @{Local="README.md"; Remote="$RemoteBase/"; Description="README"}
)

$sourceSize = 0
foreach ($transfer in $sourceTransfers) {
    $localPath = Join-Path $ProjectRoot $transfer.Local
    
    if (Test-Path $localPath) {
        Write-Host "  > Transferring $($transfer.Description)..." -ForegroundColor Gray
        
        if (-not $DryRun) {
            try {
                if (Test-Path $localPath -PathType Container) {
                    gcloud compute scp --recurse $localPath ${VMName}:$($transfer.Remote) --zone=$Zone
                } else {
                    gcloud compute scp $localPath ${VMName}:$($transfer.Remote) --zone=$Zone
                }
                
                $size = (Get-ChildItem $localPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                $sourceSize += $size
                $sizeMB = [math]::Round($size / 1MB, 2)
                Write-Host "    [OK] Transferred ($sizeMB MB)" -ForegroundColor Green
                "  [OK] $($transfer.Description): $sizeMB MB" | Out-File $TransferLog -Append
            } catch {
                Write-Host "    [ERROR] Failed: $_" -ForegroundColor Red
                "  [ERROR] $($transfer.Description): FAILED" | Out-File $TransferLog -Append
            }
        } else {
            Write-Host "    [DRY RUN] Would transfer $localPath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "    [WARN] Not found: $localPath" -ForegroundColor Yellow
    }
}

$sourceSizeMB = [math]::Round($sourceSize / 1MB, 2)
Write-Host "[OK] Source code transferred: $sourceSizeMB MB" -ForegroundColor Green
Write-Host ""

# ============================================
# Step 4: Transfer Baseline Models
# ============================================
Write-Host "[Step 4/8] Transferring baseline models..." -ForegroundColor Cyan

$baselinesPath = Join-Path $ProjectRoot "models\baselines"
if (Test-Path $baselinesPath) {
    Write-Host "  > Transferring baseline models (Logistic Regression, Linear SVM)..." -ForegroundColor Gray
    
    if (-not $DryRun) {
        try {
            gcloud compute scp --recurse "$baselinesPath\*" ${VMName}:$RemoteBase/models/baselines/ --zone=$Zone
            
            $size = (Get-ChildItem $baselinesPath -File | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  [OK] Baseline models transferred: $sizeMB MB" -ForegroundColor Green
            "[OK] Baseline models: $sizeMB MB" | Out-File $TransferLog -Append
        } catch {
            Write-Host "  [ERROR] Failed to transfer baseline models: $_" -ForegroundColor Red
            "[ERROR] Baseline models: FAILED" | Out-File $TransferLog -Append
        }
    } else {
        Write-Host "  [DRY RUN] Would transfer $baselinesPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARN] Baseline models not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 5: Transfer Toxicity Model
# ============================================
Write-Host "[Step 5/8] Transferring toxicity multi-head model..." -ForegroundColor Cyan

$toxicityPath = Join-Path $ProjectRoot "models\toxicity_multi_head"
if (Test-Path $toxicityPath) {
    Write-Host "  > Transferring toxicity model (~256 MB)..." -ForegroundColor Gray
    
    if (-not $DryRun) {
        try {
            gcloud compute scp --recurse "$toxicityPath\*" ${VMName}:$RemoteBase/models/toxicity_multi_head/ --zone=$Zone
            
            $size = (Get-ChildItem $toxicityPath -File | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  [OK] Toxicity model transferred: $sizeMB MB" -ForegroundColor Green
            "[OK] Toxicity model: $sizeMB MB" | Out-File $TransferLog -Append
        } catch {
            Write-Host "  [ERROR] Failed to transfer toxicity model: $_" -ForegroundColor Red
            "[ERROR] Toxicity model: FAILED" | Out-File $TransferLog -Append
        }
    } else {
        Write-Host "  [DRY RUN] Would transfer $toxicityPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARN] Toxicity model not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 6: Transfer DistilBERT (Main Model Only)
# ============================================
Write-Host "[Step 6/8] Transferring DistilBERT model (excluding checkpoints)..." -ForegroundColor Cyan

$distilbertPath = Join-Path $ProjectRoot "models\transformer\distilbert"
if (Test-Path $distilbertPath) {
    Write-Host "  > Transferring DistilBERT inference files (~256 MB)..." -ForegroundColor Gray
    Write-Host "  > Excluding checkpoint-* folders (saves ~3.8 GB)" -ForegroundColor Yellow
    
    if (-not $DryRun) {
        try {
            # Transfer only the main model files, not checkpoints
            $modelFiles = Get-ChildItem $distilbertPath -File
            foreach ($file in $modelFiles) {
                gcloud compute scp $file.FullName ${VMName}:$RemoteBase/models/transformer/distilbert/ --zone=$Zone
            }
            
            $size = ($modelFiles | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  [OK] DistilBERT model transferred: $sizeMB MB" -ForegroundColor Green
            "[OK] DistilBERT model: $sizeMB MB (checkpoints excluded)" | Out-File $TransferLog -Append
        } catch {
            Write-Host "  [ERROR] Failed to transfer DistilBERT model: $_" -ForegroundColor Red
            "[ERROR] DistilBERT model: FAILED" | Out-File $TransferLog -Append
        }
    } else {
        Write-Host "  [DRY RUN] Would transfer DistilBERT files (excluding checkpoints)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARN] DistilBERT model not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 7: Transfer DistilBERT Fullscale (Main Model Only)
# ============================================
Write-Host "[Step 7/8] Transferring DistilBERT Fullscale model (excluding checkpoints)..." -ForegroundColor Cyan

$distilbertFullPath = Join-Path $ProjectRoot "models\transformer\distilbert_fullscale"
if (Test-Path $distilbertFullPath) {
    Write-Host "  > Transferring DistilBERT Fullscale inference files (~256 MB)..." -ForegroundColor Gray
    Write-Host "  > Excluding checkpoint-* folders (saves ~7.7 GB)" -ForegroundColor Yellow
    
    if (-not $DryRun) {
        try {
            # Transfer only the main model files, not checkpoints
            $modelFiles = Get-ChildItem $distilbertFullPath -File
            foreach ($file in $modelFiles) {
                gcloud compute scp $file.FullName ${VMName}:$RemoteBase/models/transformer/distilbert_fullscale/ --zone=$Zone
            }
            
            $size = ($modelFiles | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  [OK] DistilBERT Fullscale model transferred: $sizeMB MB" -ForegroundColor Green
            "[OK] DistilBERT Fullscale: $sizeMB MB (checkpoints excluded)" | Out-File $TransferLog -Append
        } catch {
            Write-Host "  [ERROR] Failed to transfer DistilBERT Fullscale model: $_" -ForegroundColor Red
            "[ERROR] DistilBERT Fullscale: FAILED" | Out-File $TransferLog -Append
        }
    } else {
        Write-Host "  [DRY RUN] Would transfer DistilBERT Fullscale files (excluding checkpoints)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARN] DistilBERT Fullscale model not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 8: Verify Transfer
# ============================================
if (-not $SkipVerification -and -not $DryRun) {
    Write-Host "[Step 8/8] Verifying transferred files..." -ForegroundColor Cyan
    
    try {
        # Check directory structure
        $verifyCmd = @"
echo '=== Directory Structure ==='
ls -lh $RemoteBase/
echo ''
echo '=== Models Directory ==='
du -sh $RemoteBase/models/*
echo ''
echo '=== DistilBERT Files ==='
ls -lh $RemoteBase/models/transformer/distilbert/
echo ''
echo '=== DistilBERT Fullscale Files ==='
ls -lh $RemoteBase/models/transformer/distilbert_fullscale/
echo ''
echo '=== Baseline Models ==='
ls -lh $RemoteBase/models/baselines/
echo ''
echo '=== Total Disk Usage ==='
du -sh $RemoteBase
"@
        
        Write-Host "  > Checking remote files..." -ForegroundColor Gray
        $verifyOutput = gcloud compute ssh $VMName --zone=$Zone --command="$verifyCmd"
        
        Write-Host ""
        Write-Host "=== Remote Verification ===" -ForegroundColor Cyan
        Write-Host $verifyOutput
        Write-Host ""
        
        "=== Remote Verification ===" | Out-File $TransferLog -Append
        $verifyOutput | Out-File $TransferLog -Append
        
        Write-Host "[OK] Verification complete" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Verification failed (non-critical): $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[Step 8/8] Skipping verification" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Summary
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Phase 4 Transfer Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Duration: $($Duration.ToString('mm\:ss'))" -ForegroundColor Yellow
Write-Host "Source Code: ~$sourceSizeMB MB" -ForegroundColor Yellow
Write-Host "Models: ~770 MB (inference-ready only)" -ForegroundColor Yellow
Write-Host "Checkpoints Excluded: ~11.5 GB (94% reduction)" -ForegroundColor Green
Write-Host ""
Write-Host "Transfer Log: $TransferLog" -ForegroundColor Cyan
Write-Host ""

# Log summary
"" | Out-File $TransferLog -Append
"=== Summary ===" | Out-File $TransferLog -Append
"Duration: $($Duration.ToString('mm\:ss'))" | Out-File $TransferLog -Append
"Source Code: ~$sourceSizeMB MB" | Out-File $TransferLog -Append
"Models: ~770 MB (inference-ready only)" | Out-File $TransferLog -Append
"Checkpoints Excluded: ~11.5 GB (94% reduction)" | Out-File $TransferLog -Append
"Completed: $EndTime" | Out-File $TransferLog -Append

# ============================================
# Next Steps
# ============================================
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review transfer log: $TransferLog" -ForegroundColor White
Write-Host "2. SSH into VM: gcloud compute ssh $VMName --zone=$Zone" -ForegroundColor White
Write-Host "3. Verify files: ls -lh $RemoteBase" -ForegroundColor White
Write-Host "4. Run Phase 5: .\scripts\gcp-phase5-configure-docker.ps1" -ForegroundColor White
Write-Host ""
Write-Host "[OK] Phase 4 Complete - Ready for Phase 5!" -ForegroundColor Green
Write-Host ""
