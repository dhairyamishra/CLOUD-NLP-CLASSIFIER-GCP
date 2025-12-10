#!/usr/bin/env python3
"""
Master Training Script - Train All Models Sequentially
Runs comprehensive training for all available models with detailed logging and early stopping.

Models trained:
1. Baseline Models (Logistic Regression, Linear SVM)
2. Transformer Model (DistilBERT) - Standard configuration
3. Transformer Model (DistilBERT) - Intensive full-scale configuration

Author: CLOUD-NLP-CLASSIFIER-GCP Team
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import json

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message, color=Colors.OKCYAN):
    """Print a formatted header."""
    separator = "=" * 80
    print(f"\n{color}{separator}{Colors.ENDC}")
    print(f"{color}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{color}{separator}{Colors.ENDC}\n")

def print_success(message):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message."""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def format_duration(seconds):
    """Format duration in seconds to human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def check_prerequisites():
    """Check if all prerequisites are met."""
    print_header("Checking Prerequisites", Colors.OKBLUE)
    
    # Check data files
    print_info("Checking data files...")
    data_files = [
        Path("data/processed/train.csv"),
        Path("data/processed/val.csv"),
        Path("data/processed/test.csv")
    ]
    
    missing_files = []
    for file_path in data_files:
        if file_path.exists():
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            missing_files.append(str(file_path))
    
    if missing_files:
        print_error("\nMissing data files! Please run preprocessing first:")
        print("  python run_preprocess.py")
        return False
    
    # Check config files
    print_info("\nChecking configuration files...")
    config_files = [
        Path("config/config_baselines.yaml"),
        Path("config/config_transformer.yaml"),
        Path("config/config_transformer_fullscale.yaml")
    ]
    
    missing_configs = []
    for config_path in config_files:
        if config_path.exists():
            print_success(f"Found: {config_path}")
        else:
            print_error(f"Missing: {config_path}")
            missing_configs.append(str(config_path))
    
    if missing_configs:
        print_error("\nMissing configuration files!")
        return False
    
    print_success("\n✓ All prerequisites met!")
    return True

def run_training_step(name, command, description):
    """Run a single training step and track its performance."""
    print_header(f"Training: {name}", Colors.HEADER)
    print_info(description)
    print_info(f"Command: {' '.join(command)}\n")
    
    start_time = time.time()
    
    try:
        # Run without capturing output - show in real-time
        result = subprocess.run(
            command,
            check=False
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print_success(f"\n✓ {name} completed successfully!")
            print_success(f"Duration: {format_duration(duration)}")
            return {
                "name": name,
                "status": "success",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
        else:
            print_error(f"\n✗ {name} failed with return code {result.returncode}")
            print_error(f"Duration: {format_duration(duration)}")
            return {
                "name": name,
                "status": "failed",
                "duration": duration,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
    
    except KeyboardInterrupt:
        print_error(f"\n\n✗ {name} interrupted by user")
        return {
            "name": name,
            "status": "interrupted",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print_error(f"\n✗ {name} failed with exception: {str(e)}")
        return {
            "name": name,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def save_training_report(results, total_duration):
    """Save training report to file."""
    report = {
        "training_session": {
            "start_time": results[0]["timestamp"] if results else None,
            "end_time": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": format_duration(total_duration)
        },
        "models_trained": results,
        "summary": {
            "total_models": len(results),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "interrupted": sum(1 for r in results if r["status"] == "interrupted")
        }
    }
    
    report_path = Path("training_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print_success(f"\nTraining report saved to: {report_path}")
    return report

def print_final_summary(report):
    """Print final training summary."""
    print_header("Training Session Summary", Colors.HEADER)
    
    summary = report["summary"]
    session = report["training_session"]
    
    print(f"{Colors.BOLD}Total Duration:{Colors.ENDC} {session['total_duration_formatted']}")
    print(f"{Colors.BOLD}Models Trained:{Colors.ENDC} {summary['total_models']}")
    print(f"{Colors.OKGREEN}Successful:{Colors.ENDC} {summary['successful']}")
    
    if summary['failed'] > 0:
        print(f"{Colors.FAIL}Failed:{Colors.ENDC} {summary['failed']}")
    if summary['interrupted'] > 0:
        print(f"{Colors.WARNING}Interrupted:{Colors.ENDC} {summary['interrupted']}")
    
    print(f"\n{Colors.BOLD}Model Results:{Colors.ENDC}")
    for result in report["models_trained"]:
        status_icon = "✓" if result["status"] == "success" else "✗"
        status_color = Colors.OKGREEN if result["status"] == "success" else Colors.FAIL
        duration_str = format_duration(result["duration"]) if "duration" in result else "N/A"
        
        print(f"  {status_color}{status_icon} {result['name']}{Colors.ENDC} - {duration_str}")
    
    print(f"\n{Colors.BOLD}Model Locations:{Colors.ENDC}")
    print(f"  • Baseline Models: models/baselines/")
    print(f"  • DistilBERT (Standard): models/transformer/distilbert/")
    print(f"  • DistilBERT (Full-Scale): models/transformer/distilbert_fullscale/")
    
    if summary['successful'] == summary['total_models']:
        print_success(f"\n🎉 All models trained successfully!")
    elif summary['successful'] > 0:
        print_warning(f"\n⚠ Partial success: {summary['successful']}/{summary['total_models']} models trained")
    else:
        print_error(f"\n❌ Training failed for all models")

def main():
    """Main training orchestration."""
    print_header("FULL-SCALE MODEL TRAINING PIPELINE", Colors.BOLD)
    print_info("This script will train all available models with comprehensive configurations.")
    print_info("Training includes early stopping, detailed logging, and performance tracking.\n")
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("\nPrerequisites not met. Exiting.")
        return 1
    
    # Define training steps
    training_steps = [
        {
            "name": "Baseline Models (Logistic Regression + Linear SVM)",
            "command": [sys.executable, "-m", "src.models.train_baselines"],
            "description": "Training classical ML models with TF-IDF features (10k features, n-grams 1-3)"
        },
        {
            "name": "DistilBERT Transformer (Standard Configuration)",
            "command": [sys.executable, "-m", "src.models.transformer_training", 
                       "--config", "config/config_transformer.yaml"],
            "description": "Training DistilBERT with 256 seq length, 15 epochs, early stopping (patience=5)"
        },
        {
            "name": "DistilBERT Transformer (Intensive Full-Scale)",
            "command": [sys.executable, "-m", "src.models.transformer_training", 
                       "--config", "config/config_transformer_fullscale.yaml"],
            "description": "Training DistilBERT with 512 seq length, 25 epochs, early stopping (patience=8)"
        }
    ]
    
    # Ask for confirmation
    print_warning("\nThis will train 3 models sequentially. Estimated time: 2-6 hours (GPU) or 12-24 hours (CPU)")
    print_info("You can interrupt training at any time with Ctrl+C\n")
    
    response = input(f"{Colors.BOLD}Do you want to proceed? (yes/no): {Colors.ENDC}").strip().lower()
    if response not in ['yes', 'y']:
        print_info("Training cancelled by user.")
        return 0
    
    # Run training steps
    results = []
    overall_start_time = time.time()
    
    for i, step in enumerate(training_steps, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(training_steps)}]{Colors.ENDC}")
        result = run_training_step(step["name"], step["command"], step["description"])
        results.append(result)
        
        # Stop if user interrupted
        if result["status"] == "interrupted":
            print_warning("\nTraining interrupted by user. Saving partial results...")
            break
        
        # Optional: Stop on failure (comment out to continue on failure)
        # if result["status"] == "failed":
        #     print_error("\nStopping due to failure. Enable continue-on-failure if needed.")
        #     break
        
        # Brief pause between models
        if i < len(training_steps):
            print_info(f"\nPreparing next model... (pausing for 5 seconds)")
            time.sleep(5)
    
    overall_end_time = time.time()
    total_duration = overall_end_time - overall_start_time
    
    # Save and display report
    report = save_training_report(results, total_duration)
    print_final_summary(report)
    
    # Return appropriate exit code
    if report["summary"]["successful"] == report["summary"]["total_models"]:
        return 0
    elif report["summary"]["successful"] > 0:
        return 2  # Partial success
    else:
        return 1  # Complete failure

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\n\nTraining interrupted by user. Exiting.")
        sys.exit(130)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
