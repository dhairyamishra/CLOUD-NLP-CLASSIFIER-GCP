"""
Helper functions for Streamlit UI.

Provides utility functions for formatting, colors, and text processing.
"""

from datetime import datetime
from typing import Optional


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Datetime object. If None, use current time.
    
    Returns:
        Formatted timestamp string.
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%H:%M:%S")


def format_confidence(score: float) -> str:
    """
    Format confidence score as percentage.
    
    Args:
        score: Confidence score (0-1).
    
    Returns:
        Formatted percentage string.
    """
    return f"{score * 100:.1f}%"


def get_sentiment_color(label) -> str:
    """
    Get color for sentiment label.
    
    Args:
        label: Sentiment label (string or numeric).
    
    Returns:
        Color code (hex or name).
    """
    # Convert to string if numeric
    label_str = str(label).lower()
    
    # Check for hate/negative indicators
    if 'hate' in label_str or 'toxic' in label_str or 'negative' in label_str or label_str == '1':
        return "#DC3545"  # Red
    # Check for non-hate/positive indicators
    elif 'non-hate' in label_str or 'positive' in label_str or 'neutral' in label_str or label_str == '0':
        return "#28A745"  # Green
    else:
        return "#6C757D"  # Gray


def get_sentiment_emoji(label) -> str:
    """
    Get emoji for sentiment label.
    
    Args:
        label: Sentiment label (string or numeric).
    
    Returns:
        Emoji string.
    """
    # Convert to string if numeric
    label_str = str(label).lower()
    
    # Check for hate/negative indicators
    if 'hate' in label_str or 'toxic' in label_str or 'negative' in label_str or label_str == '1':
        return "⚠️"
    # Check for non-hate/positive indicators
    elif 'non-hate' in label_str or 'positive' in label_str or label_str == '0':
        return "✅"
    elif 'neutral' in label_str:
        return "➖"
    else:
        return "🤖"


def get_model_badge_color(model_type: str) -> str:
    """
    Get badge color for model type.
    
    Args:
        model_type: Type of model (baseline or transformer).
    
    Returns:
        Color code.
    """
    if model_type == 'baseline':
        return "#0066CC"  # Blue
    elif model_type == 'transformer':
        return "#9C27B0"  # Purple
    else:
        return "#6C757D"  # Gray


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text.
        max_length: Maximum length.
    
    Returns:
        Truncated text with ellipsis if needed.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_performance_indicator(inference_time_ms: float) -> tuple[str, str]:
    """
    Get performance indicator based on inference time.
    
    Args:
        inference_time_ms: Inference time in milliseconds.
    
    Returns:
        Tuple of (indicator_text, color).
    """
    if inference_time_ms < 50:
        return "⚡ Fast", "#28A745"
    elif inference_time_ms < 200:
        return "✓ Good", "#FFC107"
    elif inference_time_ms < 1000:
        return "⏱️ Moderate", "#FF9800"
    else:
        return "🐌 Slow", "#DC3545"


def format_probability_bar(probability: float, max_width: int = 20) -> str:
    """
    Create a text-based probability bar.
    
    Args:
        probability: Probability value (0-1).
        max_width: Maximum width of the bar in characters.
    
    Returns:
        Text bar representation.
    """
    filled = int(probability * max_width)
    empty = max_width - filled
    return "█" * filled + "░" * empty
