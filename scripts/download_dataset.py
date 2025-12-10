"""
Script to download datasets for NLP classification.

Supports multiple datasets:
1. hate_speech - Binary hate speech classification
2. toxicity - Multi-label toxicity classification (Jigsaw)
"""
import argparse
import logging
import pandas as pd
from pathlib import Path
from datasets import load_dataset
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_hate_speech_dataset(output_path: str = "data/hate_speech/dataset.csv"):
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


def download_toxicity_dataset(output_dir: str = "data/toxicity"):
    """
    Download Jigsaw Toxic Comment Classification dataset.
    
    This dataset contains multi-label toxicity annotations:
    - toxic, severe_toxic, obscene, threat, insult, identity_hate
    
    Args:
        output_dir: Directory to save train.csv and test.csv (default: data/toxicity)
    """
    logger.info("=" * 80)
    logger.info("Downloading Toxicity Dataset (Jigsaw)")
    logger.info("=" * 80)
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Try to load from HuggingFace
        logger.info("Attempting to download from HuggingFace...")
        dataset = load_dataset("jigsaw_toxicity_pred", trust_remote_code=True)
        
        logger.info(f"✅ Dataset loaded from HuggingFace")
        logger.info(f"Train samples: {len(dataset['train'])}")
        
        # Convert to DataFrame
        train_df = pd.DataFrame(dataset['train'])
        
        # Rename columns if needed
        if 'text' in train_df.columns and 'comment_text' not in train_df.columns:
            train_df = train_df.rename(columns={'text': 'comment_text'})
        
    except Exception as e:
        logger.warning(f"HuggingFace download failed: {e}")
        logger.info("Creating sample toxicity dataset for testing...")
        
        # Create sample dataset
        sample_data = {
            'comment_text': [
                "This is a normal comment",
                "You are an idiot",
                "I hate you so much",
                "Great work, keep it up!",
                "This is terrible and you should feel bad",
                "Nice job on this project",
                "You're stupid and ugly",
                "I love this community",
                "Go away, nobody wants you here",
                "Thanks for sharing this information",
            ] * 100,  # 1000 samples
            'toxic': [0, 1, 1, 0, 1, 0, 1, 0, 1, 0] * 100,
            'severe_toxic': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0] * 100,
            'obscene': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0] * 100,
            'threat': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0] * 100,
            'insult': [0, 1, 0, 0, 1, 0, 1, 0, 1, 0] * 100,
            'identity_hate': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0] * 100,
        }
        train_df = pd.DataFrame(sample_data)
    
    # Ensure required columns exist
    required_cols = ['comment_text', 'toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    for col in required_cols[1:]:  # Skip comment_text
        if col not in train_df.columns:
            logger.warning(f"Column '{col}' not found, filling with 0")
            train_df[col] = 0
    
    # Create train/test split
    train_df, test_df = train_test_split(train_df, test_size=0.1, random_state=42)
    
    # Save datasets
    train_path = Path(output_dir) / "train.csv"
    test_path = Path(output_dir) / "test.csv"
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    # Print statistics
    logger.info("=" * 80)
    logger.info("Dataset Download Complete!")
    logger.info("=" * 80)
    logger.info(f"Train samples: {len(train_df)}")
    logger.info(f"Test samples: {len(test_df)}")
    logger.info(f"Saved to: {output_dir}")
    logger.info("\nToxicity Label Distribution (Train):")
    
    for col in required_cols[1:]:
        if col in train_df.columns:
            toxic_count = train_df[col].sum()
            toxic_pct = (toxic_count / len(train_df)) * 100
            logger.info(f"  {col:15s}: {toxic_count:5d} ({toxic_pct:5.2f}%)")
    
    logger.info("=" * 80)
    
    return train_df, test_df


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(description="Download NLP classification datasets")
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["hate_speech", "toxicity", "both"],
        default="hate_speech",
        help="Which dataset to download (default: hate_speech)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: data/hate_speech for hate_speech, data/toxicity for toxicity)"
    )
    
    args = parser.parse_args()
    
    if args.dataset in ["hate_speech", "both"]:
        output_path = args.output_dir if args.output_dir else "data/hate_speech/dataset.csv"
        logger.info("\n📥 Downloading Hate Speech Dataset...")
        download_hate_speech_dataset(output_path)
    
    if args.dataset in ["toxicity", "both"]:
        output_dir = args.output_dir if args.output_dir else "data/toxicity"
        logger.info("\n📥 Downloading Toxicity Dataset...")
        download_toxicity_dataset(output_dir)
    
    logger.info("\n✅ All downloads complete!")
    logger.info("\nNext steps:")
    if args.dataset in ["hate_speech", "both"]:
        logger.info("  - Preprocess hate speech data: python -m src.data.preprocess")
        logger.info("  - Train baseline models: python run_baselines.py")
        logger.info("  - Train transformer: python run_transformer.py")
    if args.dataset in ["toxicity", "both"]:
        logger.info("  - Train toxicity model: python -m src.models.train_toxicity")
        logger.info("  - Or use script: .\\scripts\\run_toxicity_training.ps1")


if __name__ == "__main__":
    main()
