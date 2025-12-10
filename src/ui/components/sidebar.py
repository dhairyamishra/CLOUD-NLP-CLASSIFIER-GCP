"""
Sidebar component for Streamlit UI.

Provides model selection and information display.
"""

import streamlit as st
from typing import Dict, Any


def render_sidebar(models_info: Dict[str, Dict[str, Any]]) -> str:
    """
    Render the sidebar with model selection and information.
    
    Args:
        models_info: Dictionary with information about available models.
    
    Returns:
        Selected model key.
    """
    with st.sidebar:
        # Title and logo
        st.title("🤖 Cloud NLP Classifier")
        st.markdown("---")
        
        # Model selection
        st.subheader("📊 Select Model")
        
        if not models_info:
            st.error("⚠️ No models available. Please train models first.")
            return None
        
        # Create model options with unique colors for each model
        model_names = list(models_info.keys())
        
        # Define unique color badges for each model
        model_colors = {
            'logreg': '🔵',      # Blue - Logistic Regression
            'svm': '🟢',         # Green - Linear SVM
            'distilbert': '🟣',  # Purple - DistilBERT
            'toxicity': '🟠'     # Orange - Toxicity Classifier
        }
        
        # Add badges to model names
        display_names = []
        for name in model_names:
            info = models_info[name]
            model_key = info['key']
            color_badge = model_colors.get(model_key, '⚪')  # Default to white if unknown
            display_names.append(f"{color_badge} {name}")
        
        # Model selection dropdown
        selected_display = st.selectbox(
            "Choose a model:",
            options=display_names,
            help="Select the model to use for sentiment analysis"
        )
        
        # Get the actual model key
        selected_index = display_names.index(selected_display)
        selected_name = model_names[selected_index]
        selected_model_key = models_info[selected_name]['key']
        
        st.markdown("---")
        
        # Model information
        st.subheader("ℹ️ Model Info")
        
        model_info = models_info[selected_name]
        
        # Display model details
        st.markdown(f"**Type:** {model_info['type'].title()}")
        st.markdown(f"**Description:** {model_info['description']}")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Accuracy", model_info['accuracy'])
        with col2:
            st.metric("F1 Score", model_info['f1_score'])
        
        st.markdown(f"**Speed:** {model_info['inference_speed']}")
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        
        show_probabilities = st.checkbox(
            "Show probabilities",
            value=True,
            help="Display probability scores for all classes"
        )
        
        show_inference_time = st.checkbox(
            "Show inference time",
            value=True,
            help="Display how long the prediction took"
        )
        
        # Store settings in session state
        st.session_state['show_probabilities'] = show_probabilities
        st.session_state['show_inference_time'] = show_inference_time
        
        st.markdown("---")
        
        # Clear history button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state['chat_history'] = []
            st.session_state['inference_count'] = 0
            st.rerun()
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📈 Statistics")
        inference_count = st.session_state.get('inference_count', 0)
        st.metric("Total Predictions", inference_count)
        
        st.markdown("---")
        
        # Footer
        st.markdown("### 📚 About")
        st.markdown(
            """
            This is an interactive sentiment analysis tool powered by 
            machine learning and deep learning models.
            
            **Models Available:**
            - 🔵 Logistic Regression (Baseline)
            - 🟢 Linear SVM (Baseline)
            - 🟣 DistilBERT (Transformer)
            - 🟠 Toxicity Classifier (Multi-label)
            
            **Project:** Cloud NLP Classifier  
            **Phase:** 13 - Streamlit UI
            """
        )
        
        # Links
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center'>
                <small>Built with Streamlit 🎈</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    return selected_model_key
