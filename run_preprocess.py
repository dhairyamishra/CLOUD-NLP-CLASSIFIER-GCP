#!/usr/bin/env python3
"""
Cross-platform script to run data preprocessing.
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
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'scikit-learn')
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

def check_raw_data():
    """Check if raw data exists."""
    print("\nChecking raw data...")
    
    raw_data_path = Path("data/raw/dataset.csv")
    
    if raw_data_path.exists():
        print(f"  ✓ {raw_data_path} exists")
        print_success("\n✓ Raw data found!")
        return True
    else:
        print(f"  ✗ {raw_data_path} NOT found")
        print_error(f"\n❌ Raw data file not found: {raw_data_path}")
        print("\nPlease ensure you have:")
        print("  1. Downloaded the dataset")
        print("  2. Placed it at: data/raw/dataset.csv")
        print("  3. File should have 'text' and 'label' columns")
        return False

def run_preprocessing():
    """Run the preprocessing script."""
    print_header("Starting Data Preprocessing Pipeline")
    
    # Check prerequisites
    if not check_dependencies():
        return 1
    
    if not check_raw_data():
        return 1
    
    print("\n" + "=" * 60)
    print("Running preprocessing...")
    print("=" * 60 + "\n")
    
    # Run the preprocessing module
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.data.preprocess"],
            check=False
        )
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print_success("✓ Data Preprocessing Complete!")
            print_success("=" * 60)
            print("\nProcessed data saved to:")
            print("  - data/processed/train.csv")
            print("  - data/processed/val.csv")
            print("  - data/processed/test.csv")
            print("\nNext steps:")
            print("  1. Train baselines: python run_baselines.py")
            print("  2. Train transformer: python run_transformer.py")
            return 0
        else:
            print_error("✗ Data Preprocessing Failed!")
            print_error("=" * 60)
            print("\nPlease check the error messages above.")
            return result.returncode
            
    except KeyboardInterrupt:
        print_error("\n\n✗ Preprocessing interrupted by user")
        return 130
    except Exception as e:
        print_error(f"\n✗ Error: {str(e)}")
        return 1

def main():
    """Main entry point."""
    try:
        exit_code = run_preprocessing()
        sys.exit(exit_code)
    except Exception as e:
        print_error(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
