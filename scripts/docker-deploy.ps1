#!/usr/bin/env pwsh
# ============================================================================
# Docker Deployment Script with Multiple Options
# ============================================================================
# Automated deployment script for Cloud NLP Classifier with various configurations
#
# Usage:
#   .\scripts\docker-deploy.ps1 -Mode full
#   .\scripts\docker-deploy.ps1 -Mode api-only
#   .\scripts\docker-deploy.ps1 -Mode ui-only
#   .\scripts\docker-deploy.ps1 -Mode stop
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("full", "api-only", "ui-only", "stop", "restart", "logs", "status")]
    [string]$Mode = "full",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("distilbert", "logistic_regression", "linear_svm")]
    [string]$DefaultModel = "distilbert",
    
    [Parameter(Mandatory=$false)]
    [switch]$Build,
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow
)

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "============================================================================" "Cyan"
    Write-ColorOutput "  $Title" "Cyan"
    Write-ColorOutput "============================================================================" "Cyan"
    Write-Host ""
}

function Show-Menu {
    Write-Header "Cloud NLP Classifier - Docker Deployment"
    
    Write-ColorOutput "Available Modes:" "Yellow"
    Write-Host "  1. full        - Deploy API + UI (Recommended)"
    Write-Host "  2. api-only    - Deploy API only"
    Write-Host "  3. ui-only     - Deploy UI only (requires API running)"
    Write-Host "  4. stop        - Stop all containers"
    Write-Host "  5. restart     - Restart all containers"
    Write-Host "  6. logs        - View container logs"
    Write-Host "  7. status      - Check container status"
    Write-Host ""
    
    Write-ColorOutput "Options:" "Yellow"
    Write-Host "  -DefaultModel  - Choose model: distilbert, logistic_regression, linear_svm"
    Write-Host "  -Build         - Force rebuild images"
    Write-Host "  -Follow        - Follow logs in real-time"
    Write-Host ""
    
    Write-ColorOutput "Examples:" "Green"
    Write-Host "  .\scripts\docker-deploy.ps1 -Mode full"
    Write-Host "  .\scripts\docker-deploy.ps1 -Mode full -DefaultModel logistic_regression"
    Write-Host "  .\scripts\docker-deploy.ps1 -Mode full -Build"
    Write-Host "  .\scripts\docker-deploy.ps1 -Mode logs -Follow"
    Write-Host ""
}

# Main execution
Write-Header "Cloud NLP Classifier - Docker Deployment"

switch ($Mode) {
    "full" {
        Write-ColorOutput "🚀 Deploying Full Stack (API + UI)..." "Green"
        Write-Host ""
        
        # Set environment variable for default model
        $env:DEFAULT_MODEL = $DefaultModel
        Write-ColorOutput "   Default Model: $DefaultModel" "Cyan"
        
        # Build flag
        $buildFlag = if ($Build) { "--build" } else { "" }
        
        # Deploy
        Write-ColorOutput "   Starting containers..." "Yellow"
        if ($Build) {
            docker-compose -f docker-compose.full.yml up -d --build
        } else {
            docker-compose -f docker-compose.full.yml up -d
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColorOutput "✅ Deployment successful!" "Green"
            Write-Host ""
            Write-ColorOutput "Services:" "Yellow"
            Write-Host "  • API:        http://localhost:8000"
            Write-Host "  • API Docs:   http://localhost:8000/docs"
            Write-Host "  • UI:         http://localhost:8501"
            Write-Host ""
            Write-ColorOutput "Commands:" "Yellow"
            Write-Host "  • View logs:  docker-compose -f docker-compose.full.yml logs -f"
            Write-Host "  • Stop:       .\scripts\docker-deploy.ps1 -Mode stop"
            Write-Host "  • Status:     .\scripts\docker-deploy.ps1 -Mode status"
            Write-Host ""
            
            # Open browser
            Write-ColorOutput "Opening UI in browser..." "Cyan"
            Start-Sleep -Seconds 5
            Start-Process "http://localhost:8501"
        } else {
            Write-ColorOutput "❌ Deployment failed!" "Red"
            exit 1
        }
    }
    
    "api-only" {
        Write-ColorOutput "🚀 Deploying API Only..." "Green"
        Write-Host ""
        
        $env:DEFAULT_MODEL = $DefaultModel
        Write-ColorOutput "   Default Model: $DefaultModel" "Cyan"
        
        if ($Build) {
            docker-compose -f docker-compose.api-only.yml up -d --build
        } else {
            docker-compose -f docker-compose.api-only.yml up -d
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColorOutput "✅ API deployed successfully!" "Green"
            Write-Host ""
            Write-ColorOutput "Services:" "Yellow"
            Write-Host "  • API:        http://localhost:8000"
            Write-Host "  • API Docs:   http://localhost:8000/docs"
            Write-Host ""
            
            Start-Sleep -Seconds 3
            Start-Process "http://localhost:8000/docs"
        } else {
            Write-ColorOutput "❌ Deployment failed!" "Red"
            exit 1
        }
    }
    
    "ui-only" {
        Write-ColorOutput "🚀 Deploying UI Only..." "Green"
        Write-Host ""
        
        if ($Build) {
            docker-compose -f docker-compose.ui.yml up -d --build
        } else {
            docker-compose -f docker-compose.ui.yml up -d
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-ColorOutput "✅ UI deployed successfully!" "Green"
            Write-Host ""
            Write-ColorOutput "Services:" "Yellow"
            Write-Host "  • UI:         http://localhost:8501"
            Write-Host ""
            Write-ColorOutput "⚠️  Note: Ensure API is running on port 8000" "Yellow"
            Write-Host ""
            
            Start-Sleep -Seconds 3
            Start-Process "http://localhost:8501"
        } else {
            Write-ColorOutput "❌ Deployment failed!" "Red"
            exit 1
        }
    }
    
    "stop" {
        Write-ColorOutput "🛑 Stopping all containers..." "Yellow"
        Write-Host ""
        
        docker-compose -f docker-compose.full.yml down
        docker-compose -f docker-compose.api-only.yml down 2>$null
        docker-compose -f docker-compose.ui.yml down 2>$null
        
        Write-Host ""
        Write-ColorOutput "✅ All containers stopped!" "Green"
    }
    
    "restart" {
        Write-ColorOutput "🔄 Restarting containers..." "Yellow"
        Write-Host ""
        
        docker-compose -f docker-compose.full.yml restart
        
        Write-Host ""
        Write-ColorOutput "✅ Containers restarted!" "Green"
    }
    
    "logs" {
        Write-ColorOutput "📋 Viewing logs..." "Cyan"
        Write-Host ""
        
        if ($Follow) {
            docker-compose -f docker-compose.full.yml logs -f
        } else {
            docker-compose -f docker-compose.full.yml logs --tail=50
        }
    }
    
    "status" {
        Write-ColorOutput "📊 Container Status:" "Cyan"
        Write-Host ""
        
        docker-compose -f docker-compose.full.yml ps
        
        Write-Host ""
        Write-ColorOutput "Health Status:" "Yellow"
        
        # Check API health
        try {
            $apiHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2
            Write-ColorOutput "  ✅ API: Healthy" "Green"
            Write-Host "     Current Model: $($apiHealth.current_model)"
            Write-Host "     Available Models: $($apiHealth.available_models -join ', ')"
        } catch {
            Write-ColorOutput "  ❌ API: Not responding" "Red"
        }
        
        # Check UI health
        try {
            $uiHealth = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -TimeoutSec 2
            if ($uiHealth.StatusCode -eq 200) {
                Write-ColorOutput "  ✅ UI: Healthy" "Green"
            }
        } catch {
            Write-ColorOutput "  ❌ UI: Not responding" "Red"
        }
        
        Write-Host ""
    }
    
    default {
        Show-Menu
    }
}

Write-Host ""
