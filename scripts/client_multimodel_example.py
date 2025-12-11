"""
Multi-Model Client Example - Test all models and compare performance.

This script demonstrates:
1. Listing available models
2. Switching between models
3. Making predictions with different models
4. Comparing inference times and results
"""
import requests
import json
import time
from typing import Dict, Any, List


# BASE_URL = "http://localhost:8000"
BASE_URL = "http://35.232.76.140:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_health() -> Dict[str, Any]:
    """Test the health endpoint."""
    print_section("1. Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Model Loaded: {data['model_loaded']}")
        print(f"✅ Current Model: {data.get('current_model', 'N/A')}")
        print(f"✅ Available Models: {', '.join(data.get('available_models', []))}")
        
        if data['model_loaded']:
            print(f"   Model Path: {data['model_path']}")
            print(f"   Number of Classes: {data['num_classes']}")
            print(f"   Classes: {', '.join(data['classes'])}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        return None


def list_models() -> Dict[str, Any]:
    """List all available models."""
    print_section("2. List Available Models")
    
    try:
        response = requests.get(f"{BASE_URL}/models")
        response.raise_for_status()
        
        data = response.json()
        print(f"Current Model: {data['current_model']}")
        print(f"\nAvailable Models ({len(data['available_models'])}):")
        
        for model_name, model_info in data['models'].items():
            current_marker = "⭐" if model_info['is_current'] else "  "
            print(f"\n{current_marker} {model_name}:")
            print(f"   Type: {model_info['type']}")
            print(f"   Description: {model_info['description']}")
            print(f"   Path: {model_info['path']}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        return None


def switch_model(model_name: str) -> Dict[str, Any]:
    """Switch to a different model."""
    print(f"\n🔄 Switching to model: {model_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/models/switch",
            json={"model_name": model_name}
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"   Type: {data.get('type', 'N/A')}")
        print(f"   Classes: {data.get('num_classes', 0)}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Details: {e.response.text}")
        return None


def predict_text(text: str, show_all_scores: bool = False) -> Dict[str, Any]:
    """Make a prediction with the current model."""
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"text": text}
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"   Predicted: {data['predicted_label']}")
        print(f"   Confidence: {data['confidence']:.2%}")
        print(f"   Inference Time: {data['inference_time_ms']:.2f}ms")
        print(f"   Model Used: {data.get('model', 'N/A')}")
        
        if show_all_scores:
            print(f"   All Scores:")
            for score in data['scores'][:3]:  # Show top 3
                print(f"      {score['label']}: {score['score']:.2%}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        return None


def compare_models(test_texts: List[str]):
    """Compare all models on the same texts."""
    print_section("3. Model Comparison")
    
    # Get available models
    models_response = requests.get(f"{BASE_URL}/models").json()
    available_models = models_response['available_models']
    
    results = {}
    
    for model_name in available_models:
        print(f"\n{'─' * 80}")
        print(f"Testing Model: {model_name.upper()}")
        print(f"{'─' * 80}")
        
        # Switch to model
        switch_result = switch_model(model_name)
        if not switch_result:
            continue
        
        model_results = []
        total_time = 0
        
        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}: \"{text[:60]}...\"" if len(text) > 60 else f"\nTest {i}: \"{text}\"")
            result = predict_text(text)
            
            if result:
                model_results.append(result)
                total_time += result['inference_time_ms']
        
        avg_time = total_time / len(test_texts) if test_texts else 0
        print(f"\n📊 Average Inference Time: {avg_time:.2f}ms")
        
        results[model_name] = {
            'predictions': model_results,
            'avg_time': avg_time
        }
    
    return results


def print_comparison_summary(results: Dict[str, Any]):
    """Print a summary comparison of all models."""
    print_section("4. Performance Summary")
    
    print(f"\n{'Model':<25} {'Avg Time (ms)':<20} {'Speed Ranking'}")
    print("─" * 70)
    
    # Sort by average time
    sorted_models = sorted(results.items(), key=lambda x: x[1]['avg_time'])
    
    for rank, (model_name, data) in enumerate(sorted_models, 1):
        speed_emoji = "🚀" if rank == 1 else "⚡" if rank == 2 else "🐢"
        print(f"{model_name:<25} {data['avg_time']:<20.2f} {speed_emoji} #{rank}")
    
    print("\n💡 Recommendations:")
    fastest = sorted_models[0][0]
    fastest_time = sorted_models[0][1]['avg_time']
    
    if fastest_time > 0:
        print(f"   • Fastest: {fastest} ({fastest_time:.2f}ms)")
        
        if len(sorted_models) > 1:
            slowest = sorted_models[-1][0]
            slowest_time = sorted_models[-1][1]['avg_time']
            if slowest_time > 0 and fastest_time > 0:
                speedup = slowest_time / fastest_time
                print(f"   • {fastest} is {speedup:.1f}x faster than {slowest}")
    else:
        print(f"   • Fastest: {fastest} (no valid timing data)")
    
    print(f"   • Use DistilBERT for best accuracy (90-93%)")
    print(f"   • Use Logistic Regression or Linear SVM for speed (85-88% accuracy)")


def main():
    """Main function to run all tests."""
    print("\n" + "🎯" * 40)
    print("  MULTI-MODEL TEXT CLASSIFICATION CLIENT")
    print("🎯" * 40)
    
    # Test 1: Health check
    health = test_health()
    if not health or not health.get('model_loaded'):
        print("\n❌ API is not healthy. Please ensure the server is running.")
        return
    
    # Test 2: List models
    models = list_models()
    if not models:
        print("\n❌ Could not retrieve model list.")
        return
    
    # Test 3: Compare models with sample texts
    test_texts = [
        "Apple announces new iPhone with advanced AI features and improved camera",
        "The football team won the championship after an intense final match",
        "Stock market reaches all-time high as investors show confidence",
        "Scientists discover new planet in distant solar system",
        "Breaking news: Major earthquake hits coastal region",
    ]
    
    results = compare_models(test_texts)
    
    # Test 4: Print summary
    if results:
        print_comparison_summary(results)
    
    # Test 5: Interactive mode
    print_section("5. Interactive Testing")
    print("\nYou can now test with your own text!")
    print("Current model:", models['current_model'])
    print("\nTry these commands:")
    print("  • Switch model: POST /models/switch with {\"model_name\": \"logistic_regression\"}")
    print("  • Make prediction: POST /predict with {\"text\": \"your text here\"}")
    print("  • View docs: http://localhost:8000/docs")
    
    print("\n" + "✅" * 40)
    print("  TESTING COMPLETE!")
    print("✅" * 40 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
