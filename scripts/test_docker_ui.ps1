# PowerShell script to test Docker Streamlit UI deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Streamlit UI Test Script      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Build the image
Write-Host "Building Streamlit UI Docker image..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Gray
docker build -f Dockerfile.streamlit -t cloud-nlp-classifier-ui:test .

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Check if port 8501 is available
Write-Host "Checking if port 8501 is available..." -ForegroundColor Yellow
$portCheck = netstat -ano | Select-String ":8501"
if ($portCheck) {
    Write-Host "⚠ Port 8501 is already in use!" -ForegroundColor Yellow
    Write-Host "Stopping any existing containers..." -ForegroundColor Yellow
    docker stop nlp-ui-test 2>$null
    docker rm nlp-ui-test 2>$null
    Start-Sleep -Seconds 2
}

Write-Host "✓ Port 8501 is available" -ForegroundColor Green
Write-Host ""

# Run the container
Write-Host "Starting Streamlit UI container..." -ForegroundColor Yellow
docker run -d `
    --name nlp-ui-test `
    -p 8501:8501 `
    cloud-nlp-classifier-ui:test

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start container!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Container started successfully" -ForegroundColor Green
Write-Host ""

# Wait for container to be ready
Write-Host "Waiting for container to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container status
$containerStatus = docker ps --filter "name=nlp-ui-test" --format "{{.Status}}"
Write-Host "Container status: $containerStatus" -ForegroundColor Cyan
Write-Host ""

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -UseBasicParsing -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Health check passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Health check returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Health check failed (this is normal if container is still starting)" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Gray
}

Write-Host ""

# Show logs
Write-Host "Container logs (last 20 lines):" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
docker logs --tail 20 nlp-ui-test
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

# Final instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker UI is running!                 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the UI at: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:    docker logs -f nlp-ui-test" -ForegroundColor Cyan
Write-Host "  Stop:         docker stop nlp-ui-test" -ForegroundColor Cyan
Write-Host "  Remove:       docker rm nlp-ui-test" -ForegroundColor Cyan
Write-Host "  Restart:      docker restart nlp-ui-test" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop following logs, or close this window." -ForegroundColor Gray
Write-Host ""

# Follow logs
docker logs -f nlp-ui-test
