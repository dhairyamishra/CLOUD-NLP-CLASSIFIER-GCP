"""
Evaluation utilities for classification models.
"""
import logging
from typing import Dict, List, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

logger = logging.getLogger(__name__)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Compute comprehensive classification metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities (optional, for ROC-AUC)
        labels: Label names (optional, for better reporting)
        
    Returns:
        Dictionary of metric names and values
    """
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['f1_macro'] = f1_score(y_true, y_pred, average='macro')
    metrics['f1_weighted'] = f1_score(y_true, y_pred, average='weighted')
    metrics['precision_macro'] = precision_score(y_true, y_pred, average='macro')
    metrics['precision_weighted'] = precision_score(y_true, y_pred, average='weighted')
    metrics['recall_macro'] = recall_score(y_true, y_pred, average='macro')
    metrics['recall_weighted'] = recall_score(y_true, y_pred, average='weighted')
    
    # ROC-AUC (if probabilities provided)
    if y_pred_proba is not None:
        try:
            # For binary classification
            if len(np.unique(y_true)) == 2:
                # Use probability of positive class
                if y_pred_proba.ndim == 2:
                    y_pred_proba_binary = y_pred_proba[:, 1]
                else:
                    y_pred_proba_binary = y_pred_proba
                metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba_binary)
            else:
                # For multi-class, use one-vs-rest
                metrics['roc_auc_ovr'] = roc_auc_score(
                    y_true, y_pred_proba, multi_class='ovr', average='macro'
                )
        except Exception as e:
            logger.warning(f"Could not compute ROC-AUC: {str(e)}")
    
    return metrics


def print_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None,
    model_name: str = "Model"
) -> Dict[str, float]:
    """
    Compute and print classification metrics in a formatted way.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities (optional)
        labels: Label names (optional)
        model_name: Name of the model for display
        
    Returns:
        Dictionary of computed metrics
    """
    logger.info("=" * 80)
    logger.info(f"Evaluation Results: {model_name}")
    logger.info("=" * 80)
    
    # Compute metrics
    metrics = compute_classification_metrics(y_true, y_pred, y_pred_proba, labels)
    
    # Print metrics
    logger.info(f"Accuracy:           {metrics['accuracy']:.4f}")
    logger.info(f"F1 Score (Macro):   {metrics['f1_macro']:.4f}")
    logger.info(f"F1 Score (Weighted):{metrics['f1_weighted']:.4f}")
    logger.info(f"Precision (Macro):  {metrics['precision_macro']:.4f}")
    logger.info(f"Recall (Macro):     {metrics['recall_macro']:.4f}")
    
    if 'roc_auc' in metrics:
        logger.info(f"ROC-AUC:            {metrics['roc_auc']:.4f}")
    elif 'roc_auc_ovr' in metrics:
        logger.info(f"ROC-AUC (OvR):      {metrics['roc_auc_ovr']:.4f}")
    
    logger.info("=" * 80)
    
    return metrics


def print_classification_report_detailed(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None
):
    """
    Print detailed classification report.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: Label names (optional)
    """
    logger.info("\nDetailed Classification Report:")
    logger.info("-" * 80)
    
    report = classification_report(y_true, y_pred, target_names=labels)
    logger.info(f"\n{report}")


def print_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None
):
    """
    Print confusion matrix.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: Label names (optional)
    """
    logger.info("\nConfusion Matrix:")
    logger.info("-" * 80)
    
    cm = confusion_matrix(y_true, y_pred)
    
    # Format confusion matrix
    if labels is None:
        labels = [f"Class {i}" for i in range(len(cm))]
    
    # Print header
    header = "True\\Pred |" + " | ".join([f"{label:^10}" for label in labels])
    logger.info(header)
    logger.info("-" * len(header))
    
    # Print rows
    for i, row in enumerate(cm):
        row_str = f"{labels[i]:^10}|" + " | ".join([f"{val:^10}" for val in row])
        logger.info(row_str)
    
    logger.info("-" * 80)


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None,
    model_name: str = "Model",
    detailed: bool = True
) -> Dict[str, float]:
    """
    Complete evaluation pipeline for a model.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities (optional)
        labels: Label names (optional)
        model_name: Name of the model
        detailed: Whether to print detailed report and confusion matrix
        
    Returns:
        Dictionary of computed metrics
    """
    # Print main metrics
    metrics = print_classification_metrics(
        y_true, y_pred, y_pred_proba, labels, model_name
    )
    
    # Print detailed report if requested
    if detailed:
        print_classification_report_detailed(y_true, y_pred, labels)
        print_confusion_matrix(y_true, y_pred, labels)
    
    return metrics
