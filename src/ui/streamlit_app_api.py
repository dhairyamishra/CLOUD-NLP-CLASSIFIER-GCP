"""
Streamlit Application for Cloud NLP Classifier (API Mode).

Interactive sentiment analysis using deployed FastAPI backend.
This version connects to a remote API instead of loading models locally.
"""

import os
import streamlit as st
from datetime import datetime
from typing import Dict, Any

# Import components
from src.ui.components.header import render_header
from src.ui.components.results_display import render_results, render_message_bubble

# Import API inference handler
from src.ui.utils.api_inference import get_api_inference_handler
from src.ui.utils.helpers import format_timestamp


# Page configuration
st.set_page_config(
    page_title="Cloud NLP Classifier",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    if 'inference_count' not in st.session_state:
        st.session_state['inference_count'] = 0
    
    if 'show_probabilities' not in st.session_state:
        st.session_state['show_probabilities'] = True
    
    if 'show_inference_time' not in st.session_state:
        st.session_state['show_inference_time'] = True
    
    if 'selected_model' not in st.session_state:
        st.session_state['selected_model'] = None
    
    if 'api_url' not in st.session_state:
        # Get API URL from environment or use default
        st.session_state['api_url'] = os.getenv('API_URL', 'http://localhost:8000')


def add_message(role: str, content: Any, timestamp: str = None):
    """
    Add a message to chat history.
    
    Args:
        role: Message role ('user' or 'assistant').
        content: Message content.
        timestamp: Optional timestamp string.
    """
    if timestamp is None:
        timestamp = format_timestamp()
    
    st.session_state['chat_history'].append({
        'role': role,
        'content': content,
        'timestamp': timestamp
    })


def render_chat_history():
    """Render the chat history."""
    chat_history = st.session_state.get('chat_history', [])
    
    if not chat_history:
        st.info("👋 Welcome! Enter some text below to analyze its sentiment.")
        return
    
    # Display messages
    for idx, msg in enumerate(chat_history):
        role = msg['role']
        content = msg['content']
        timestamp = msg.get('timestamp', '')
        
        if role == 'user':
            # User message
            render_message_bubble('user', content, timestamp)
        else:
            # Assistant message with results
            render_message_bubble('assistant', None, timestamp)
            render_results(content, key_suffix=f"msg_{idx}")


def render_api_sidebar(api_handler, models_data: Dict[str, Any]):
    """
    Render sidebar with API connection info and model selection.
    
    Args:
        api_handler: APIInferenceHandler instance.
        models_data: Dictionary with available models information.
    
    Returns:
        Selected model key or None.
    """
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # API Connection Status
        st.markdown("### 🌐 API Connection")
        is_connected, message = api_handler.test_connection()
        
        if is_connected:
            st.success(message)
        else:
            st.error(message)
            st.info(f"API URL: `{api_handler.api_url}`")
            return None
        
        st.markdown("---")
        
        # Model Selection
        st.markdown("### 🤖 Model Selection")
        
        available_models = models_data.get('available_models', [])
        current_model = models_data.get('current_model', 'unknown')
        
        if not available_models:
            st.warning("No models available from API")
            return None
        
        # Create model options
        model_options = {}
        for model in available_models:
            # Handle both string and dict formats
            if isinstance(model, str):
                model_name = model
                display_name = model_name
            else:
                model_name = model.get('name', 'Unknown')
                model_type = model.get('type', 'unknown')
                display_name = f"{model_name} ({model_type})"
            model_options[display_name] = model_name
        
        # Find current selection
        current_display = None
        for display, name in model_options.items():
            if name == current_model:
                current_display = display
                break
        
        if current_display is None and model_options:
            current_display = list(model_options.keys())[0]
        
        # Model selector
        selected_display = st.selectbox(
            "Choose a model:",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(current_display) if current_display else 0,
            key="model_selector"
        )
        
        selected_model = model_options[selected_display]
        
        # Show model info (only if models are dicts with details)
        for model in available_models:
            if isinstance(model, dict):
                if model.get('name') == selected_model:
                    with st.expander("📊 Model Details", expanded=False):
                        st.markdown(f"**Type:** {model.get('type', 'N/A')}")
                        st.markdown(f"**Status:** {model.get('status', 'N/A')}")
                    break
            elif model == selected_model:
                # Simple string model name - show basic info
                with st.expander("📊 Model Details", expanded=False):
                    st.markdown(f"**Model:** {selected_model}")
                    st.markdown(f"**Status:** Active")
                break
        
        # Switch model button
        if selected_model != current_model:
            if st.button("🔄 Switch Model", use_container_width=True):
                with st.spinner(f"Switching to {selected_model}..."):
                    result = api_handler.switch_model(selected_model)
                    if 'error' in result:
                        st.error(f"Failed to switch: {result['error']}")
                    else:
                        st.success(f"Switched to {selected_model}")
                        st.rerun()
        
        st.markdown("---")
        
        # Display Options
        st.markdown("### 🎨 Display Options")
        st.session_state['show_probabilities'] = st.checkbox(
            "Show Probabilities",
            value=st.session_state.get('show_probabilities', True)
        )
        st.session_state['show_inference_time'] = st.checkbox(
            "Show Inference Time",
            value=st.session_state.get('show_inference_time', True)
        )
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📈 Statistics")
        st.metric("Total Predictions", st.session_state.get('inference_count', 0))
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state['chat_history'] = []
            st.session_state['inference_count'] = 0
            st.rerun()
        
        return selected_model


def main():
    """Main application logic."""
    # Initialize session state
    initialize_session_state()
    
    # Get API URL
    api_url = st.session_state['api_url']
    
    # Initialize API handler
    try:
        api_handler = get_api_inference_handler(api_url=api_url)
        
        # Test connection
        is_connected, conn_message = api_handler.test_connection()
        
        if not is_connected:
            st.error(
                f"""
                ⚠️ **Cannot connect to API!**
                
                {conn_message}
                
                **API URL:** `{api_url}`
                
                Please ensure:
                1. The API server is running
                2. The API_URL environment variable is set correctly
                3. Network connectivity is available
                """
            )
            return
        
        # Get available models
        models_data = api_handler.get_available_models()
        
        if 'error' in models_data:
            st.error(f"❌ Error getting models: {models_data['error']}")
            return
        
        if not models_data.get('available_models'):
            st.error("⚠️ No models available from API")
            return
        
    except Exception as e:
        st.error(f"❌ Error initializing API handler: {e}")
        st.stop()
        return
    
    # Render sidebar and get selected model
    selected_model_key = render_api_sidebar(api_handler, models_data)
    
    if selected_model_key is None:
        st.error("Please check API connection and model availability.")
        return
    
    # Store selected model in session state
    st.session_state['selected_model'] = selected_model_key
    
    # Render header
    st.markdown(
        """
        <div style='text-align: center; padding: 20px;'>
            <h1>🤖 Cloud NLP Classifier</h1>
            <p style='font-size: 18px; color: #666;'>
                Powered by FastAPI Backend | Real-time Sentiment Analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Main chat area
    st.markdown("### 💬 Chat")
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        render_chat_history()
    
    # Input area (always at bottom)
    st.markdown("---")
    
    # Create columns for input and button
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Enter text to analyze:",
            height=100,
            placeholder="Type your message here... (e.g., 'I love this product!')",
            key="user_input_area",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        submit_button = st.button("🚀 Analyze", use_container_width=True, type="primary")
    
    # Handle submission
    if submit_button and user_input:
        # Add user message to chat
        add_message('user', user_input)
        
        # Show spinner while processing
        with st.spinner(f"🤖 Analyzing with {selected_model_key}..."):
            # Get prediction from API
            result = api_handler.predict(user_input, selected_model_key)
            
            # Add assistant response
            add_message('assistant', result)
            
            # Increment inference count
            st.session_state['inference_count'] += 1
        
        # Rerun to update display
        st.rerun()
    
    elif submit_button and not user_input:
        st.warning("⚠️ Please enter some text to analyze.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #6C757D; font-size: 14px;'>
            <p>
                <strong>Cloud NLP Classifier</strong> | API Mode<br>
                Connected to: <code>{api_url}</code><br>
                Built with Streamlit 🎈 | Powered by FastAPI ⚡
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
