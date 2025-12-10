# ============================================================================
# Docker Compose Startup Script - UI + API
# ============================================================================
# This script builds and starts both the Streamlit UI and FastAPI backend
# using Docker Compose with the toxicity model support.
# ============================================================================

param(
    [switch]$Build,
    [switch]$Rebuild,
    [switch]$Down,
    [switch]$Logs,
    [string]$Service = ""
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Cloud NLP Classifier - Docker Compose Manager" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$COMPOSE_FILE = "docker-compose.yml"
$PROJECT_NAME = "cloud-nlp-classifier"

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    } catch {
        Write-Host "✗ Docker is not running!" -ForegroundColor Red
        Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
        return $false
    }
}

# Function to check if docker-compose is available
function Test-DockerCompose {
    try {
        docker-compose --version | Out-Null
        return $true
    } catch {
        Write-Host "✗ docker-compose is not installed!" -ForegroundColor Red
        Write-Host "Please install docker-compose and try again." -ForegroundColor Yellow
        return $false
    }
}

# Check prerequisites
if (-not (Test-DockerRunning)) {
    exit 1
}

if (-not (Test-DockerCompose)) {
    exit 1
}

# Handle different commands
if ($Down) {
    Write-Host "Stopping and removing containers..." -ForegroundColor Yellow
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    Write-Host "✓ Containers stopped and removed" -ForegroundColor Green
    exit 0
}

if ($Logs) {
    if ($Service) {
        Write-Host "Following logs for service: $Service" -ForegroundColor Yellow
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f $Service
    } else {
        Write-Host "Following logs for all services..." -ForegroundColor Yellow
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    }
    exit 0
}

# Build images
if ($Build -or $Rebuild) {
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    Write-Host ""
    
    if ($Rebuild) {
        Write-Host "Performing clean rebuild (no cache)..." -ForegroundColor Gray
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build --no-cache
    } else {
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Build complete" -ForegroundColor Green
    Write-Host ""
}

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start services!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

# Wait for services to be healthy
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Services are running!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the applications at:" -ForegroundColor Yellow
Write-Host "  📊 Streamlit UI:  http://localhost:8501" -ForegroundColor Cyan
Write-Host "  🚀 FastAPI:       http://localhost:8000" -ForegroundColor Cyan
Write-Host "  📖 API Docs:      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ❤️  Health Check:  http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available Models:" -ForegroundColor Yellow
Write-Host "  1. DistilBERT (Transformer) - Best accuracy" -ForegroundColor White
Write-Host "  2. Toxicity Classifier - Multi-label toxicity detection" -ForegroundColor White
Write-Host "  3. Logistic Regression - Fast inference" -ForegroundColor White
Write-Host "  4. Linear SVM - Ultra-fast inference" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  View logs (all):     docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f" -ForegroundColor Gray
Write-Host "  View logs (API):     docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f api" -ForegroundColor Gray
Write-Host "  View logs (UI):      docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f ui" -ForegroundColor Gray
Write-Host "  Stop services:       docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down" -ForegroundColor Gray
Write-Host "  Restart services:    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart" -ForegroundColor Gray
Write-Host ""
Write-Host "Or use this script:" -ForegroundColor Yellow
Write-Host "  .\scripts\docker-compose-up.ps1 -Logs          # View all logs" -ForegroundColor Gray
Write-Host "  .\scripts\docker-compose-up.ps1 -Logs -Service api   # View API logs" -ForegroundColor Gray
Write-Host "  .\scripts\docker-compose-up.ps1 -Down          # Stop all services" -ForegroundColor Gray
Write-Host "  .\scripts\docker-compose-up.ps1 -Build         # Rebuild and start" -ForegroundColor Gray
Write-Host "  .\scripts\docker-compose-up.ps1 -Rebuild       # Clean rebuild (no cache)" -ForegroundColor Gray
Write-Host ""
