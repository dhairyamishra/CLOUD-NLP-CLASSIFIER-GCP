# PowerShell script to run all Phase 3 tests

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 3 Testing Suite" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Test 1: Model Loading
Write-Host "Running Test 1: Model Loading..." -ForegroundColor Yellow
python tests\test_model_loading.py
if ($LASTEXITCODE -ne 0) {
    $allPassed = $false
    Write-Host "❌ Model loading test failed" -ForegroundColor Red
} else {
    Write-Host "✅ Model loading test passed" -ForegroundColor Green
}
Write-Host ""

# Test 2: Inference
Write-Host "Running Test 2: Inference..." -ForegroundColor Yellow
python tests\test_inference.py
if ($LASTEXITCODE -ne 0) {
    $allPassed = $false
    Write-Host "❌ Inference test failed" -ForegroundColor Red
} else {
    Write-Host "✅ Inference test passed" -ForegroundColor Green
}
Write-Host ""

# Test 3: Metrics Validation
Write-Host "Running Test 3: Metrics Validation..." -ForegroundColor Yellow
python tests\test_metrics.py
if ($LASTEXITCODE -ne 0) {
    $allPassed = $false
    Write-Host "❌ Metrics validation failed" -ForegroundColor Red
} else {
    Write-Host "✅ Metrics validation passed" -ForegroundColor Green
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "✅ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Phase 3 is working correctly!" -ForegroundColor Green
} else {
    Write-Host "❌ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "Please check the output above for details" -ForegroundColor Red
}
Write-Host "==========================================" -ForegroundColor Cyan
