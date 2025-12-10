"""
Test script for toxicity classification model.
Tests inference on sample texts.
"""
import os
import sys
import json
import torch
import logging
from pathlib import Path
from transformers import AutoTokenizer, DistilBertForSequenceClassification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test samples
TEST_SAMPLES = [
    {
        "text": "This is a great project! Well done!",
        "expected": "non-toxic"
    },
    {
        "text": "You are an idiot and nobody likes you",
        "expected": "toxic, insult"
    },
    {
        "text": "I will find you and hurt you",
        "expected": "toxic, threat"
    },
    {
        "text": "This is absolutely disgusting and offensive",
        "expected": "toxic, obscene"
    },
    {
        "text": "Thanks for sharing this information",
        "expected": "non-toxic"
    },
    {
        "text": "You're so stupid, go kill yourself",
        "expected": "toxic, severe_toxic, insult"
    },
]

def load_model(model_path="models/toxicity_multi_head"):
    """Load the trained toxicity model."""
    logger.info(f"Loading model from {model_path}...")
    
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}")
        logger.info("Please train the model first:")
        logger.info("  python -m src.models.train_toxicity")
        sys.exit(1)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # Load model
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    
    # Load labels
    labels_path = os.path.join(model_path, "labels.json")
    if os.path.exists(labels_path):
        with open(labels_path, 'r') as f:
            labels_data = json.load(f)
            labels = labels_data.get("classes", list(labels_data.get("id2label", {}).values()))
    else:
        # Default labels
        labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    
    # Set to eval mode
    model.eval()
    
    # Check for GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    logger.info(f"✅ Model loaded successfully")
    logger.info(f"   Device: {device}")
    logger.info(f"   Labels: {labels}")
    
    return model, tokenizer, labels, device

def predict(text, model, tokenizer, labels, device, threshold=0.5):
    """Make prediction on a single text."""
    # Tokenize
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256
    )
    
    # Move to device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        
        # Apply sigmoid to get probabilities
        probs = torch.sigmoid(logits).cpu().numpy()[0]
    
    # Create results
    results = {}
    flagged_labels = []
    
    for i, label in enumerate(labels):
        prob = float(probs[i])
        results[label] = prob
        
        if prob > threshold:
            flagged_labels.append(label)
    
    return results, flagged_labels

def print_prediction(text, results, flagged_labels, expected=None):
    """Pretty print prediction results."""
    print("\n" + "=" * 80)
    print(f"Text: {text}")
    print("-" * 80)
    
    if expected:
        print(f"Expected: {expected}")
        print("-" * 80)
    
    print("Toxicity Scores:")
    for label, prob in results.items():
        flag = "⚠️ " if prob > 0.5 else "✅ "
        bar = "█" * int(prob * 20)
        print(f"  {flag} {label:15s}: {prob:.4f} |{bar}")
    
    print("-" * 80)
    if flagged_labels:
        print(f"🚨 Flagged as: {', '.join(flagged_labels)}")
    else:
        print("✅ Non-toxic")
    print("=" * 80)

def main():
    """Main test function."""
    logger.info("=" * 80)
    logger.info("Toxicity Model Testing")
    logger.info("=" * 80)
    
    # Load model
    model, tokenizer, labels, device = load_model()
    
    # Test on samples
    logger.info(f"\nTesting on {len(TEST_SAMPLES)} sample texts...")
    
    for i, sample in enumerate(TEST_SAMPLES, 1):
        text = sample["text"]
        expected = sample.get("expected", "")
        
        # Predict
        results, flagged_labels = predict(text, model, tokenizer, labels, device)
        
        # Print results
        print_prediction(text, results, flagged_labels, expected)
    
    # Interactive mode
    print("\n" + "=" * 80)
    print("Interactive Testing Mode")
    print("=" * 80)
    print("Enter text to classify (or 'quit' to exit):")
    
    while True:
        try:
            text = input("\n> ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not text:
                continue
            
            results, flagged_labels = predict(text, model, tokenizer, labels, device)
            print_prediction(text, results, flagged_labels)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    logger.info("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
