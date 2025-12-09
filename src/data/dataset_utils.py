"""
Dataset utilities for loading and splitting data.
"""
import logging
from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def load_raw_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load raw dataset from CSV file with basic validation.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        DataFrame with the loaded data
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded dataset from {csv_path} with shape {df.shape}")
        
        # Validate required columns
        required_columns = ['text', 'label']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {list(df.columns)}"
            )
        
        # Basic statistics
        logger.info(f"Dataset has {len(df)} samples")
        logger.info(f"Label distribution:\n{df['label'].value_counts()}")
        
        return df
        
    except FileNotFoundError:
        logger.error(f"Dataset file not found: {csv_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


def train_val_test_split(
    df: pd.DataFrame,
    test_size: float = 0.1,
    val_size: float = 0.1,
    random_state: int = 42,
    stratify: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split dataframe into train, validation, and test sets.
    
    Args:
        df: Input dataframe with 'text' and 'label' columns
        test_size: Proportion of data for test set (0.0 to 1.0)
        val_size: Proportion of data for validation set (0.0 to 1.0)
        random_state: Random seed for reproducibility
        stratify: Whether to maintain label distribution across splits
        
    Returns:
        Tuple of (train_df, val_df, test_df)
        
    Raises:
        ValueError: If required columns are missing or sizes are invalid
    """
    # Validate columns
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError("DataFrame must contain 'text' and 'label' columns")
    
    # Validate split sizes
    if not (0 < test_size < 1) or not (0 < val_size < 1):
        raise ValueError("test_size and val_size must be between 0 and 1")
    
    if test_size + val_size >= 1.0:
        raise ValueError("test_size + val_size must be less than 1.0")
    
    # Prepare stratification
    stratify_col = df['label'] if stratify else None
    
    # First split: separate test set
    train_val_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_col
    )
    
    # Second split: separate validation from training
    # Adjust val_size to be relative to the remaining data
    adjusted_val_size = val_size / (1 - test_size)
    stratify_col_train_val = train_val_df['label'] if stratify else None
    
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=adjusted_val_size,
        random_state=random_state,
        stratify=stratify_col_train_val
    )
    
    # Log split statistics
    logger.info(f"Split sizes - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    logger.info(f"Train label distribution:\n{train_df['label'].value_counts()}")
    logger.info(f"Val label distribution:\n{val_df['label'].value_counts()}")
    logger.info(f"Test label distribution:\n{test_df['label'].value_counts()}")
    
    return train_df, val_df, test_df


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean dataframe.
    
    Args:
        df: Input dataframe
        
    Returns:
        Validated and cleaned dataframe
    """
    initial_size = len(df)
    
    # Remove rows with missing text or label
    df = df.dropna(subset=['text', 'label'])
    
    # Remove empty strings
    df = df[df['text'].str.strip() != '']
    
    # Reset index
    df = df.reset_index(drop=True)
    
    removed = initial_size - len(df)
    if removed > 0:
        logger.warning(f"Removed {removed} invalid samples ({removed/initial_size*100:.2f}%)")
    
    return df
