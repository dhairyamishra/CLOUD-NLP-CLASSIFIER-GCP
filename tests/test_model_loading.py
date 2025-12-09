"""
Test script to verify transformer model can be loaded after training.
"""
import os
import json
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

def test_model_loading():
    """Test that the trained model can be loaded successfully."""
    model_path = "models/transformer/distilbert"
    
    # Check if model directory exists
    if not os.path.exists(model_path):
        print(f"❌ Model directory not found: {model_path}")
        print("   Please run training first: .\\scripts\\run_transformer_local.ps1")
        return False
    
    print("=" * 60)
    print("Testing Model Loading")
    print("=" * 60)
    
    try:
        # Load tokenizer
        print("\n1. Loading tokenizer...")
        tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        print("   ✅ Tokenizer loaded successfully")
        
        # Load model
        print("\n2. Loading model...")
        model = DistilBertForSequenceClassification.from_pretrained(model_path)
        print("   ✅ Model loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        print(f"   Number of parameters: {sum(p.numel() for p in model.parameters()):,}")
        
        # Load labels
        print("\n3. Loading label mappings...")
        labels_path = os.path.join(model_path, "labels.json")
        with open(labels_path, 'r') as f:
            labels = json.load(f)
        print(f"   ✅ Labels loaded successfully")
        print(f"   Number of classes: {len(labels['classes'])}")
        print(f"   Classes: {labels['classes']}")
        
        # Test inference
        print("\n4. Testing inference...")
        text = "This is a test sentence to verify the model works."
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = model(**inputs)
        print(f"   ✅ Inference successful!")
        print(f"   Input text: '{text}'")
        print(f"   Output shape: {outputs.logits.shape}")
        print(f"   Expected shape: (1, {len(labels['classes'])})")
        
        # Verify training info
        print("\n5. Checking training info...")
        info_path = os.path.join(model_path, "training_info.json")
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
            print(f"   ✅ Training info found")
            print(f"   Test Accuracy: {info['metrics']['accuracy']:.4f}")
            print(f"   Test F1 Macro: {info['metrics']['f1_macro']:.4f}")
            print(f"   Training time: {info['training_time_minutes']:.2f} minutes")
        else:
            print(f"   ⚠️  Training info not found")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_model_loading()
    exit(0 if success else 1)
