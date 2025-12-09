"""
Quick API endpoint testing script for Phase 5.
Tests all endpoints and verifies multi-model functionality.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("API ENDPOINT TESTING")
print("=" * 80)

# Test 1: Root endpoint
print("\n1. Testing Root Endpoint (GET /)...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 2: Health check
print("\n2. Testing Health Check (GET /health)...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Status: {data.get('status')}")
    print(f"   Current Model: {data.get('current_model')}")
    print(f"   Available Models: {data.get('available_models')}")
    assert response.status_code == 200
    assert data.get('status') == 'healthy'
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 3: List models
print("\n3. Testing List Models (GET /models)...")
try:
    response = requests.get(f"{BASE_URL}/models")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Current Model: {data.get('current_model')}")
    print(f"   Available Models: {len(data.get('available_models', []))}")
    for model in data.get('available_models', []):
        print(f"     - {model['name']}: {model['type']} (Acc: {model.get('accuracy', 'N/A')})")
    assert response.status_code == 200
    assert len(data.get('available_models', [])) == 3
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 4: Prediction with DistilBERT
print("\n4. Testing Prediction with DistilBERT (POST /predict)...")
try:
    payload = {"text": "I love this product! It's amazing!"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Text: {payload['text']}")
    print(f"   Predicted Label: {data.get('predicted_label')}")
    print(f"   Confidence: {data.get('confidence', 0)*100:.2f}%")
    print(f"   Model Used: {data.get('model_used')}")
    print(f"   Inference Time: {data.get('inference_time_ms', 0):.2f}ms")
    assert response.status_code == 200
    assert 'predicted_label' in data
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 5: Switch to Logistic Regression
print("\n5. Testing Model Switch to Logistic Regression (POST /models/switch)...")
try:
    payload = {"model_name": "logistic_regression"}
    response = requests.post(f"{BASE_URL}/models/switch", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Message: {data.get('message')}")
    print(f"   Previous Model: {data.get('previous_model')}")
    print(f"   Current Model: {data.get('current_model')}")
    assert response.status_code == 200
    assert data.get('current_model') == 'logistic_regression'
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 6: Prediction with Logistic Regression
print("\n6. Testing Prediction with Logistic Regression (POST /predict)...")
try:
    payload = {"text": "This is offensive and hateful content"}
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    elapsed = (time.time() - start_time) * 1000
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Text: {payload['text']}")
    print(f"   Predicted Label: {data.get('predicted_label')}")
    print(f"   Confidence: {data.get('confidence', 0)*100:.2f}%")
    print(f"   Model Used: {data.get('model_used')}")
    print(f"   Inference Time: {data.get('inference_time_ms', 0):.2f}ms")
    print(f"   Total Request Time: {elapsed:.2f}ms")
    assert response.status_code == 200
    assert data.get('model_used') == 'logistic_regression'
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 7: Switch to Linear SVM
print("\n7. Testing Model Switch to Linear SVM (POST /models/switch)...")
try:
    payload = {"model_name": "linear_svm"}
    response = requests.post(f"{BASE_URL}/models/switch", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Current Model: {data.get('current_model')}")
    assert response.status_code == 200
    assert data.get('current_model') == 'linear_svm'
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 8: Prediction with Linear SVM
print("\n8. Testing Prediction with Linear SVM (POST /predict)...")
try:
    payload = {"text": "Normal everyday conversation"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Text: {payload['text']}")
    print(f"   Predicted Label: {data.get('predicted_label')}")
    print(f"   Confidence: {data.get('confidence', 0)*100:.2f}%")
    print(f"   Model Used: {data.get('model_used')}")
    print(f"   Inference Time: {data.get('inference_time_ms', 0):.2f}ms")
    assert response.status_code == 200
    assert data.get('model_used') == 'linear_svm'
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 9: Switch back to DistilBERT
print("\n9. Testing Model Switch back to DistilBERT (POST /models/switch)...")
try:
    payload = {"model_name": "distilbert"}
    response = requests.post(f"{BASE_URL}/models/switch", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Current Model: {data.get('current_model')}")
    assert response.status_code == 200
    assert data.get('current_model') == 'distilbert'
    print("   ✅ PASSED")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 10: Invalid model switch
print("\n10. Testing Invalid Model Switch (POST /models/switch)...")
try:
    payload = {"model_name": "invalid_model"}
    response = requests.post(f"{BASE_URL}/models/switch", json=payload)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 400
    print("   ✅ PASSED (correctly rejected invalid model)")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 80)
print("API TESTING COMPLETE!")
print("=" * 80)
print("\n✅ All 10 tests completed!")
print("\nNext steps:")
print("  1. Check interactive docs: http://localhost:8000/docs")
print("  2. Run full test suite: python run_tests.py")
print("  3. Stop the server (Ctrl+C in server terminal)")
print("=" * 80)
