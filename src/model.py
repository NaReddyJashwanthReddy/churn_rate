"""
Model module for the churn prediction application.

This module handles model training, evaluation, and selection.
"""

import os
from typing import Dict, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate

from src.config import (
    MODEL_MAX_ITER,
    MODEL_N_SPLITS,
    MODEL_RANDOM_STATE,
    MODEL_SCORING_METRIC,
    MODEL_DIR,
)
from churn_rate.utils.logger import get_logger

logger = get_logger(__name__)


class ChurnModel:
    """
    Manages churn prediction model training and evaluation.
    
    This class handles model creation, cross-validation, and selection
    of the best performing model.
    """
    
    def __init__(self) -> None:
        """Initialize ChurnModel."""
        self.model: Optional[RandomForestClassifier] = None
        self.best_cv_results: Optional[Dict] = None
        self.best_fold_index: Optional[int] = None
        logger.info("ChurnModel initialized")
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Train the model using stratified k-fold cross-validation.
        
        Uses RandomForestClassifier and evaluates it with cross-validation
        to select the best performing fold.
        
        Args:
            X: Input features (already transformed)
            y: Target variable
            
        Returns:
            Dict: Cross-validation results containing scores and estimators
        """
        logger.info("Starting model training with cross-validation...")
        logger.info(f"Data shape: X={X.shape}, y={y.shape}")
        
        # Create stratified k-fold splitter
        stf = StratifiedKFold(
            n_splits=MODEL_N_SPLITS,
            shuffle=True,
            random_state=MODEL_RANDOM_STATE
        )
        
        # Initialize model
        model = RandomForestClassifier(random_state=MODEL_RANDOM_STATE)
        
        # Perform cross-validation
        try:
            cv_results = cross_validate(
                model,
                X,
                y,
                cv=stf,
                scoring=MODEL_SCORING_METRIC,
                return_estimator=True
            )
            
            logger.info(f"Cross-validation completed")
            logger.info(f"Test scores: {cv_results['test_score']}")
            logger.info(f"Mean score: {np.mean(cv_results['test_score']):.4f}")
            
            # Select best model from the folds
            self.best_fold_index = np.argmax(cv_results['test_score'])
            self.model = cv_results['estimator'][self.best_fold_index]
            self.best_cv_results = cv_results
            
            logger.info(f"Best model selected from fold {self.best_fold_index} "
                       f"with score: {cv_results['test_score'][self.best_fold_index]:.4f}")
            
            return cv_results
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise
    
    def get_model(self) -> RandomForestClassifier:
        """
        Get the trained model.
        
        Returns:
            RandomForestClassifier: The trained model
            
        Raises:
            ValueError: If model is not trained
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        return self.model
    
    def save_model(self, filename: str = "churn_model.pkl") -> str:
        """
        Save the trained model to disk.
        
        Args:
            filename: Name of the file to save the model
            
        Returns:
            str: Path to the saved model
            
        Raises:
            ValueError: If model is not trained
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        model_path = os.path.join(MODEL_DIR, filename)
        
        try:
            joblib.dump(self.model, model_path)
            logger.info(f"Model saved successfully to: {model_path}")
            return model_path
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise
    
    def load_model(self, filename: str = "churn_model.pkl") -> RandomForestClassifier:
        """
        Load a trained model from disk.
        
        Args:
            filename: Name of the file containing the saved model
            
        Returns:
            RandomForestClassifier: The loaded model
            
        Raises:
            FileNotFoundError: If the model file does not exist
        """
        model_path = os.path.join(MODEL_DIR, filename)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        
        try:
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded successfully from: {model_path}")
            return self.model
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def get_cv_results(self) -> Dict:
        """
        Get cross-validation results.
        
        Returns:
            Dict: Cross-validation results
            
        Raises:
            ValueError: If model is not trained
        """
        if self.best_cv_results is None:
            raise ValueError("Model not trained. Call train() first.")
        return self.best_cv_results
