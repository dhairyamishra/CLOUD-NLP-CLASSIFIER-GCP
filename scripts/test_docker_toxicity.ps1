# ============================================================================
# Test Docker Build with Toxicity Model
# ============================================================================
# This script tests the Docker build and deployment with the toxicity model
# ============================================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Docker Build Test - Toxicity Model Support" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$IMAGE_NAME = "cloud-nlp-classifier:toxicity"
$CONTAINER_NAME = "nlp-api-toxicity-test"
$PORT = 8000

# Step 1: Clean up any existing containers
Write-Host "[1/6] Cleaning up existing containers..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null
docker rm $CONTAINER_NAME 2>$null
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Step 2: Build Docker image
Write-Host "[2/6] Building Docker image..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Gray
$buildStart = Get-Date
docker build -t $IMAGE_NAME .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    exit 1
}
$buildEnd = Get-Date
$buildDuration = ($buildEnd - $buildStart).TotalSeconds
Write-Host "✓ Build complete in $([math]::Round($buildDuration, 2)) seconds" -ForegroundColor Green
Write-Host ""

# Step 3: Check image size
Write-Host "[3/6] Checking image size..." -ForegroundColor Yellow
$imageInfo = docker images $IMAGE_NAME --format "{{.Size}}"
Write-Host "Image size: $imageInfo" -ForegroundColor Cyan
Write-Host ""

# Step 4: Start container
Write-Host "[4/6] Starting container..." -ForegroundColor Yellow
docker run -d -p ${PORT}:8000 --name $CONTAINER_NAME $IMAGE_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start container!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Container started" -ForegroundColor Green
Write-Host ""

# Step 5: Wait for container to be ready
Write-Host "[5/6] Waiting for API to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    Start-Sleep -Seconds 2
    $attempt++
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:${PORT}/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
            Write-Host "✓ API is ready after $($attempt * 2) seconds" -ForegroundColor Green
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if (-not $ready) {
    Write-Host ""
    Write-Host "✗ API failed to start within timeout" -ForegroundColor Red
    Write-Host "Container logs:" -ForegroundColor Yellow
    docker logs $CONTAINER_NAME
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    exit 1
}
Write-Host ""

# Step 6: Test all models
Write-Host "[6/6] Testing all models..." -ForegroundColor Yellow
Write-Host ""

# Test 1: Check available models
Write-Host "Test 1: Checking available models..." -ForegroundColor Cyan
try {
    $modelsResponse = Invoke-RestMethod -Uri "http://localhost:${PORT}/models" -Method Get
    $availableModels = $modelsResponse.available_models
    
    Write-Host "Available models:" -ForegroundColor White
    foreach ($model in $availableModels) {
        Write-Host "  - $model" -ForegroundColor Gray
    }
    
    # Check if toxicity model is available
    if ($availableModels -contains "toxicity") {
        Write-Host "✓ Toxicity model is available" -ForegroundColor Green
    } else {
        Write-Host "✗ Toxicity model NOT found!" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Failed to get models list: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Test toxicity model prediction
Write-Host "Test 2: Testing toxicity model prediction..." -ForegroundColor Cyan
try {
    # Switch to toxicity model
    $switchBody = @{
        model_name = "toxicity"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:${PORT}/models/switch" -Method Post -Body $switchBody -ContentType "application/json" | Out-Null
    
    # Make prediction
    $testText = "This is a test message for toxicity detection"
    $predictBody = @{
        text = $testText
    } | ConvertTo-Json
    
    $prediction = Invoke-RestMethod -Uri "http://localhost:${PORT}/predict" -Method Post -Body $predictBody -ContentType "application/json"
    
    Write-Host "Input: $testText" -ForegroundColor White
    Write-Host "Model used: $($prediction.model_name)" -ForegroundColor White
    Write-Host "Is toxic: $($prediction.is_toxic)" -ForegroundColor White
    Write-Host "Inference time: $($prediction.inference_time_ms) ms" -ForegroundColor White
    Write-Host "✓ Toxicity model prediction successful" -ForegroundColor Green
} catch {
    Write-Host "✗ Toxicity model prediction failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Test DistilBERT model
Write-Host "Test 3: Testing DistilBERT model..." -ForegroundColor Cyan
try {
    # Switch to distilbert model
    $switchBody = @{
        model_name = "distilbert"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:${PORT}/models/switch" -Method Post -Body $switchBody -ContentType "application/json" | Out-Null
    
    # Make prediction
    $testText = "I love this product!"
    $predictBody = @{
        text = $testText
    } | ConvertTo-Json
    
    $prediction = Invoke-RestMethod -Uri "http://localhost:${PORT}/predict" -Method Post -Body $predictBody -ContentType "application/json"
    
    Write-Host "Input: $testText" -ForegroundColor White
    Write-Host "Model used: $($prediction.model_name)" -ForegroundColor White
    Write-Host "Predicted label: $($prediction.predicted_label)" -ForegroundColor White
    Write-Host "Confidence: $([math]::Round($prediction.confidence * 100, 2))%" -ForegroundColor White
    Write-Host "Inference time: $($prediction.inference_time_ms) ms" -ForegroundColor White
    Write-Host "✓ DistilBERT model prediction successful" -ForegroundColor Green
} catch {
    Write-Host "✗ DistilBERT model prediction failed: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Image: $IMAGE_NAME" -ForegroundColor White
Write-Host "Container: $CONTAINER_NAME" -ForegroundColor White
Write-Host "Port: $PORT" -ForegroundColor White
Write-Host "Build time: $([math]::Round($buildDuration, 2)) seconds" -ForegroundColor White
Write-Host "Image size: $imageInfo" -ForegroundColor White
Write-Host ""
Write-Host "Container is running. Access the API at:" -ForegroundColor Yellow
Write-Host "  - API: http://localhost:${PORT}" -ForegroundColor Cyan
Write-Host "  - Health: http://localhost:${PORT}/health" -ForegroundColor Cyan
Write-Host "  - Docs: http://localhost:${PORT}/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop and remove the container:" -ForegroundColor Yellow
Write-Host "  docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME" -ForegroundColor Gray
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  docker logs -f $CONTAINER_NAME" -ForegroundColor Gray
Write-Host ""
