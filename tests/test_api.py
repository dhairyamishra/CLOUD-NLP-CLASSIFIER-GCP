"""
Tests for FastAPI server endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.server import app, model_manager


# Create test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    
    # Check if model is loaded
    if data["model_loaded"]:
        assert data["status"] == "ok"
        assert "model_path" in data
        assert "num_classes" in data
        assert "classes" in data
        assert isinstance(data["classes"], list)
    else:
        assert data["status"] == "model_not_loaded"


def test_predict_endpoint_valid_text():
    """Test prediction endpoint with valid text."""
    # Skip if model is not loaded
    if not model_manager.is_loaded():
        pytest.skip("Model not loaded - train model first")
    
    # Test with sample text
    payload = {"text": "This is a test message for classification."}
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "predicted_label" in data
    assert "confidence" in data
    assert "scores" in data
    assert "inference_time_ms" in data
    
    # Validate confidence is between 0 and 1
    assert 0.0 <= data["confidence"] <= 1.0
    
    # Validate scores
    assert isinstance(data["scores"], list)
    assert len(data["scores"]) > 0
    
    for score in data["scores"]:
        assert "label" in score
        assert "score" in score
        assert 0.0 <= score["score"] <= 1.0
    
    # Validate inference time is positive
    assert data["inference_time_ms"] > 0


def test_predict_endpoint_empty_text():
    """Test prediction endpoint with empty text."""
    payload = {"text": ""}
    response = client.post("/predict", json=payload)
    
    # Should return validation error
    assert response.status_code == 422


def test_predict_endpoint_whitespace_only():
    """Test prediction endpoint with whitespace-only text."""
    payload = {"text": "   "}
    response = client.post("/predict", json=payload)
    
    # Should return validation error
    assert response.status_code == 422


def test_predict_endpoint_missing_text():
    """Test prediction endpoint with missing text field."""
    payload = {}
    response = client.post("/predict", json=payload)
    
    # Should return validation error
    assert response.status_code == 422


def test_predict_endpoint_long_text():
    """Test prediction endpoint with long text."""
    # Skip if model is not loaded
    if not model_manager.is_loaded():
        pytest.skip("Model not loaded - train model first")
    
    # Create a long text
    long_text = "This is a test. " * 100
    payload = {"text": long_text}
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data


def test_predict_endpoint_special_characters():
    """Test prediction endpoint with special characters."""
    # Skip if model is not loaded
    if not model_manager.is_loaded():
        pytest.skip("Model not loaded - train model first")
    
    # Text with special characters
    special_text = "Hello! @#$%^&*() How are you? 😊"
    payload = {"text": special_text}
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data


def test_predict_endpoint_multiple_requests():
    """Test multiple consecutive predictions."""
    # Skip if model is not loaded
    if not model_manager.is_loaded():
        pytest.skip("Model not loaded - train model first")
    
    texts = [
        "This is the first test message.",
        "Here is another message to classify.",
        "And one more for good measure.",
    ]
    
    for text in texts:
        payload = {"text": text}
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_label" in data
        assert "confidence" in data


def test_openapi_schema():
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    
    # Check that our endpoints are in the schema
    assert "/health" in schema["paths"]
    assert "/predict" in schema["paths"]


def test_docs_endpoint():
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint():
    """Test that ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
