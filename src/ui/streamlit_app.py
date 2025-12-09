"""
Main Streamlit Application for Cloud NLP Classifier.

Interactive sentiment analysis with model selection and chat interface.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any

# Import components
from src.ui.components.header import render_header
from src.ui.components.sidebar import render_sidebar
from src.ui.components.results_display import render_results, render_message_bubble

# Import utilities
from src.ui.utils.model_manager import get_model_manager
from src.ui.utils.inference_handler import InferenceHandler
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
            # Use index as unique key suffix
            render_message_bubble('assistant', None, timestamp)
            render_results(content, key_suffix=f"msg_{idx}")


def main():
    """Main application logic."""
    # Initialize session state
    initialize_session_state()
    
    # Load models
    try:
        model_manager = get_model_manager()
        models_info = model_manager.get_available_models()
        
        if not models_info:
            st.error(
                """
                ⚠️ **No models found!**
                
                Please ensure you have trained models in the following locations:
                - `models/baselines/logistic_regression_tfidf.joblib`
                - `models/baselines/linear_svm_tfidf.joblib`
                - `models/transformer/distilbert/`
                
                Run the training scripts first:
                ```bash
                python run_baselines.py
                python run_transformer.py
                ```
                """
            )
            return
        
        # Initialize inference handler
        inference_handler = InferenceHandler(model_manager)
        
    except Exception as e:
        st.error(f"❌ Error loading models: {e}")
        st.stop()
        return
    
    # Render sidebar and get selected model
    selected_model_key = render_sidebar(models_info)
    
    if selected_model_key is None:
        st.error("Please select a model from the sidebar.")
        return
    
    # Store selected model in session state
    st.session_state['selected_model'] = selected_model_key
    
    # Render header
    render_header(models_info)
    
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
            # Get prediction
            result = inference_handler.predict(user_input, selected_model_key)
            
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
        """
        <div style='text-align: center; color: #6C757D; font-size: 14px;'>
            <p>
                <strong>Cloud NLP Classifier</strong> | Phase 13: Streamlit UI<br>
                Built with Streamlit 🎈 | Powered by DistilBERT 🤗
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
