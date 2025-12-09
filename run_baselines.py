#!/usr/bin/env python3
"""
Cross-platform script to run baseline model training.
Works on Windows, Linux, and Mac.
"""
import sys
import subprocess
from pathlib import Path

def print_header(message, color_code=36):
    """Print colored header (cyan by default)."""
    separator = "=" * 60
    print(f"\033[{color_code}m{separator}\033[0m")
    print(f"\033[{color_code}m{message}\033[0m")
    print(f"\033[{color_code}m{separator}\033[0m")

def print_success(message):
    """Print success message in green."""
    print(f"\033[32m{message}\033[0m")

def print_error(message):
    """Print error message in red."""
    print(f"\033[31m{message}\033[0m")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\nChecking dependencies...")
    
    required_modules = [
        ('sklearn', 'scikit-learn'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('joblib', 'joblib'),
        ('yaml', 'PyYAML')
    ]
    
    missing = []
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {name} installed")
        except ImportError:
            print(f"  ✗ {name} NOT installed")
            missing.append(name)
    
    if missing:
        print_error(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("\nPlease install them using:")
        print("  pip install -r requirements.txt")
        return False
    
    print_success("\n✓ All dependencies installed!")
    return True

def check_data():
    """Check if preprocessed data exists."""
    print("\nChecking data files...")
    
    data_files = [
        Path("data/processed/train.csv"),
        Path("data/processed/val.csv"),
        Path("data/processed/test.csv")
    ]
    
    missing = []
    for file_path in data_files:
        if file_path.exists():
            print(f"  ✓ {file_path} exists")
        else:
            print(f"  ✗ {file_path} NOT found")
            missing.append(str(file_path))
    
    if missing:
        print_error(f"\n❌ Missing data files: {', '.join(missing)}")
        print("\nPlease run preprocessing first:")
        print("  python run_preprocess.py")
        return False
    
    print_success("\n✓ All data files found!")
    return True

def run_baselines():
    """Run the baseline training script."""
    print_header("Starting Baseline Model Training Pipeline")
    
    # Check prerequisites
    if not check_dependencies():
        return 1
    
    if not check_data():
        return 1
    
    print("\n" + "=" * 60)
    print("Running baseline training...")
    print("=" * 60 + "\n")
    
    # Run the training module
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.models.train_baselines"],
            check=False
        )
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print_success("✓ Baseline Training Complete!")
            print_success("=" * 60)
            print("\nModels saved to: models/baselines/")
            print("\nNext steps:")
            print("  1. Train transformer: python run_transformer.py")
            print("  2. Compare results")
            return 0
        else:
            print_error("✗ Baseline Training Failed!")
            print_error("=" * 60)
            print("\nPlease check the error messages above.")
            return result.returncode
            
    except KeyboardInterrupt:
        print_error("\n\n✗ Training interrupted by user")
        return 130
    except Exception as e:
        print_error(f"\n✗ Error: {str(e)}")
        return 1

def main():
    """Main entry point."""
    try:
        exit_code = run_baselines()
        sys.exit(exit_code)
    except Exception as e:
        print_error(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
