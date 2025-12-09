"""
Cross-platform script to run Streamlit UI.

This script works on Windows, Linux, and Mac.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_streamlit_installed():
    """Check if Streamlit is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def install_streamlit():
    """Install Streamlit and dependencies."""
    print("Installing Streamlit...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "streamlit>=1.28.0", "plotly>=5.17.0"],
            check=True
        )
        print("✓ Streamlit installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install Streamlit")
        return False


def check_models_exist():
    """Check if trained models exist."""
    project_root = Path(__file__).parent
    
    models_found = []
    
    # Check baseline models
    logreg_path = project_root / "models" / "baselines" / "logistic_regression_tfidf.joblib"
    if logreg_path.exists():
        models_found.append("Logistic Regression")
    
    svm_path = project_root / "models" / "baselines" / "linear_svm_tfidf.joblib"
    if svm_path.exists():
        models_found.append("Linear SVM")
    
    # Check transformer model
    transformer_path = project_root / "models" / "transformer" / "distilbert" / "pytorch_model.bin"
    if transformer_path.exists():
        models_found.append("DistilBERT")
    
    return models_found


def main():
    """Main function."""
    print("=" * 50)
    print("  Cloud NLP Classifier - Streamlit UI")
    print("=" * 50)
    print()
    
    # Check Streamlit installation
    print("Checking dependencies...")
    if not check_streamlit_installed():
        print("✗ Streamlit is not installed!")
        print()
        if not install_streamlit():
            sys.exit(1)
    else:
        print("✓ Streamlit is installed")
    
    print()
    
    # Check for models
    print("Checking for trained models...")
    models_found = check_models_exist()
    
    if models_found:
        for model in models_found:
            print(f"✓ {model} model found")
    else:
        print()
        print("⚠ WARNING: No trained models found!")
        print("Please train models first:")
        print("  python run_baselines.py")
        print("  python run_transformer.py")
        print()
        print("The UI will start but may not work without models.")
        print()
        
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting...")
            sys.exit(1)
    
    print()
    print("=" * 50)
    print("Starting Streamlit UI...")
    print("=" * 50)
    print()
    print("The UI will open in your browser at:")
    print("  http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Get project root and app path
    project_root = Path(__file__).parent
    app_path = project_root / "src" / "ui" / "streamlit_app.py"
    
    # Run Streamlit
    try:
        subprocess.run(
            [
                sys.executable, "-m", "streamlit", "run",
                str(app_path),
                "--server.port", "8501"
            ],
            cwd=str(project_root)
        )
    except KeyboardInterrupt:
        print()
        print("Shutting down...")
    except Exception as e:
        print(f"✗ Error running Streamlit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
