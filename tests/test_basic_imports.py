"""
Basic import tests to verify package structure.
"""
import pytest


def test_import_data_utils():
    """Test that data utilities can be imported."""
    from src.data import dataset_utils
    from src.data import preprocess
    
    assert hasattr(dataset_utils, 'load_raw_dataset')
    assert hasattr(dataset_utils, 'train_val_test_split')
    assert hasattr(preprocess, 'clean_text')
    assert hasattr(preprocess, 'preprocess_dataframe')


def test_clean_text_function():
    """Test basic text cleaning functionality."""
    from src.data.preprocess import clean_text
    
    # Test URL removal
    text = "Check this out http://example.com"
    cleaned = clean_text(text)
    assert "http://" not in cleaned
    assert "example.com" not in cleaned
    
    # Test lowercase conversion
    text = "THIS IS UPPERCASE"
    cleaned = clean_text(text)
    assert cleaned == "this is uppercase"
    
    # Test whitespace normalization
    text = "Too   many    spaces"
    cleaned = clean_text(text)
    assert "  " not in cleaned


def test_import_config():
    """Test that config module exists."""
    import config
    assert config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
