# ============================================================================
# Docker API Testing Script
# ============================================================================
# Quick script to test the containerized API endpoints
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Dockerized NLP Classifier API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check Endpoint" -ForegroundColor Yellow
Write-Host "GET http://localhost:8000/health" -ForegroundColor Gray
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ Health check passed!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Gray
    $health | ConvertTo-Json -Depth 10
    Write-Host ""
} catch {
    Write-Host "❌ Health check failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

# Test 2: Root Endpoint
Write-Host "Test 2: Root Endpoint" -ForegroundColor Yellow
Write-Host "GET http://localhost:8000/" -ForegroundColor Gray
try {
    $root = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "✅ Root endpoint passed!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Gray
    $root | ConvertTo-Json -Depth 10
    Write-Host ""
} catch {
    Write-Host "❌ Root endpoint failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

# Test 3: Prediction - Positive Text
Write-Host "Test 3: Prediction Endpoint - Positive Text" -ForegroundColor Yellow
Write-Host "POST http://localhost:8000/predict" -ForegroundColor Gray
$body1 = @{
    text = "I love this product! It's amazing and works perfectly!"
} | ConvertTo-Json

try {
    $pred1 = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body1 -ContentType "application/json"
    Write-Host "✅ Prediction successful!" -ForegroundColor Green
    Write-Host "Input: 'I love this product! It's amazing and works perfectly!'" -ForegroundColor Gray
    Write-Host "Response:" -ForegroundColor Gray
    $pred1 | ConvertTo-Json -Depth 10
    Write-Host ""
} catch {
    Write-Host "❌ Prediction failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

# Test 4: Prediction - Negative Text
Write-Host "Test 4: Prediction Endpoint - Negative Text" -ForegroundColor Yellow
Write-Host "POST http://localhost:8000/predict" -ForegroundColor Gray
$body2 = @{
    text = "This is terrible and offensive content that should be flagged."
} | ConvertTo-Json

try {
    $pred2 = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body2 -ContentType "application/json"
    Write-Host "✅ Prediction successful!" -ForegroundColor Green
    Write-Host "Input: 'This is terrible and offensive content that should be flagged.'" -ForegroundColor Gray
    Write-Host "Response:" -ForegroundColor Gray
    $pred2 | ConvertTo-Json -Depth 10
    Write-Host ""
} catch {
    Write-Host "❌ Prediction failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

# Test 5: Prediction - Neutral Text
Write-Host "Test 5: Prediction Endpoint - Neutral Text" -ForegroundColor Yellow
Write-Host "POST http://localhost:8000/predict" -ForegroundColor Gray
$body3 = @{
    text = "The weather today is cloudy with a chance of rain."
} | ConvertTo-Json

try {
    $pred3 = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body3 -ContentType "application/json"
    Write-Host "✅ Prediction successful!" -ForegroundColor Green
    Write-Host "Input: 'The weather today is cloudy with a chance of rain.'" -ForegroundColor Gray
    Write-Host "Response:" -ForegroundColor Gray
    $pred3 | ConvertTo-Json -Depth 10
    Write-Host ""
} catch {
    Write-Host "❌ Prediction failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:8000/docs in your browser for interactive API docs" -ForegroundColor Gray
Write-Host "2. View container logs: docker logs -f nlp-api" -ForegroundColor Gray
Write-Host "3. Check resource usage: docker stats nlp-api" -ForegroundColor Gray
Write-Host "4. Stop container: docker stop nlp-api" -ForegroundColor Gray
Write-Host ""
