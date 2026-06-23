"""
Prediction module for the churn prediction application.

This module handles making predictions using the trained model
and can be used as a backend service.
"""

from typing import Dict, List, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from churn_rate.utils.logger import get_logger
from src.preprocessor import DataPreprocessor

logger = get_logger(__name__)


class ChurnPredictor:
    """
    Handles prediction of customer churn.
    
    This class provides a backend-ready interface for making predictions
    on single customers or batches of customers.
    """
    
    def __init__(
        self,
        model: RandomForestClassifier,
        preprocessor: DataPreprocessor
    ) -> None:
        """
        Initialize ChurnPredictor with a trained model and preprocessor.
        
        Args:
            model: Trained RandomForestClassifier model
            preprocessor: DataPreprocessor instance with fitted transformer
        """
        self.model = model
        self.preprocessor = preprocessor
        logger.info("ChurnPredictor initialized")
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probability of churn for the given features.
        
        Args:
            X: Input features dataframe
            
        Returns:
            np.ndarray: Predicted probabilities [prob_no_churn, prob_churn]
            
        Raises:
            ValueError: If input is invalid
        """
        if X.empty:
            raise ValueError("Input dataframe is empty")
        
        try:
            # Transform features
            X_transformed = self.preprocessor.transform(X)
            
            # Get probabilities
            probabilities = self.model.predict_proba(X_transformed)
            
            logger.info(f"Predictions made for {len(X)} records")
            return probabilities
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """
        Predict churn status for the given features.
        
        Args:
            X: Input features dataframe
            threshold: Probability threshold for churn prediction (default: 0.5)
            
        Returns:
            np.ndarray: Predicted churn status (0 or 1)
            
        Raises:
            ValueError: If input is invalid or threshold is invalid
        """
        if X.empty:
            raise ValueError("Input dataframe is empty")
        
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        try:
            probabilities = self.predict_proba(X)
            predictions = (probabilities[:, 1] >= threshold).astype(int)
            
            logger.info(f"Predictions (threshold={threshold}) made for {len(X)} records")
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def predict_single(
        self,
        customer_data: Dict,
        threshold: float = 0.5
    ) -> Dict[str, Union[int, float]]:
        """
        Predict churn for a single customer (backend API endpoint usage).
        
        This method is designed for backend API usage where individual
        customer data is provided as a dictionary.
        
        Args:
            customer_data: Dictionary containing customer features
            threshold: Probability threshold for churn prediction (default: 0.5)
            
        Returns:
            Dict containing:
                - churn_prediction: 0 (no churn) or 1 (churn)
                - churn_probability: Probability of churn
                - retention_probability: Probability of retention
                
        Raises:
            ValueError: If customer_data is invalid
        """
        try:
            # Convert to dataframe
            df = pd.DataFrame([customer_data])
            
            # Get prediction
            predictions = self.predict(df, threshold=threshold)
            probabilities = self.predict_proba(df)
            
            result = {
                'churn_prediction': int(predictions[0]),
                'churn_probability': float(probabilities[0, 1]),
                'retention_probability': float(probabilities[0, 0]),
                'threshold_used': threshold
            }
            
            logger.info(f"Single prediction: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Single prediction failed: {str(e)}")
            raise
    
    def predict_batch(
        self,
        customers_data: List[Dict],
        threshold: float = 0.5,
        return_probabilities: bool = True
    ) -> pd.DataFrame:
        """
        Predict churn for a batch of customers.
        
        Args:
            customers_data: List of dictionaries containing customer features
            threshold: Probability threshold for churn prediction (default: 0.5)
            return_probabilities: Whether to return probabilities (default: True)
            
        Returns:
            pd.DataFrame: Dataframe with predictions and probabilities
            
        Raises:
            ValueError: If customers_data is empty or invalid
        """
        if not customers_data:
            raise ValueError("customers_data is empty")
        
        try:
            # Convert to dataframe
            df = pd.DataFrame(customers_data)
            
            # Get predictions
            predictions = self.predict(df, threshold=threshold)
            probabilities = self.predict_proba(df)
            
            # Create result dataframe
            result_df = pd.DataFrame({
                'churn_prediction': predictions,
                'churn_probability': probabilities[:, 1],
                'retention_probability': probabilities[:, 0]
            })
            
            logger.info(f"Batch predictions made for {len(result_df)} customers")
            return result_df
            
        except Exception as e:
            logger.error(f"Batch prediction failed: {str(e)}")
            raise
