"""
Baseline text classification models using TF-IDF and classical ML.
"""
import logging
from typing import Optional, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import joblib

logger = logging.getLogger(__name__)


class BaselineTextClassifier:
    """
    Baseline text classifier using TF-IDF/Count vectorization and classical ML.
    
    Supports:
    - Vectorizers: TfidfVectorizer, CountVectorizer
    - Classifiers: LogisticRegression, LinearSVC
    """
    
    def __init__(
        self,
        vectorizer_type: str = "tfidf",
        classifier_type: str = "logistic",
        max_features: int = 10000,
        ngram_range: tuple = (1, 2),
        min_df: int = 2,
        max_df: float = 0.95,
        C: float = 1.0,
        max_iter: int = 1000,
        class_weight: str = "balanced",
        random_state: int = 42,
        # Additional vectorizer parameters
        sublinear_tf: bool = True,
        use_idf: bool = True,
        smooth_idf: bool = True,
        norm: str = "l2",
        # Additional classifier parameters
        solver: str = "saga",
        penalty: str = "l2",
        tol: float = 1e-4,
        n_jobs: int = -1,
        verbose: int = 0,
        # SVM-specific parameters
        loss: str = "squared_hinge",
        dual: bool = True
    ):
        """
        Initialize baseline classifier.
        
        Args:
            vectorizer_type: "tfidf" or "count"
            classifier_type: "logistic" or "svm"
            max_features: Maximum number of features
            ngram_range: N-gram range (e.g., (1, 2) for unigrams and bigrams)
            min_df: Minimum document frequency
            max_df: Maximum document frequency
            C: Regularization parameter
            max_iter: Maximum iterations
            class_weight: Class weight strategy
            random_state: Random seed
        """
        self.vectorizer_type = vectorizer_type
        self.classifier_type = classifier_type
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.C = C
        self.max_iter = max_iter
        self.class_weight = class_weight
        self.random_state = random_state
        # Vectorizer parameters
        self.sublinear_tf = sublinear_tf
        self.use_idf = use_idf
        self.smooth_idf = smooth_idf
        self.norm = norm
        # Classifier parameters
        self.solver = solver
        self.penalty = penalty
        self.tol = tol
        self.n_jobs = n_jobs
        self.verbose = verbose
        # SVM parameters
        self.loss = loss
        self.dual = dual
        
        # Initialize pipeline
        self.pipeline = self._build_pipeline()
        
    def _build_pipeline(self) -> Pipeline:
        """Build sklearn pipeline with vectorizer and classifier."""
        # Choose vectorizer
        if self.vectorizer_type == "tfidf":
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
                max_df=self.max_df,
                sublinear_tf=self.sublinear_tf,
                use_idf=self.use_idf,
                smooth_idf=self.smooth_idf,
                norm=self.norm
            )
        elif self.vectorizer_type == "count":
            vectorizer = CountVectorizer(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
                max_df=self.max_df
            )
        else:
            raise ValueError(f"Unknown vectorizer type: {self.vectorizer_type}")
        
        # Choose classifier
        if self.classifier_type == "logistic":
            classifier = LogisticRegression(
                C=self.C,
                max_iter=self.max_iter,
                class_weight=self.class_weight,
                random_state=self.random_state,
                solver=self.solver,
                penalty=self.penalty,
                tol=self.tol,
                n_jobs=self.n_jobs,
                verbose=self.verbose
            )
        elif self.classifier_type == "svm":
            classifier = LinearSVC(
                C=self.C,
                max_iter=self.max_iter,
                class_weight=self.class_weight,
                random_state=self.random_state,
                loss=self.loss,
                penalty=self.penalty,
                dual=self.dual,
                tol=self.tol,
                verbose=self.verbose
            )
        else:
            raise ValueError(f"Unknown classifier type: {self.classifier_type}")
        
        # Build pipeline
        pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', classifier)
        ])
        
        return pipeline
    
    def fit(self, texts: List[str], labels: np.ndarray):
        """
        Train the model.
        
        Args:
            texts: List of text samples
            labels: Array of labels
        """
        logger.info(f"Training {self.classifier_type} with {self.vectorizer_type} vectorizer...")
        logger.info(f"Training samples: {len(texts)}")
        
        self.pipeline.fit(texts, labels)
        
        logger.info("Training complete!")
        
    def predict(self, texts: List[str]) -> np.ndarray:
        """
        Predict labels for texts.
        
        Args:
            texts: List of text samples
            
        Returns:
            Array of predicted labels
        """
        return self.pipeline.predict(texts)
    
    def predict_proba(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Predict class probabilities for texts.
        
        Args:
            texts: List of text samples
            
        Returns:
            Array of predicted probabilities, or None if not supported
        """
        # Check if classifier supports predict_proba
        classifier = self.pipeline.named_steps['classifier']
        
        if hasattr(classifier, 'predict_proba'):
            return classifier.predict_proba(
                self.pipeline.named_steps['vectorizer'].transform(texts)
            )
        elif hasattr(classifier, 'decision_function'):
            # For SVM, use decision function as proxy
            decision = classifier.decision_function(
                self.pipeline.named_steps['vectorizer'].transform(texts)
            )
            # Convert to pseudo-probabilities using sigmoid
            if decision.ndim == 1:
                # Binary classification
                proba = 1 / (1 + np.exp(-decision))
                return np.vstack([1 - proba, proba]).T
            else:
                # Multi-class
                return decision
        else:
            logger.warning(f"Classifier {self.classifier_type} does not support probability prediction")
            return None
    
    def save(self, path: str):
        """
        Save model to disk.
        
        Args:
            path: Path to save the model
        """
        joblib.dump(self.pipeline, path)
        logger.info(f"Model saved to: {path}")
    
    @classmethod
    def load(cls, path: str) -> 'BaselineTextClassifier':
        """
        Load model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            Loaded BaselineTextClassifier instance
        """
        instance = cls()
        instance.pipeline = joblib.load(path)
        logger.info(f"Model loaded from: {path}")
        return instance
    
    def get_feature_importance(self, top_n: int = 20) -> dict:
        """
        Get top features by importance (for logistic regression).
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            Dictionary mapping class to top features
        """
        classifier = self.pipeline.named_steps['classifier']
        vectorizer = self.pipeline.named_steps['vectorizer']
        
        if not hasattr(classifier, 'coef_'):
            logger.warning("Classifier does not have feature importance")
            return {}
        
        feature_names = vectorizer.get_feature_names_out()
        importance = {}
        
        if classifier.coef_.ndim == 1:
            # Binary classification
            coef = classifier.coef_[0]
            top_positive_idx = np.argsort(coef)[-top_n:][::-1]
            top_negative_idx = np.argsort(coef)[:top_n]
            
            importance['positive'] = [(feature_names[i], coef[i]) for i in top_positive_idx]
            importance['negative'] = [(feature_names[i], coef[i]) for i in top_negative_idx]
        else:
            # Multi-class
            for class_idx in range(classifier.coef_.shape[0]):
                coef = classifier.coef_[class_idx]
                top_idx = np.argsort(coef)[-top_n:][::-1]
                importance[f'class_{class_idx}'] = [(feature_names[i], coef[i]) for i in top_idx]
        
        return importance
