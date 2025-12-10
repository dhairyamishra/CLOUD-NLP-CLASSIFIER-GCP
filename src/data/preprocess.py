"""
Text preprocessing utilities and main preprocessing script.
"""
import re
import logging
import argparse
from pathlib import Path
import pandas as pd
from typing import Optional

from src.data.dataset_utils import load_raw_dataset, train_val_test_split, validate_dataframe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove user mentions (e.g., @username)
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags (keep the text, remove the #)
    text = re.sub(r'#(\w+)', r'\1', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess entire dataframe.
    
    Args:
        df: Input dataframe with 'text' and 'label' columns
        
    Returns:
        Preprocessed dataframe
    """
    logger.info(f"Starting preprocessing for {len(df)} samples")
    
    # Validate dataframe
    df = validate_dataframe(df)
    
    # Clean text
    df['text'] = df['text'].apply(clean_text)
    
    # Remove samples with empty text after cleaning
    df = df[df['text'] != '']
    df = df.reset_index(drop=True)
    
    logger.info(f"Preprocessing complete. Final dataset size: {len(df)}")
    
    return df


def main(
    raw_data_path: str = "data/hate_speech/dataset.csv",
    output_dir: str = "data/processed",
    test_size: float = 0.1,
    val_size: float = 0.1,
    random_state: int = 42
):
    """
    Main preprocessing pipeline.
    
    Args:
        raw_data_path: Path to raw CSV file
        output_dir: Directory to save processed splits
        test_size: Proportion for test set
        val_size: Proportion for validation set
        random_state: Random seed for reproducibility
    """
    logger.info("=" * 80)
    logger.info("Starting Data Preprocessing Pipeline")
    logger.info("=" * 80)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load raw data
    logger.info(f"Loading raw data from: {raw_data_path}")
    df = load_raw_dataset(raw_data_path)
    
    # Preprocess data
    logger.info("Preprocessing text data...")
    df = preprocess_dataframe(df)
    
    # Split data
    logger.info("Splitting data into train/val/test sets...")
    train_df, val_df, test_df = train_val_test_split(
        df,
        test_size=test_size,
        val_size=val_size,
        random_state=random_state,
        stratify=True
    )
    
    # Save splits
    train_path = output_path / "train.csv"
    val_path = output_path / "val.csv"
    test_path = output_path / "test.csv"
    
    logger.info(f"Saving train set to: {train_path}")
    train_df.to_csv(train_path, index=False)
    
    logger.info(f"Saving validation set to: {val_path}")
    val_df.to_csv(val_path, index=False)
    
    logger.info(f"Saving test set to: {test_path}")
    test_df.to_csv(test_path, index=False)
    
    # Print summary
    logger.info("=" * 80)
    logger.info("Preprocessing Complete!")
    logger.info("=" * 80)
    logger.info(f"Train samples: {len(train_df)}")
    logger.info(f"Validation samples: {len(val_df)}")
    logger.info(f"Test samples: {len(test_df)}")
    logger.info(f"Total samples: {len(train_df) + len(val_df) + len(test_df)}")
    logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess text classification dataset")
    parser.add_argument(
        "--raw_data_path",
        type=str,
        default="data/hate_speech/dataset.csv",
        help="Path to raw CSV file"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/processed",
        help="Directory to save processed splits"
    )
    parser.add_argument(
        "--test_size",
        type=float,
        default=0.1,
        help="Proportion for test set (0.0 to 1.0)"
    )
    parser.add_argument(
        "--val_size",
        type=float,
        default=0.1,
        help="Proportion for validation set (0.0 to 1.0)"
    )
    parser.add_argument(
        "--random_state",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    main(
        raw_data_path=args.raw_data_path,
        output_dir=args.output_dir,
        test_size=args.test_size,
        val_size=args.val_size,
        random_state=args.random_state
    )
