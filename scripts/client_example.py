"""
Example client script to test the FastAPI prediction endpoint.
"""
import requests
import json
import sys
from typing import Dict, Any


def test_health(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Test the health endpoint.
    
    Args:
        base_url: Base URL of the API server
        
    Returns:
        Health check response
    """
    print("=" * 80)
    print("Testing Health Endpoint")
    print("=" * 80)
    
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Model Loaded: {data['model_loaded']}")
        
        if data['model_loaded']:
            print(f"Model Path: {data['model_path']}")
            print(f"Number of Classes: {data['num_classes']}")
            print(f"Classes: {data['classes']}")
        
        print("=" * 80)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        print("=" * 80)
        return None


def predict_text(
    text: str,
    base_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """
    Send a prediction request to the API.
    
    Args:
        text: Text to classify
        base_url: Base URL of the API server
        
    Returns:
        Prediction response
    """
    print("=" * 80)
    print("Making Prediction")
    print("=" * 80)
    print(f"Input Text: {text}")
    print("-" * 80)
    
    try:
        # Prepare request
        payload = {"text": text}
        
        # Send POST request
        response = requests.post(
            f"{base_url}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Print results
        print(f"Predicted Label: {data['predicted_label']}")
        print(f"Confidence: {data['confidence']:.4f} ({data['confidence']*100:.2f}%)")
        print(f"Inference Time: {data['inference_time_ms']:.2f} ms")
        print("-" * 80)
        print("All Class Scores:")
        
        for score in data['scores']:
            print(f"  {score['label']:20s}: {score['score']:.4f} ({score['score']*100:.2f}%)")
        
        print("=" * 80)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Detail: {error_detail}")
            except:
                print(f"Response: {e.response.text}")
        print("=" * 80)
        return None


def main():
    """Main function to run example predictions."""
    print("\n" + "=" * 80)
    print("FastAPI Client Example")
    print("=" * 80)
    print()
    
    # API base URL
    base_url = "http://localhost:8000"
    
    # Check if server is running
    print("Checking if server is running...")
    try:
        response = requests.get(base_url, timeout=2)
        print("✓ Server is running!")
        print()
    except requests.exceptions.RequestException:
        print("✗ Server is not running!")
        print(f"Please start the server first using: python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000")
        print("Or use the script: .\\scripts\\run_api_local.ps1")
        sys.exit(1)
    
    # Test health endpoint
    health_data = test_health(base_url)
    print()
    
    if not health_data or not health_data.get('model_loaded'):
        print("Model is not loaded. Please train the model first.")
        sys.exit(1)
    
    # Example texts to classify
    example_texts = [
        "I love this product! It's amazing and works perfectly.",
        "This is terrible. Worst experience ever.",
        "The weather is nice today.",
        "I hate you and everything you stand for!",
        "Thank you so much for your help, you're wonderful!",
    ]
    
    # Make predictions for each example
    print("\n" + "=" * 80)
    print("Running Example Predictions")
    print("=" * 80)
    print()
    
    results = []
    for i, text in enumerate(example_texts, 1):
        print(f"\nExample {i}/{len(example_texts)}:")
        result = predict_text(text, base_url)
        if result:
            results.append(result)
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total predictions: {len(results)}")
    
    if results:
        avg_inference_time = sum(r['inference_time_ms'] for r in results) / len(results)
        print(f"Average inference time: {avg_inference_time:.2f} ms")
        
        print("\nPrediction Distribution:")
        label_counts = {}
        for result in results:
            label = result['predicted_label']
            label_counts[label] = label_counts.get(label, 0) + 1
        
        for label, count in label_counts.items():
            print(f"  {label}: {count} ({count/len(results)*100:.1f}%)")
    
    print("=" * 80)
    print("Client example completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
