"""
Test script to verify baseline models can be loaded and used for inference.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.baselines import BaselineTextClassifier


def test_model_loading_and_inference():
    """Test that saved models can be loaded and make predictions."""
    
    # Test samples
    test_texts = [
        "I love this product, it's amazing!",
        "You are a stupid idiot and I hate you",
        "The weather is nice today",
        "Go kill yourself you worthless piece of trash"
    ]
    
    models = [
        ("Logistic Regression", "models/baselines/logistic_regression_tfidf.joblib"),
        ("Linear SVM", "models/baselines/linear_svm_tfidf.joblib")
    ]
    
    print("=" * 80)
    print("Testing Baseline Model Inference")
    print("=" * 80)
    
    for model_name, model_path in models:
        print(f"\n{model_name}:")
        print("-" * 80)
        
        # Load model
        model = BaselineTextClassifier.load(model_path)
        print(f"✓ Model loaded successfully from {model_path}")
        
        # Make predictions
        predictions = model.predict(test_texts)
        probabilities = model.predict_proba(test_texts)
        
        print(f"✓ Predictions generated for {len(test_texts)} samples")
        
        # Display results
        print("\nPredictions:")
        for i, (text, pred, proba) in enumerate(zip(test_texts, predictions, probabilities)):
            confidence = max(proba) if proba is not None else "N/A"
            print(f"  {i+1}. [{pred}] (conf: {confidence:.3f}) - {text[:50]}...")
    
    print("\n" + "=" * 80)
    print("✓ All tests passed! Phase 2 implementation verified.")
    print("=" * 80)


if __name__ == "__main__":
    test_model_loading_and_inference()
