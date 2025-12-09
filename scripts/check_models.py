"""
Diagnostic script to check if models are available in the container/environment.

This script helps debug model loading issues in Docker containers.
"""

import os
import sys
from pathlib import Path


def check_models():
    """Check for the presence of trained models."""
    print("=" * 70)
    print("MODEL AVAILABILITY CHECK")
    print("=" * 70)
    print()
    
    # Determine project root
    if os.path.exists('/app'):
        # Running in Docker
        project_root = Path('/app')
        print("🐳 Running in Docker container")
    else:
        # Running locally
        project_root = Path(__file__).parent.parent
        print("💻 Running locally")
    
    print(f"📁 Project root: {project_root}")
    print()
    
    models_dir = project_root / "models"
    baseline_dir = models_dir / "baselines"
    transformer_dir = models_dir / "transformer" / "distilbert"
    
    # Check directories
    print("📂 Directory Structure:")
    print(f"  models/: {'✅ EXISTS' if models_dir.exists() else '❌ NOT FOUND'}")
    print(f"  models/baselines/: {'✅ EXISTS' if baseline_dir.exists() else '❌ NOT FOUND'}")
    print(f"  models/transformer/distilbert/: {'✅ EXISTS' if transformer_dir.exists() else '❌ NOT FOUND'}")
    print()
    
    # Check baseline models
    print("🔵 Baseline Models:")
    logreg_path = baseline_dir / "logistic_regression_tfidf.joblib"
    svm_path = baseline_dir / "linear_svm_tfidf.joblib"
    
    logreg_exists = logreg_path.exists()
    svm_exists = svm_path.exists()
    
    if logreg_exists:
        size_mb = logreg_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Logistic Regression: {logreg_path} ({size_mb:.2f} MB)")
    else:
        print(f"  ❌ Logistic Regression: NOT FOUND at {logreg_path}")
    
    if svm_exists:
        size_mb = svm_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Linear SVM: {svm_path} ({size_mb:.2f} MB)")
    else:
        print(f"  ❌ Linear SVM: NOT FOUND at {svm_path}")
    
    print()
    
    # Check transformer model
    print("🟣 Transformer Model (DistilBERT):")
    
    if transformer_dir.exists():
        required_files = [
            "config.json",
            "pytorch_model.bin",
            "tokenizer_config.json",
            "vocab.txt",
            "labels.json"
        ]
        
        all_found = True
        for filename in required_files:
            file_path = transformer_dir / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ {filename}: {size_mb:.2f} MB")
            else:
                print(f"  ❌ {filename}: NOT FOUND")
                all_found = False
        
        if all_found:
            print(f"  ✅ All transformer files present")
        else:
            print(f"  ⚠️ Some transformer files are missing")
    else:
        print(f"  ❌ Transformer directory NOT FOUND at {transformer_dir}")
    
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    models_found = []
    if logreg_exists:
        models_found.append("Logistic Regression")
    if svm_exists:
        models_found.append("Linear SVM")
    if transformer_dir.exists() and (transformer_dir / "pytorch_model.bin").exists():
        models_found.append("DistilBERT")
    
    if models_found:
        print(f"✅ Found {len(models_found)} model(s):")
        for model in models_found:
            print(f"   - {model}")
    else:
        print("❌ No models found!")
        print()
        print("To train models, run:")
        print("  python run_baselines.py")
        print("  python run_transformer.py")
    
    print()
    print("=" * 70)
    
    return len(models_found) > 0


if __name__ == "__main__":
    success = check_models()
    sys.exit(0 if success else 1)
