"""
Test script to verify transformer model inference works correctly.
"""
import os
import json
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import numpy as np

def test_inference():
    """Test inference on sample texts."""
    model_path = "models/transformer/distilbert"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Model directory not found: {model_path}")
        print("   Please run training first: .\\scripts\\run_transformer_local.ps1")
        return False
    
    print("=" * 60)
    print("Testing Model Inference")
    print("=" * 60)
    
    try:
        # Load model and tokenizer
        print("\nLoading model and tokenizer...")
        tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        model = DistilBertForSequenceClassification.from_pretrained(model_path)
        model.eval()
        print("✅ Model loaded successfully")
        
        # Load labels
        with open(f"{model_path}/labels.json", 'r') as f:
            label_info = json.load(f)
        id2label = {int(k): v for k, v in label_info['id2label'].items()}
        print(f"✅ Labels loaded: {label_info['classes']}")
        
        # Test samples (adjust based on your dataset)
        test_texts = [
            "I love this product, it's amazing and works perfectly!",
            "This is terrible, worst experience ever. Very disappointed.",
            "It's okay, nothing special. Average quality.",
            "Absolutely fantastic! Highly recommend to everyone.",
            "Horrible service, would not recommend to anyone."
        ]
        
        print("\n" + "=" * 60)
        print("Running Inference on Test Samples")
        print("=" * 60)
        
        for i, text in enumerate(test_texts, 1):
            # Tokenize
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128
            )
            
            # Predict
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)
                pred_class = torch.argmax(probs, dim=1).item()
                confidence = probs[0][pred_class].item()
            
            print(f"\n{i}. Text: {text[:60]}{'...' if len(text) > 60 else ''}")
            print(f"   Predicted: {id2label[pred_class]}")
            print(f"   Confidence: {confidence:.4f}")
            
            # Show all class probabilities
            print(f"   All probabilities:")
            for class_id, prob in enumerate(probs[0].numpy()):
                print(f"      {id2label[class_id]}: {prob:.4f}")
        
        print("\n" + "=" * 60)
        print("✅ Inference test completed successfully!")
        print("=" * 60)
        
        # Measure inference speed
        print("\nMeasuring inference speed...")
        test_text = "This is a test sentence for speed measurement."
        inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
        
        import time
        num_runs = 100
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(num_runs):
                outputs = model(**inputs)
        
        elapsed = time.time() - start_time
        avg_time_ms = (elapsed / num_runs) * 1000
        
        print(f"✅ Average inference time: {avg_time_ms:.2f} ms/sample")
        print(f"   (Based on {num_runs} runs)")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_inference()
    exit(0 if success else 1)
