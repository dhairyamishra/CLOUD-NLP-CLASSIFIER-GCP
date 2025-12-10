# Docker API Testing Script
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "Docker API Comprehensive Testing" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "   Status: $($response.status)" -ForegroundColor Green
    Write-Host "   Current Model: $($response.current_model)" -ForegroundColor Green
    Write-Host "   Available Models: $($response.available_models -join ', ')" -ForegroundColor Green
    Write-Host "   Classes: $($response.num_classes)" -ForegroundColor Green
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 2: Root Endpoint
Write-Host "`n2. Testing Root Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   Version: $($response.version)" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Green
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 3: Prediction with DistilBERT
Write-Host "`n3. Testing Prediction (DistilBERT)..." -ForegroundColor Yellow
try {
    $body = @{
        text = "I love this product, it is amazing!"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/predict" -Method Post -ContentType "application/json" -Body $body
    Write-Host "   Text: 'I love this product, it is amazing!'" -ForegroundColor Green
    Write-Host "   Predicted Label: $($response.predicted_label)" -ForegroundColor Green
    Write-Host "   Confidence: $([math]::Round($response.confidence * 100, 2))%" -ForegroundColor Green
    Write-Host "   Inference Time: $([math]::Round($response.inference_time_ms, 2))ms" -ForegroundColor Green
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 4: List Models
Write-Host "`n4. Testing List Models..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/models" -Method Get
    Write-Host "   Current Model: $($response.current_model)" -ForegroundColor Green
    Write-Host "   Available Models: $($response.available_models.Count)" -ForegroundColor Green
    foreach ($model in $response.available_models) {
        Write-Host "     - $model" -ForegroundColor Cyan
    }
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 5: Negative Sentiment
Write-Host "`n5. Testing Negative Sentiment..." -ForegroundColor Yellow
try {
    $body = @{
        text = "This is terrible and offensive content that should be flagged"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/predict" -Method Post -ContentType "application/json" -Body $body
    Write-Host "   Predicted Label: $($response.predicted_label)" -ForegroundColor Green
    Write-Host "   Confidence: $([math]::Round($response.confidence * 100, 2))%" -ForegroundColor Green
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 6: Neutral Text
Write-Host "`n6. Testing Neutral Text..." -ForegroundColor Yellow
try {
    $body = @{
        text = "The weather is nice today"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/predict" -Method Post -ContentType "application/json" -Body $body
    Write-Host "   Predicted Label: $($response.predicted_label)" -ForegroundColor Green
    Write-Host "   Confidence: $([math]::Round($response.confidence * 100, 2))%" -ForegroundColor Green
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 7: Performance Test (10 requests)
Write-Host "`n7. Testing Performance (10 requests)..." -ForegroundColor Yellow
try {
    $times = @()
    $body = @{
        text = "Quick performance test"
    } | ConvertTo-Json
    
    for ($i = 1; $i -le 10; $i++) {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri "$baseUrl/predict" -Method Post -ContentType "application/json" -Body $body
        $end = Get-Date
        $elapsed = ($end - $start).TotalMilliseconds
        $times += $elapsed
    }
    
    $avgTime = ($times | Measure-Object -Average).Average
    $minTime = ($times | Measure-Object -Minimum).Minimum
    $maxTime = ($times | Measure-Object -Maximum).Maximum
    
    Write-Host "   Average Time: $([math]::Round($avgTime, 2))ms" -ForegroundColor Green
    Write-Host "   Min Time: $([math]::Round($minTime, 2))ms" -ForegroundColor Green
    Write-Host "   Max Time: $([math]::Round($maxTime, 2))ms" -ForegroundColor Green
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 8: Container Logs Check
Write-Host "`n8. Checking Container Logs..." -ForegroundColor Yellow
try {
    $logs = docker logs nlp-api --tail 5 2>&1
    Write-Host "   Last 5 log lines:" -ForegroundColor Cyan
    $logs | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "Total Tests: $($testsPassed + $testsFailed)" -ForegroundColor White
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`n✅ ALL TESTS PASSED! Docker deployment is working perfectly!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some tests failed. Please review the errors above." -ForegroundColor Yellow
}

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "  1. View interactive docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  2. View container logs: docker-compose logs -f api" -ForegroundColor White
Write-Host "  3. Stop containers: docker-compose down" -ForegroundColor White
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
