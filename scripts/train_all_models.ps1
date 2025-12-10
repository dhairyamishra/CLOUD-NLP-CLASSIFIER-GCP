# PowerShell Script: Full-Scale Model Training
# Trains all available models with comprehensive configurations and early stopping
# Compatible with Windows PowerShell 5.1+ and PowerShell Core 7+

param(
    [switch]$SkipConfirmation,
    [switch]$ContinueOnFailure,
    [string]$LogFile = "training_log.txt"
)

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput ("=" * 80) -Color Cyan
    Write-ColorOutput $Message -Color Cyan
    Write-ColorOutput ("=" * 80) -Color Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" -Color Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" -Color Red
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" -Color Yellow
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" -Color Blue
}

function Format-Duration {
    param([double]$Seconds)
    
    $hours = [Math]::Floor($Seconds / 3600)
    $minutes = [Math]::Floor(($Seconds % 3600) / 60)
    $secs = [Math]::Floor($Seconds % 60)
    
    if ($hours -gt 0) {
        return "${hours}h ${minutes}m ${secs}s"
    } elseif ($minutes -gt 0) {
        return "${minutes}m ${secs}s"
    } else {
        return "${secs}s"
    }
}

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $allGood = $true
    
    # Check data files
    Write-Info "Checking data files..."
    $dataFiles = @(
        "data\processed\train.csv",
        "data\processed\val.csv",
        "data\processed\test.csv"
    )
    
    foreach ($file in $dataFiles) {
        if (Test-Path $file) {
            Write-Success "Found: $file"
        } else {
            Write-ErrorMsg "Missing: $file"
            $allGood = $false
        }
    }
    
    # Check config files
    Write-Info "`nChecking configuration files..."
    $configFiles = @(
        "config\config_baselines.yaml",
        "config\config_transformer.yaml",
        "config\config_transformer_fullscale.yaml"
    )
    
    foreach ($config in $configFiles) {
        if (Test-Path $config) {
            Write-Success "Found: $config"
        } else {
            Write-ErrorMsg "Missing: $config"
            $allGood = $false
        }
    }
    
    if (-not $allGood) {
        Write-ErrorMsg "`nPrerequisites not met!"
        Write-Info "Please run preprocessing first: python run_preprocess.py"
        return $false
    }
    
    Write-Success "`n✓ All prerequisites met!"
    return $true
}

function Invoke-TrainingStep {
    param(
        [string]$Name,
        [string[]]$Command,
        [string]$Description
    )
    
    Write-Header "Training: $Name"
    Write-Info $Description
    Write-Info "Command: $($Command -join ' ')`n"
    
    $startTime = Get-Date
    
    try {
        # Run command with real-time output (no redirection)
        $process = Start-Process -FilePath $Command[0] -ArgumentList $Command[1..($Command.Length-1)] `
                                 -NoNewWindow -Wait -PassThru
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($process.ExitCode -eq 0) {
            Write-Success "`n✓ $Name completed successfully!"
            Write-Success "Duration: $(Format-Duration $duration)"
            return @{
                Name = $Name
                Status = "success"
                Duration = $duration
                Timestamp = $startTime.ToString("o")
            }
        } else {
            Write-ErrorMsg "`n✗ $Name failed with exit code $($process.ExitCode)"
            Write-ErrorMsg "Duration: $(Format-Duration $duration)"
            return @{
                Name = $Name
                Status = "failed"
                Duration = $duration
                ExitCode = $process.ExitCode
                Timestamp = $startTime.ToString("o")
            }
        }
    }
    catch {
        Write-ErrorMsg "`n✗ $Name failed with exception: $_"
        return @{
            Name = $Name
            Status = "error"
            Error = $_.Exception.Message
            Timestamp = (Get-Date).ToString("o")
        }
    }
}

function Save-TrainingReport {
    param(
        [array]$Results,
        [double]$TotalDuration
    )
    
    $report = @{
        training_session = @{
            start_time = $Results[0].Timestamp
            end_time = (Get-Date).ToString("o")
            total_duration_seconds = $TotalDuration
            total_duration_formatted = Format-Duration $TotalDuration
        }
        models_trained = $Results
        summary = @{
            total_models = $Results.Count
            successful = ($Results | Where-Object { $_.Status -eq "success" }).Count
            failed = ($Results | Where-Object { $_.Status -eq "failed" }).Count
            interrupted = ($Results | Where-Object { $_.Status -eq "interrupted" }).Count
        }
    }
    
    $reportPath = "training_report.json"
    $report | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8
    
    Write-Success "`nTraining report saved to: $reportPath"
    return $report
}

function Show-FinalSummary {
    param([hashtable]$Report)
    
    Write-Header "Training Session Summary"
    
    $summary = $Report.summary
    $session = $Report.training_session
    
    Write-Host "Total Duration: $($session.total_duration_formatted)" -ForegroundColor White
    Write-Host "Models Trained: $($summary.total_models)" -ForegroundColor White
    Write-ColorOutput "Successful: $($summary.successful)" -Color Green
    
    if ($summary.failed -gt 0) {
        Write-ColorOutput "Failed: $($summary.failed)" -Color Red
    }
    if ($summary.interrupted -gt 0) {
        Write-ColorOutput "Interrupted: $($summary.interrupted)" -Color Yellow
    }
    
    Write-Host "`nModel Results:" -ForegroundColor White
    foreach ($result in $Report.models_trained) {
        $icon = if ($result.Status -eq "success") { "✓" } else { "✗" }
        $color = if ($result.Status -eq "success") { "Green" } else { "Red" }
        $duration = if ($result.Duration) { Format-Duration $result.Duration } else { "N/A" }
        
        Write-ColorOutput "  $icon $($result.Name) - $duration" -Color $color
    }
    
    Write-Host "`nModel Locations:" -ForegroundColor White
    Write-Host "  • Baseline Models: models\baselines\"
    Write-Host "  • DistilBERT (Standard): models\transformer\distilbert\"
    Write-Host "  • DistilBERT (Full-Scale): models\transformer\distilbert_fullscale\"
    
    if ($summary.successful -eq $summary.total_models) {
        Write-Success "`n🎉 All models trained successfully!"
    } elseif ($summary.successful -gt 0) {
        Write-Warning "`n⚠ Partial success: $($summary.successful)/$($summary.total_models) models trained"
    } else {
        Write-ErrorMsg "`n❌ Training failed for all models"
    }
}

# Main execution
function Main {
    Write-Header "FULL-SCALE MODEL TRAINING PIPELINE"
    Write-Info "This script will train all available models with comprehensive configurations."
    Write-Info "Training includes early stopping, detailed logging, and performance tracking.`n"
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-ErrorMsg "`nPrerequisites not met. Exiting."
        exit 1
    }
    
    # Define training steps
    $trainingSteps = @(
        @{
            Name = "Baseline Models (Logistic Regression + Linear SVM)"
            Command = @("python", "-m", "src.models.train_baselines")
            Description = "Training classical ML models with TF-IDF features (10k features, n-grams 1-3)"
        },
        @{
            Name = "DistilBERT Transformer (Standard Configuration)"
            Command = @("python", "-m", "src.models.transformer_training", "--config", "config\config_transformer.yaml")
            Description = "Training DistilBERT with 256 seq length, 15 epochs, early stopping (patience=5)"
        },
        @{
            Name = "DistilBERT Transformer (Intensive Full-Scale)"
            Command = @("python", "-m", "src.models.transformer_training", "--config", "config\config_transformer_fullscale.yaml")
            Description = "Training DistilBERT with 512 seq length, 25 epochs, early stopping (patience=8)"
        }
    )
    
    # Ask for confirmation
    if (-not $SkipConfirmation) {
        Write-Warning "`nThis will train 3 models sequentially. Estimated time: 2-6 hours (GPU) or 12-24 hours (CPU)"
        Write-Info "You can interrupt training at any time with Ctrl+C`n"
        
        $response = Read-Host "Do you want to proceed? (yes/no)"
        if ($response -notmatch "^(yes|y)$") {
            Write-Info "Training cancelled by user."
            exit 0
        }
    }
    
    # Run training steps
    $results = @()
    $overallStartTime = Get-Date
    
    for ($i = 0; $i -lt $trainingSteps.Count; $i++) {
        $step = $trainingSteps[$i]
        Write-Host "`n[$($i+1)/$($trainingSteps.Count)]" -ForegroundColor White
        
        $result = Invoke-TrainingStep -Name $step.Name -Command $step.Command -Description $step.Description
        $results += $result
        
        # Stop if interrupted
        if ($result.Status -eq "interrupted") {
            Write-Warning "`nTraining interrupted by user. Saving partial results..."
            break
        }
        
        # Optional: Stop on failure
        if ((-not $ContinueOnFailure) -and ($result.Status -eq "failed")) {
            Write-ErrorMsg "`nStopping due to failure. Use -ContinueOnFailure to continue on errors."
            break
        }
        
        # Brief pause between models
        if ($i -lt ($trainingSteps.Count - 1)) {
            Write-Info "`nPreparing next model... (pausing for 5 seconds)"
            Start-Sleep -Seconds 5
        }
    }
    
    $overallEndTime = Get-Date
    $totalDuration = ($overallEndTime - $overallStartTime).TotalSeconds
    
    # Save and display report
    $report = Save-TrainingReport -Results $results -TotalDuration $totalDuration
    Show-FinalSummary -Report $report
    
    # Return appropriate exit code
    if ($report.summary.successful -eq $report.summary.total_models) {
        exit 0
    } elseif ($report.summary.successful -gt 0) {
        exit 2  # Partial success
    } else {
        exit 1  # Complete failure
    }
}

# Run main function
try {
    Main
}
catch {
    Write-ErrorMsg "`nUnexpected error: $_"
    Write-Host $_.ScriptStackTrace
    exit 1
}
