"""
Test script for toxicity API endpoint.
Tests the /predict/toxicity endpoint with various examples.
"""
import requests
import json
import time
from typing import Dict, List

# API Configuration
API_URL = "http://localhost:8000"
TOXICITY_ENDPOINT = f"{API_URL}/predict/toxicity"

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
    {
        "text": "I hate all people from that country",
        "expected": "toxic, identity_hate"
    },
]

def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_toxicity_result(text: str, result: Dict, expected: str = None):
    """Pretty print toxicity analysis result."""
    print("\n" + "=" * 80)
    print(f"Text: {text}")
    print("-" * 80)
    
    if expected:
        print(f"Expected: {expected}")
        print("-" * 80)
    
    # Overall status
    if result["is_toxic"]:
        print(f"🚨 TOXIC - Flagged categories: {', '.join(result['flagged_categories'])}")
    else:
        print("✅ NON-TOXIC")
    
    print("-" * 80)
    print("Toxicity Scores:")
    
    # Print scores
    for score in result["toxicity_scores"]:
        category = score["category"]
        prob = score["score"]
        flagged = score["flagged"]
        
        flag = "⚠️ " if flagged else "✅ "
        bar = "█" * int(prob * 20)
        print(f"  {flag} {category:15s}: {prob:.4f} |{bar}")
    
    print("-" * 80)
    print(f"Inference time: {result['inference_time_ms']:.2f}ms")
    print("=" * 80)

def test_health():
    """Test health endpoint."""
    print_header("Testing Health Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Model loaded: {data['model_loaded']}")
        print(f"✅ Current model: {data.get('current_model', 'None')}")
        print(f"✅ Available models: {data['available_models']}")
        
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_toxicity_prediction(text: str, expected: str = None) -> Dict:
    """Test toxicity prediction for a single text."""
    try:
        # Make request
        response = requests.post(
            TOXICITY_ENDPOINT,
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Parse result
        result = response.json()
        
        # Print result
        print_toxicity_result(text, result, expected)
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_batch_predictions():
    """Test multiple predictions."""
    print_header(f"Testing {len(TEST_SAMPLES)} Sample Texts")
    
    results = []
    total_time = 0
    
    for i, sample in enumerate(TEST_SAMPLES, 1):
        print(f"\n[{i}/{len(TEST_SAMPLES)}]")
        result = test_toxicity_prediction(sample["text"], sample["expected"])
        
        if result:
            results.append(result)
            total_time += result["inference_time_ms"]
    
    # Summary
    if results:
        print_header("Summary")
        print(f"Total predictions: {len(results)}")
        print(f"Successful: {len(results)}/{len(TEST_SAMPLES)}")
        print(f"Total inference time: {total_time:.2f}ms")
        print(f"Average inference time: {total_time / len(results):.2f}ms")
        
        # Count toxic vs non-toxic
        toxic_count = sum(1 for r in results if r["is_toxic"])
        print(f"\nToxic samples: {toxic_count}")
        print(f"Non-toxic samples: {len(results) - toxic_count}")

def interactive_mode():
    """Interactive testing mode."""
    print_header("Interactive Toxicity Testing")
    print("Enter text to analyze (or 'quit' to exit):")
    
    while True:
        try:
            text = input("\n> ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not text:
                continue
            
            test_toxicity_prediction(text)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main test function."""
    print_header("Toxicity API Testing")
    print(f"API URL: {API_URL}")
    print(f"Endpoint: {TOXICITY_ENDPOINT}")
    
    # Test health
    if not test_health():
        print("\n❌ Server not available. Please start the server first:")
        print("   python -m uvicorn src.api.server:app --reload")
        return
    
    # Test predictions
    test_batch_predictions()
    
    # Interactive mode
    print("\n")
    choice = input("Enter interactive mode? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_mode()
    
    print_header("Testing Complete!")

if __name__ == "__main__":
    main()
