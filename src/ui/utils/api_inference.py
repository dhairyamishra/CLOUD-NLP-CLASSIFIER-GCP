"""
API-based Inference Handler for Streamlit UI.

Connects to deployed FastAPI backend instead of loading models locally.
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIInferenceHandler:
    """Handles inference by calling the deployed FastAPI backend."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize API Inference Handler.
        
        Args:
            api_url: Base URL of the API. If None, uses environment variable.
        """
        self.api_url = api_url or os.getenv('API_URL', 'http://localhost:8000')
        self.api_url = self.api_url.rstrip('/')  # Remove trailing slash
        self.timeout = 30  # Request timeout in seconds
        
        # Create session with retry logic
        self.session = self._create_session()
        
        logger.info(f"API Inference Handler initialized with URL: {self.api_url}")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests Session.
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET", "POST"]  # Retry on these methods
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test connection to the API.
        
        Returns:
            Tuple of (is_connected, message).
        """
        try:
            response = self.session.get(
                f"{self.api_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    model_info = data.get('current_model', 'unknown')
                    return True, f"✅ Connected to API | Model: {model_info}"
                else:
                    return False, f"⚠️ API is not healthy: {data}"
            else:
                return False, f"❌ API returned status code {response.status_code}"
        
        except requests.exceptions.Timeout:
            return False, f"❌ Connection timeout to {self.api_url}"
        except requests.exceptions.ConnectionError:
            return False, f"❌ Cannot connect to {self.api_url}. Is the API running?"
        except Exception as e:
            return False, f"❌ Connection test failed: {str(e)}"
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available models from the API.
        
        Returns:
            Dictionary with model information.
        """
        try:
            response = self.session.get(
                f"{self.api_url}/models",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get models: {e}")
            return {
                'error': str(e),
                'available_models': []
            }
    
    def predict(self, text: str, model_key: str = None) -> Dict[str, Any]:
        """
        Get prediction from the API.
        
        Args:
            text: Input text to classify.
            model_key: Optional model key (for display purposes).
        
        Returns:
            Dictionary with prediction results.
        """
        try:
            payload = {'text': text}
            
            response = self.session.post(
                f"{self.api_url}/predict",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Transform API response to match expected format
            transformed = {
                'label': result.get('predicted_label', 'Unknown'),
                'confidence': result.get('confidence', 0.0),
                'inference_time_ms': result.get('inference_time_ms', 0.0),
                'model_type': 'api',
                'model_name': result.get('model_name', model_key or 'unknown')
            }
            
            # Add probabilities if available
            if 'scores' in result:
                transformed['probabilities'] = result['scores']
            
            return transformed
        
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return {
                'error': f"Request timed out after {self.timeout} seconds. The API might be overloaded."
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {self.api_url}")
            return {
                'error': f"Cannot connect to API at {self.api_url}. Please check if the API is running."
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            try:
                error_detail = e.response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            return {
                'error': f"API error: {error_detail}"
            }
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'error': f"Unexpected error: {str(e)}"
            }
    
    def switch_model(self, model_name: str) -> Dict[str, Any]:
        """
        Switch the active model on the API.
        
        Args:
            model_name: Name of the model to switch to.
        
        Returns:
            Dictionary with switch result.
        """
        try:
            payload = {'model_name': model_name}
            
            response = self.session.post(
                f"{self.api_url}/models/switch",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Model switch failed: {e}")
            try:
                error_detail = e.response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            return {
                'error': f"Failed to switch model: {error_detail}"
            }
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information from root endpoint.
        
        Returns:
            Dictionary with API information.
        """
        try:
            response = self.session.get(
                f"{self.api_url}/",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get API info: {e}")
            return {
                'error': str(e)
            }


# Singleton instance
_api_inference_handler = None


def get_api_inference_handler(api_url: Optional[str] = None) -> APIInferenceHandler:
    """
    Get or create the APIInferenceHandler singleton instance.
    
    Args:
        api_url: Optional API URL to use. If None, uses environment variable.
    
    Returns:
        APIInferenceHandler instance.
    """
    global _api_inference_handler
    
    # Create new instance if:
    # 1. No instance exists
    # 2. api_url is provided and different from current instance
    if _api_inference_handler is None:
        _api_inference_handler = APIInferenceHandler(api_url=api_url)
    elif api_url and api_url != _api_inference_handler.api_url:
        _api_inference_handler = APIInferenceHandler(api_url=api_url)
    
    return _api_inference_handler
