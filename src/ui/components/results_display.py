"""
Results display component for Streamlit UI.

Formats and displays prediction results.
"""

import streamlit as st
from typing import Dict, Any
import plotly.graph_objects as go
import html
from src.ui.utils.helpers import (
    format_confidence,
    get_sentiment_color,
    get_sentiment_emoji,
    get_performance_indicator
)


def render_toxicity_results(result: Dict[str, Any], key_suffix: str = None) -> None:
    """
    Render toxicity prediction results (multi-label).
    
    Args:
        result: Dictionary with toxicity prediction results.
        key_suffix: Optional suffix for unique widget keys.
    """
    import time
    
    # Generate unique key if not provided
    if key_suffix is None:
        key_suffix = str(time.time()).replace('.', '_')
    
    # Check for errors
    if 'error' in result:
        st.error(f"❌ {result['error']}")
        return
    
    # Extract data
    is_toxic = result.get('is_toxic', False)
    toxicity_scores = result.get('toxicity_scores', [])
    flagged_categories = result.get('flagged_categories', [])
    
    # Escape flagged categories for HTML display
    escaped_categories = ', '.join([html.escape(str(cat)) for cat in flagged_categories])
    
    # Overall status
    if is_toxic:
        st.markdown(
            f"""
            <div style='
                background-color: #ff444420;
                border-left: 4px solid #ff4444;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            '>
                <h3 style='margin: 0; color: #ff4444;'>
                    🚨 Toxic Content Detected
                </h3>
                <p style='margin: 5px 0 0 0; font-size: 16px;'>
                    <strong>Flagged categories:</strong> {escaped_categories}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='
                background-color: #00cc0020;
                border-left: 4px solid #00cc00;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            '>
                <h3 style='margin: 0; color: #00cc00;'>
                    ✅ Non-Toxic Content
                </h3>
                <p style='margin: 5px 0 0 0; font-size: 16px;'>
                    No toxicity categories flagged
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Toxicity scores
    st.markdown("### 📊 Toxicity Category Scores")
    
    for score_data in toxicity_scores:
        category = score_data['category']
        score = score_data['score']
        flagged = score_data['flagged']
        
        # Color based on score
        if score > 0.7:
            color = "#ff4444"
        elif score > 0.5:
            color = "#ff8800"
        elif score > 0.3:
            color = "#ffcc00"
        else:
            color = "#00cc00"
        
        # Display with progress bar
        col1, col2 = st.columns([3, 1])
        with col1:
            flag_emoji = "⚠️" if flagged else "✅"
            st.markdown(f"{flag_emoji} **{category.replace('_', ' ').title()}**")
            st.progress(score)
        with col2:
            st.markdown(f"<div style='color: {color}; font-size: 20px; font-weight: bold; text-align: right;'>{score:.1%}</div>", unsafe_allow_html=True)

def render_results(result: Dict[str, Any], key_suffix: str = None) -> None:
    """
    Render prediction results in a formatted way.
    
    Args:
        result: Dictionary with prediction results.
        key_suffix: Optional suffix for unique widget keys.
    """
    import time
    
    # Generate unique key if not provided
    if key_suffix is None:
        key_suffix = str(time.time()).replace('.', '_')
    
    # Check if this is a toxicity result
    if result.get('model_type') == 'toxicity':
        return render_toxicity_results(result, key_suffix)
    
    # Check for errors
    if 'error' in result:
        st.error(f"❌ {result['error']}")
        return
    
    # Get settings from session state
    show_probabilities = st.session_state.get('show_probabilities', True)
    show_inference_time = st.session_state.get('show_inference_time', True)
    
    # Extract result data
    label = result.get('label', 'Unknown')
    confidence = result.get('confidence', 0.0)
    inference_time = result.get('inference_time_ms', 0.0)
    probabilities = result.get('probabilities', {})
    model_type = result.get('model_type', 'unknown')
    
    # Get color and emoji
    color = get_sentiment_color(label)
    emoji = get_sentiment_emoji(label)
    
    # Escape label to prevent HTML injection
    escaped_label = html.escape(str(label))
    
    # Main result container
    with st.container():
        # Sentiment badge
        st.markdown(
            f"""
            <div style='
                background-color: {color}20;
                border-left: 4px solid {color};
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            '>
                <h3 style='margin: 0; color: {color};'>
                    {emoji} {escaped_label}
                </h3>
                <p style='margin: 5px 0 0 0; font-size: 18px;'>
                    <strong>Confidence:</strong> {format_confidence(confidence)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Inference time
        if show_inference_time:
            perf_indicator, perf_color = get_performance_indicator(inference_time)
            st.markdown(
                f"""
                <div style='margin: 10px 0; color: {perf_color};'>
                    {perf_indicator} • Inference time: {inference_time:.2f}ms
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Probability scores
        if show_probabilities and probabilities:
            st.markdown("### 📊 Probability Scores")
            
            # Define consistent label order (don't sort by value)
            # This ensures consistent axis ordering regardless of probabilities
            label_order = {
                'Hate Speech': 0,
                'Non-Hate Speech': 1,
                'hate_speech': 0,
                'non_hate_speech': 1,
                'positive': 0,
                'negative': 1,
                'neutral': 2
            }
            
            # Sort by predefined order, fallback to alphabetical
            sorted_probs = sorted(
                probabilities.items(),
                key=lambda x: label_order.get(x[0], ord(x[0][0]))
            )
            
            # Create horizontal bar chart
            labels_list = [item[0] for item in sorted_probs]
            values_list = [item[1] * 100 for item in sorted_probs]  # Convert to percentage
            
            # Color bars based on sentiment
            colors_list = [get_sentiment_color(label) for label in labels_list]
            
            fig = go.Figure(data=[
                go.Bar(
                    y=labels_list,
                    x=values_list,
                    orientation='h',
                    marker=dict(
                        color=colors_list,
                        line=dict(color='rgba(0,0,0,0.3)', width=1)
                    ),
                    text=[f"{v:.1f}%" for v in values_list],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                xaxis_title="Probability (%)",
                yaxis_title="Class",
                height=max(200, len(labels_list) * 60),
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
                xaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")
        
        # Model info badge
        model_badge_color = "#0066CC" if model_type == 'baseline' else "#9C27B0"
        model_badge_text = "ML Model" if model_type == 'baseline' else "DL Model"
        
        st.markdown(
            f"""
            <div style='text-align: right; margin-top: 10px;'>
                <span style='
                    background-color: {model_badge_color};
                    color: white;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-size: 12px;
                '>
                    {model_badge_text}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_message_bubble(role: str, content: Any, timestamp: str = None) -> None:
    """
    Render a chat message bubble.
    
    Args:
        role: Message role ('user' or 'assistant').
        content: Message content (str for user, dict for assistant).
        timestamp: Optional timestamp string.
    """
    if role == 'user':
        # User message (right-aligned, blue)
        # Escape HTML to prevent rendering issues
        escaped_content = html.escape(content)
        escaped_timestamp = html.escape(timestamp) if timestamp else ""
        
        # Build the complete HTML string at once
        html_content = f"""
            <div style='
                text-align: right;
                margin: 10px 0;
            '>
                <div style='
                    display: inline-block;
                    background-color: #0066CC;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 15px 15px 0 15px;
                    max-width: 70%;
                    text-align: left;
                '>
                    {escaped_content}
                </div>
        """
        
        # Add timestamp if present
        if timestamp:
            html_content += f"""<div style='font-size: 11px; color: #6C757D; margin-top: 3px;'>{escaped_timestamp}</div>"""
        
        html_content += """</div>"""
        
        st.markdown(html_content, unsafe_allow_html=True)
    else:
        # Assistant message (left-aligned, gray)
        escaped_timestamp = html.escape(timestamp) if timestamp else ""
        
        # Build the complete HTML string at once
        html_content = f"""
            <div style='
                text-align: left;
                margin: 10px 0;
            '>
                <div style='
                    display: inline-block;
                    background-color: #F0F2F6;
                    color: #262730;
                    padding: 10px 15px;
                    border-radius: 15px 15px 15px 0;
                    max-width: 70%;
                    text-align: left;
                '>
                    🤖 <strong>Analysis Result</strong>
                </div>
        """
        
        # Add timestamp if present
        if timestamp:
            html_content += f"""<div style='font-size: 11px; color: #6C757D; margin-top: 3px;'>{escaped_timestamp}</div>"""
        
        html_content += """</div>"""
        
        st.markdown(html_content, unsafe_allow_html=True)
