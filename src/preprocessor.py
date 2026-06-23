"""
Preprocessing module for the churn prediction application.

This module handles data transformation and feature engineering.
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from src.config import (
    MIN_MAX_SCALER_FEATURE_RANGE,
    ONEHOT_HANDLE_UNKNOWN,
    ONEHOT_SPARSE_OUTPUT,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class DataPreprocessor:
    """
    Handles data preprocessing and transformation.
    
    This class creates and manages the column transformer for feature scaling
    and encoding. It also provides methods for fitting and transforming data.
    """
    
    def __init__(self) -> None:
        """Initialize DataPreprocessor."""
        self.processor: Optional[ColumnTransformer] = None
        self.num_columns: Optional[list] = None
        self.cat_columns: Optional[list] = None
        logger.info("DataPreprocessor initialized")
    
    def build_processor(self, num_columns: list, cat_columns: list) -> ColumnTransformer:
        """
        Build the column transformer with scalers and encoders.
        
        Args:
            num_columns: List of numeric column names
            cat_columns: List of categorical column names
            
        Returns:
            ColumnTransformer: Fitted transformer
        """
        self.num_columns = list(num_columns)
        self.cat_columns = list(cat_columns)
        
        logger.info(f"Building preprocessor with:")
        logger.info(f"  - Numeric columns: {self.num_columns}")
        logger.info(f"  - Categorical columns: {self.cat_columns}")
        
        self.processor = ColumnTransformer([
            ('numeric', MinMaxScaler(feature_range=MIN_MAX_SCALER_FEATURE_RANGE), self.num_columns),
            ('categorical', OneHotEncoder(
                sparse_output=ONEHOT_SPARSE_OUTPUT,
                handle_unknown=ONEHOT_HANDLE_UNKNOWN
            ), self.cat_columns)
        ], remainder='passthrough')
        
        logger.info("ColumnTransformer created successfully")
        return self.processor
    
    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit the processor and transform the input data.
        
        Args:
            X: Input features dataframe
            
        Returns:
            np.ndarray: Transformed data
            
        Raises:
            ValueError: If processor is not built
        """
        if self.processor is None:
            raise ValueError("Processor not built. Call build_processor() first.")
        
        try:
            transformed_data = self.processor.fit_transform(X)
            logger.info(f"Data transformed successfully. Shape: {transformed_data.shape}")
            return transformed_data
        except Exception as e:
            logger.error(f"Failed to transform data: {str(e)}")
            raise
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform the input data using the fitted processor.
        
        Args:
            X: Input features dataframe
            
        Returns:
            np.ndarray: Transformed data
            
        Raises:
            ValueError: If processor is not fitted
        """
        if self.processor is None:
            raise ValueError("Processor not fitted. Call fit_transform() first.")
        
        try:
            transformed_data = self.processor.transform(X)
            logger.info(f"Data transformed successfully. Shape: {transformed_data.shape}")
            return transformed_data
        except Exception as e:
            logger.error(f"Failed to transform data: {str(e)}")
            raise
    
    def get_processor(self) -> ColumnTransformer:
        """
        Get the fitted processor.
        
        Returns:
            ColumnTransformer: The fitted processor
            
        Raises:
            ValueError: If processor is not fitted
        """
        if self.processor is None:
            raise ValueError("Processor not fitted.")
        return self.processor
