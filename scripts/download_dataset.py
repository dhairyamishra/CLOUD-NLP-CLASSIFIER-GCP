"""
Script to download hate speech dataset.

This script downloads a popular hate speech detection dataset from Hugging Face.
We'll use the "hate_speech_offensive" dataset which is well-suited for this task.
"""
import logging
import pandas as pd
from pathlib import Path
from datasets import load_dataset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_hate_speech_dataset(output_path: str = "data/raw/dataset.csv"):
    """
    Download hate speech dataset from Hugging Face and save as CSV.
    
    We'll use the "hate_speech_offensive" dataset which contains:
    - Text: Tweet text
    - Label: 0 (hate speech), 1 (offensive language), 2 (neither)
    
    For simplicity, we'll combine into binary classification:
    - 0 or 1 -> 1 (hate/offensive)
    - 2 -> 0 (normal)
    
    Args:
        output_path: Path to save the CSV file
    """
    logger.info("=" * 80)
    logger.info("Downloading Hate Speech Dataset")
    logger.info("=" * 80)
    
    # Create output directory
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download dataset from Hugging Face
        logger.info("Downloading dataset from Hugging Face...")
        logger.info("Dataset: hate_speech_offensive")
        
        # Load the dataset
        dataset = load_dataset("hate_speech_offensive", trust_remote_code=True)
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(dataset['train'])
        
        logger.info(f"Downloaded {len(df)} samples")
        logger.info(f"Columns: {list(df.columns)}")
        
        # The dataset has 'tweet' and 'class' columns
        # Rename to standard 'text' and 'label'
        if 'tweet' in df.columns:
            df = df.rename(columns={'tweet': 'text'})
        if 'class' in df.columns:
            df = df.rename(columns={'class': 'label'})
        
        # Convert to binary classification
        # Original: 0 (hate speech), 1 (offensive language), 2 (neither)
        # New: 0 (neither), 1 (hate/offensive)
        logger.info("Converting to binary classification...")
        logger.info(f"Original label distribution:\n{df['label'].value_counts()}")
        
        df['label'] = df['label'].apply(lambda x: 0 if x == 2 else 1)
        
        logger.info(f"Binary label distribution:\n{df['label'].value_counts()}")
        
        # Keep only text and label columns
        df = df[['text', 'label']]
        
        # Save to CSV
        logger.info(f"Saving dataset to: {output_path}")
        df.to_csv(output_path, index=False)
        
        # Print statistics
        logger.info("=" * 80)
        logger.info("Dataset Download Complete!")
        logger.info("=" * 80)
        logger.info(f"Total samples: {len(df)}")
        logger.info(f"Label distribution:")
        logger.info(f"  - Class 0 (Normal): {(df['label'] == 0).sum()} ({(df['label'] == 0).sum() / len(df) * 100:.2f}%)")
        logger.info(f"  - Class 1 (Hate/Offensive): {(df['label'] == 1).sum()} ({(df['label'] == 1).sum() / len(df) * 100:.2f}%)")
        logger.info(f"Average text length: {df['text'].str.len().mean():.2f} characters")
        logger.info("=" * 80)
        
        # Show sample data
        logger.info("\nSample data:")
        logger.info(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        logger.info("\nAlternative: You can manually download a hate speech dataset and place it at:")
        logger.info(f"  {output_path}")
        logger.info("\nRequired format: CSV with 'text' and 'label' columns")
        raise


if __name__ == "__main__":
    download_hate_speech_dataset()
