"""
Data loading module for the churn prediction application.

This module handles all data loading and basic validation operations.
"""

import os
from typing import Tuple

import pandas as pd

from src.config import CSV_PATH, NUMERIC_COLUMNS_EXCLUDE, TARGET_COLUMN
from churn_rate.utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """
    Handles data loading and initial data validation.
    
    This class is responsible for loading CSV files and performing
    basic data quality checks.
    """
    
    def __init__(self, csv_path: str = CSV_PATH) -> None:
        """
        Initialize DataLoader with a CSV path.
        
        Args:
            csv_path: Path to the CSV file containing the data
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Data file not found at: {csv_path}")
        
        self.csv_path = csv_path
        self.data: pd.DataFrame = None
        logger.info(f"DataLoader initialized with path: {csv_path}")
    
    def load_data(self) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            Exception: If data loading fails
        """
        try:
            self.data = pd.read_csv(self.csv_path)
            logger.info(f"Data loaded successfully. Shape: {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
    
    def validate_data(self) -> bool:
        """
        Perform basic data validation checks.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Check for empty dataframe
        if self.data.empty:
            raise ValueError("Data is empty")
        
        # Check for required columns
        required_columns = list(NUMERIC_COLUMNS_EXCLUDE) + [TARGET_COLUMN]
        missing_columns = set(required_columns) - set(self.data.columns)
        
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")
        
        # Check for duplicates
        duplicates = self.data.duplicated().sum()
        logger.info(f"Duplicate rows found: {duplicates}")
        
        # Check for null values
        null_counts = self.data.isnull().sum()
        if null_counts.any():
            logger.warning(f"Null values found:\n{null_counts[null_counts > 0]}")
        
        logger.info("Data validation passed")
        return True
    
    def get_feature_columns(self) -> Tuple[pd.Index, pd.Index]:
        """
        Get categorical and numeric column indices from the data.
        
        Returns:
            Tuple[pd.Index, pd.Index]: Categorical columns, Numeric columns (excluding target and id)
            
        Raises:
            ValueError: If data is not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Remove customer_id and target column
        working_data = self.data.drop(columns=NUMERIC_COLUMNS_EXCLUDE, errors='ignore')
        
        cat_columns = working_data.select_dtypes(include='object').columns
        num_columns = working_data.select_dtypes(exclude='object').columns
        
        logger.info(f"Categorical columns: {list(cat_columns)}")
        logger.info(f"Numeric columns: {list(num_columns)}")
        
        return cat_columns, num_columns
    
    def get_features_and_target(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Get features and target variable from the data.
        
        Returns:
            Tuple[pd.DataFrame, pd.Series]: Features (X), Target (y)
            
        Raises:
            ValueError: If data is not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        X = self.data.drop(columns=NUMERIC_COLUMNS_EXCLUDE, errors='ignore')
        y = self.data[TARGET_COLUMN]
        
        return X, y
