# Phase 10: Cleanup & Verification Script
# Final cleanup and verification of all testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Phase 10: Cleanup & Verification     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$START_TIME = Get-Date
$VERIFICATION_RESULTS = @{}

# ============================================
# Step 1: Stop and Remove Test Containers
# ============================================
Write-Host "[STEP 1] Cleaning up Docker containers..." -ForegroundColor Cyan

$testContainers = @(
    "nlp-api-test-default",
    "nlp-api-test-logreg",
    "nlp-api-test-svm",
    "nlp-api-test-switching",
    "nlp-api-perf-test",
    "nlp-api"
)

$stoppedCount = 0
$removedCount = 0

foreach ($container in $testContainers) {
    $exists = docker ps -a --filter "name=$container" --format "{{.Names}}" 2>$null
    if ($exists) {
        Write-Host "  Stopping container: $container" -ForegroundColor Gray
        docker stop $container 2>$null | Out-Null
        $stoppedCount++
        
        Write-Host "  Removing container: $container" -ForegroundColor Gray
        docker rm $container 2>$null | Out-Null
        $removedCount++
    }
}

Write-Host "[OK] Containers cleaned up: $stoppedCount stopped, $removedCount removed" -ForegroundColor Green
$VERIFICATION_RESULTS["ContainersCleanedUp"] = @{
    Stopped = $stoppedCount
    Removed = $removedCount
}

# ============================================
# Step 2: Verify Model Files
# ============================================
Write-Host "`n[STEP 2] Verifying model files..." -ForegroundColor Cyan

$modelFiles = @{
    "DistilBERT Model" = "models\transformer\distilbert\pytorch_model.bin"
    "DistilBERT Config" = "models\transformer\distilbert\config.json"
    "DistilBERT Tokenizer" = "models\transformer\distilbert\tokenizer_config.json"
    "DistilBERT Labels" = "models\transformer\distilbert\label_mappings.json"
    "Logistic Regression" = "models\baselines\logistic_regression_pipeline.pkl"
    "Linear SVM" = "models\baselines\linear_svm_pipeline.pkl"
}

$modelVerification = @{
    Found = 0
    Missing = 0
    TotalSize = 0
}

foreach ($modelName in $modelFiles.Keys) {
    $path = $modelFiles[$modelName]
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        $sizeFormatted = if ($size -gt 1MB) { 
            "$([math]::Round($size / 1MB, 2)) MB" 
        } else { 
            "$([math]::Round($size / 1KB, 2)) KB" 
        }
        Write-Host "  [OK] $modelName : $sizeFormatted" -ForegroundColor Green
        $modelVerification.Found++
        $modelVerification.TotalSize += $size
    } else {
        Write-Host "  [MISSING] $modelName" -ForegroundColor Red
        $modelVerification.Missing++
    }
}

$totalSizeMB = [math]::Round($modelVerification.TotalSize / 1MB, 2)
Write-Host "[OK] Model verification: $($modelVerification.Found) found, $($modelVerification.Missing) missing" -ForegroundColor Green
Write-Host "     Total model size: $totalSizeMB MB" -ForegroundColor Gray

$VERIFICATION_RESULTS["ModelFiles"] = $modelVerification

# ============================================
# Step 3: Verify Data Files
# ============================================
Write-Host "`n[STEP 3] Verifying data files..." -ForegroundColor Cyan

$dataFiles = @{
    "Raw Dataset" = "data\raw\dataset.csv"
    "Train Split" = "data\processed\train.csv"
    "Validation Split" = "data\processed\val.csv"
    "Test Split" = "data\processed\test.csv"
}

$dataVerification = @{
    Found = 0
    Missing = 0
}

foreach ($dataName in $dataFiles.Keys) {
    $path = $dataFiles[$dataName]
    if (Test-Path $path) {
        $lines = (Get-Content $path | Measure-Object -Line).Lines
        Write-Host "  [OK] $dataName : $lines lines" -ForegroundColor Green
        $dataVerification.Found++
    } else {
        Write-Host "  [MISSING] $dataName" -ForegroundColor Red
        $dataVerification.Missing++
    }
}

Write-Host "[OK] Data verification: $($dataVerification.Found) found, $($dataVerification.Missing) missing" -ForegroundColor Green
$VERIFICATION_RESULTS["DataFiles"] = $dataVerification

# ============================================
# Step 4: Verify Docker Image
# ============================================
Write-Host "`n[STEP 4] Verifying Docker image..." -ForegroundColor Cyan

$imageName = "cloud-nlp-classifier:latest"
$imageExists = docker images --filter "reference=$imageName" --format "{{.Repository}}:{{.Tag}}" 2>$null

if ($imageExists) {
    $imageSize = docker images --filter "reference=$imageName" --format "{{.Size}}" 2>$null
    Write-Host "  [OK] Image found: $imageName" -ForegroundColor Green
    Write-Host "       Size: $imageSize" -ForegroundColor Gray
    $VERIFICATION_RESULTS["DockerImage"] = @{
        Exists = $true
        Size = $imageSize
    }
} else {
    Write-Host "  [MISSING] Image not found: $imageName" -ForegroundColor Red
    $VERIFICATION_RESULTS["DockerImage"] = @{
        Exists = $false
    }
}

# ============================================
# Step 5: Check Docker Resources
# ============================================
Write-Host "`n[STEP 5] Docker resource summary..." -ForegroundColor Cyan

$runningContainers = (docker ps --format "{{.Names}}" 2>$null | Measure-Object -Line).Lines
$allContainers = (docker ps -a --format "{{.Names}}" 2>$null | Measure-Object -Line).Lines
$images = (docker images --format "{{.Repository}}" 2>$null | Measure-Object -Line).Lines

Write-Host "  Running containers: $runningContainers" -ForegroundColor Gray
Write-Host "  Total containers: $allContainers" -ForegroundColor Gray
Write-Host "  Total images: $images" -ForegroundColor Gray

$VERIFICATION_RESULTS["DockerResources"] = @{
    RunningContainers = $runningContainers
    TotalContainers = $allContainers
    TotalImages = $images
}

# ============================================
# Step 6: Verify Test Results
# ============================================
Write-Host "`n[STEP 6] Verifying test results..." -ForegroundColor Cyan

$testResultFiles = @{
    "Performance Results" = "performance_results.json"
    "Progress Tracker" = "END_TO_END_TEST_PROGRESS.md"
    "Test Results" = "END_TO_END_TEST_RESULTS.md"
}

$testVerification = @{
    Found = 0
    Missing = 0
}

foreach ($testName in $testResultFiles.Keys) {
    $path = $testResultFiles[$testName]
    if (Test-Path $path) {
        Write-Host "  [OK] $testName" -ForegroundColor Green
        $testVerification.Found++
    } else {
        Write-Host "  [MISSING] $testName" -ForegroundColor Red
        $testVerification.Missing++
    }
}

$VERIFICATION_RESULTS["TestResults"] = $testVerification

# ============================================
# Step 7: Generate Summary Statistics
# ============================================
Write-Host "`n[STEP 7] Generating summary statistics..." -ForegroundColor Cyan

# Count documentation files
$docFiles = Get-ChildItem -Path "docs" -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object
$scriptFiles = Get-ChildItem -Path "scripts" -Filter "*.ps1" -ErrorAction SilentlyContinue | Measure-Object
$testFiles = Get-ChildItem -Path "tests" -Filter "*.py" -ErrorAction SilentlyContinue | Measure-Object

Write-Host "  Documentation files: $($docFiles.Count)" -ForegroundColor Gray
Write-Host "  Script files: $($scriptFiles.Count)" -ForegroundColor Gray
Write-Host "  Test files: $($testFiles.Count)" -ForegroundColor Gray

$VERIFICATION_RESULTS["ProjectFiles"] = @{
    Documentation = $docFiles.Count
    Scripts = $scriptFiles.Count
    Tests = $testFiles.Count
}

# ============================================
# Final Summary
# ============================================
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Phase 10: Cleanup & Verification Summary" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n[SUMMARY] Cleanup Results:" -ForegroundColor Cyan
Write-Host "  Containers stopped: $($VERIFICATION_RESULTS.ContainersCleanedUp.Stopped)" -ForegroundColor Gray
Write-Host "  Containers removed: $($VERIFICATION_RESULTS.ContainersCleanedUp.Removed)" -ForegroundColor Gray

Write-Host "`n[SUMMARY] Model Verification:" -ForegroundColor Cyan
Write-Host "  Models found: $($VERIFICATION_RESULTS.ModelFiles.Found)/6" -ForegroundColor Gray
Write-Host "  Total size: $totalSizeMB MB" -ForegroundColor Gray
if ($VERIFICATION_RESULTS.ModelFiles.Missing -eq 0) {
    Write-Host "  Status: [OK] All models present" -ForegroundColor Green
} else {
    Write-Host "  Status: [WARNING] Some models missing" -ForegroundColor Yellow
}

Write-Host "`n[SUMMARY] Data Verification:" -ForegroundColor Cyan
Write-Host "  Data files found: $($VERIFICATION_RESULTS.DataFiles.Found)/4" -ForegroundColor Gray
if ($VERIFICATION_RESULTS.DataFiles.Missing -eq 0) {
    Write-Host "  Status: [OK] All data files present" -ForegroundColor Green
} else {
    Write-Host "  Status: [WARNING] Some data files missing" -ForegroundColor Yellow
}

Write-Host "`n[SUMMARY] Docker Status:" -ForegroundColor Cyan
Write-Host "  Image exists: $($VERIFICATION_RESULTS.DockerImage.Exists)" -ForegroundColor Gray
if ($VERIFICATION_RESULTS.DockerImage.Exists) {
    Write-Host "  Image size: $($VERIFICATION_RESULTS.DockerImage.Size)" -ForegroundColor Gray
}
Write-Host "  Running containers: $($VERIFICATION_RESULTS.DockerResources.RunningContainers)" -ForegroundColor Gray

Write-Host "`n[SUMMARY] Project Statistics:" -ForegroundColor Cyan
Write-Host "  Documentation: $($VERIFICATION_RESULTS.ProjectFiles.Documentation) files" -ForegroundColor Gray
Write-Host "  Scripts: $($VERIFICATION_RESULTS.ProjectFiles.Scripts) files" -ForegroundColor Gray
Write-Host "  Tests: $($VERIFICATION_RESULTS.ProjectFiles.Tests) files" -ForegroundColor Gray

$DURATION = ((Get-Date) - $START_TIME).TotalSeconds
Write-Host "`n[INFO] Cleanup duration: $([math]::Round($DURATION, 2)) seconds" -ForegroundColor Cyan

# Save verification results
$resultsJson = $VERIFICATION_RESULTS | ConvertTo-Json -Depth 10
$resultsJson | Out-File -FilePath "cleanup_verification_results.json" -Encoding UTF8
Write-Host "[INFO] Results saved to cleanup_verification_results.json" -ForegroundColor Cyan

# Final status
Write-Host "`n" + "="*60 -ForegroundColor Cyan
$allChecks = ($VERIFICATION_RESULTS.ModelFiles.Missing -eq 0) -and 
             ($VERIFICATION_RESULTS.DataFiles.Missing -eq 0) -and
             ($VERIFICATION_RESULTS.DockerImage.Exists)

if ($allChecks) {
    Write-Host "[SUCCESS] Phase 10: All verifications passed!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Phase 10: Some verifications failed" -ForegroundColor Yellow
}
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n[OK] Phase 10 complete!" -ForegroundColor Green
Write-Host "Review the results and update END_TO_END_TEST_PROGRESS.md" -ForegroundColor Yellow
