"""
Training script for baseline models (TF-IDF + Classical ML).
"""
import logging
import time
import argparse
from pathlib import Path
import pandas as pd
import yaml
import numpy as np

from src.models.baselines import BaselineTextClassifier
from src.models.evaluation import evaluate_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/config_baselines.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def load_data(config: dict) -> tuple:
    """Load train, validation, and test datasets."""
    logger.info("Loading datasets...")
    
    train_df = pd.read_csv(config['data']['train_path'])
    val_df = pd.read_csv(config['data']['val_path'])
    test_df = pd.read_csv(config['data']['test_path'])
    
    logger.info(f"Train samples: {len(train_df)}")
    logger.info(f"Val samples: {len(val_df)}")
    logger.info(f"Test samples: {len(test_df)}")
    
    return train_df, val_df, test_df


def train_and_evaluate_model(
    model_name: str,
    model_config: dict,
    vectorizer_config: dict,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    save_dir: str
) -> dict:
    """
    Train and evaluate a single baseline model.
    
    Args:
        model_name: Name of the model (e.g., "logistic_regression")
        model_config: Model-specific configuration
        vectorizer_config: Vectorizer configuration
        train_df: Training dataframe
        val_df: Validation dataframe
        test_df: Test dataframe
        save_dir: Directory to save the model
        
    Returns:
        Dictionary of evaluation metrics
    """
    logger.info("=" * 80)
    logger.info(f"Training Model: {model_name}")
    logger.info("=" * 80)
    
    # Determine classifier type
    if "logistic" in model_name.lower():
        classifier_type = "logistic"
    elif "svm" in model_name.lower():
        classifier_type = "svm"
    else:
        raise ValueError(f"Unknown model type: {model_name}")
    
    # Initialize model
    model = BaselineTextClassifier(
        vectorizer_type=vectorizer_config['type'],
        classifier_type=classifier_type,
        max_features=vectorizer_config['max_features'],
        ngram_range=tuple(vectorizer_config['ngram_range']),
        min_df=vectorizer_config['min_df'],
        max_df=vectorizer_config['max_df'],
        C=model_config['C'],
        max_iter=model_config['max_iter'],
        class_weight=model_config['class_weight'],
        random_state=model_config['random_state']
    )
    
    # Train model
    logger.info("Starting training...")
    train_start = time.time()
    
    model.fit(train_df['text'].tolist(), train_df['label'].values)
    
    train_time = time.time() - train_start
    logger.info(f"Training completed in {train_time:.2f} seconds")
    
    # Evaluate on validation set
    logger.info("\nEvaluating on Validation Set...")
    val_pred = model.predict(val_df['text'].tolist())
    val_pred_proba = model.predict_proba(val_df['text'].tolist())
    
    val_metrics = evaluate_model(
        y_true=val_df['label'].values,
        y_pred=val_pred,
        y_pred_proba=val_pred_proba,
        labels=["Normal", "Hate/Offensive"],
        model_name=f"{model_name} (Validation)",
        detailed=True
    )
    
    # Evaluate on test set
    logger.info("\nEvaluating on Test Set...")
    test_pred = model.predict(test_df['text'].tolist())
    test_pred_proba = model.predict_proba(test_df['text'].tolist())
    
    test_metrics = evaluate_model(
        y_true=test_df['label'].values,
        y_pred=test_pred,
        y_pred_proba=test_pred_proba,
        labels=["Normal", "Hate/Offensive"],
        model_name=f"{model_name} (Test)",
        detailed=True
    )
    
    # Measure inference time
    logger.info("\nMeasuring inference time...")
    sample_texts = test_df['text'].tolist()[:100]
    
    inference_start = time.time()
    _ = model.predict(sample_texts)
    inference_time = time.time() - inference_start
    avg_inference_time = (inference_time / len(sample_texts)) * 1000  # Convert to ms
    
    logger.info(f"Average inference time: {avg_inference_time:.2f} ms per sample")
    
    # Save model
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    model_file = save_path / f"{model_name.lower().replace(' ', '_')}.joblib"
    model.save(str(model_file))
    
    # Print feature importance (for logistic regression)
    if classifier_type == "logistic":
        logger.info("\nTop Features by Importance:")
        logger.info("-" * 80)
        importance = model.get_feature_importance(top_n=10)
        
        if 'positive' in importance:
            logger.info("\nTop features for Hate/Offensive class:")
            for feature, coef in importance['positive']:
                logger.info(f"  {feature:30s} {coef:8.4f}")
            
            logger.info("\nTop features for Normal class:")
            for feature, coef in importance['negative']:
                logger.info(f"  {feature:30s} {coef:8.4f}")
    
    # Compile results
    results = {
        'model_name': model_name,
        'train_time_seconds': train_time,
        'avg_inference_time_ms': avg_inference_time,
        'val_metrics': val_metrics,
        'test_metrics': test_metrics
    }
    
    return results


def main(config_path: str = "config/config_baselines.yaml"):
    """Main training pipeline for baseline models."""
    logger.info("=" * 80)
    logger.info("Baseline Models Training Pipeline")
    logger.info("=" * 80)
    
    # Load configuration
    config = load_config(config_path)
    logger.info(f"Loaded configuration from: {config_path}")
    
    # Load data
    train_df, val_df, test_df = load_data(config)
    
    # Train models
    all_results = []
    
    # 1. Logistic Regression + TF-IDF
    logger.info("\n" + "=" * 80)
    logger.info("Model 1: Logistic Regression + TF-IDF")
    logger.info("=" * 80)
    
    lr_results = train_and_evaluate_model(
        model_name="Logistic_Regression_TFIDF",
        model_config=config['logistic_regression'],
        vectorizer_config=config['vectorizer'],
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        save_dir=config['model_save_dir']
    )
    all_results.append(lr_results)
    
    # 2. Linear SVM + TF-IDF
    logger.info("\n" + "=" * 80)
    logger.info("Model 2: Linear SVM + TF-IDF")
    logger.info("=" * 80)
    
    svm_results = train_and_evaluate_model(
        model_name="Linear_SVM_TFIDF",
        model_config=config['linear_svm'],
        vectorizer_config=config['vectorizer'],
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        save_dir=config['model_save_dir']
    )
    all_results.append(svm_results)
    
    # Print summary comparison
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY: Baseline Models Comparison")
    logger.info("=" * 80)
    
    logger.info(f"\n{'Model':<30} {'Train Time (s)':<15} {'Inference (ms)':<15} {'Test Acc':<12} {'Test F1':<12}")
    logger.info("-" * 90)
    
    for result in all_results:
        logger.info(
            f"{result['model_name']:<30} "
            f"{result['train_time_seconds']:<15.2f} "
            f"{result['avg_inference_time_ms']:<15.2f} "
            f"{result['test_metrics']['accuracy']:<12.4f} "
            f"{result['test_metrics']['f1_macro']:<12.4f}"
        )
    
    logger.info("=" * 80)
    logger.info("Baseline Training Complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train baseline classification models")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config_baselines.yaml",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    main(config_path=args.config)
