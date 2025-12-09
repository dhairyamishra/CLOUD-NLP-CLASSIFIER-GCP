"""
Header component for Streamlit UI.

Displays the main title and description.
"""

import streamlit as st
from typing import Dict, Any


def render_header(models_info: Dict[str, Dict[str, Any]]) -> None:
    """
    Render the application header.
    
    Args:
        models_info: Dictionary with information about available models.
    """
    # Main title
    st.markdown(
        """
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='margin: 0;'>💬 Sentiment Analysis Chat</h1>
            <p style='font-size: 18px; color: #6C757D; margin: 10px 0;'>
                Interactive hate speech detection powered by ML and DL models
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Status indicators
    num_models = len(models_info)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🤖 Models Loaded",
            value=num_models,
            help="Number of available models"
        )
    
    with col2:
        inference_count = st.session_state.get('inference_count', 0)
        st.metric(
            label="📊 Predictions Made",
            value=inference_count,
            help="Total number of predictions in this session"
        )
    
    with col3:
        chat_length = len(st.session_state.get('chat_history', []))
        st.metric(
            label="💬 Messages",
            value=chat_length,
            help="Number of messages in chat history"
        )
    
    st.markdown("---")
    
    # Example prompts (expandable)
    with st.expander("💡 Try these example texts"):
        st.markdown(
            """
            **Positive Examples:**
            - "I love this product! It's amazing and works perfectly."
            - "Thank you so much for your help. You're wonderful!"
            - "This is the best day ever! So happy and grateful."
            
            **Negative Examples:**
            - "I hate you and everything you stand for."
            - "You're stupid and worthless, nobody likes you."
            - "This is terrible and offensive content."
            
            **Neutral Examples:**
            - "The weather is nice today."
            - "I went to the store and bought some groceries."
            - "The meeting is scheduled for 3 PM tomorrow."
            """
        )
