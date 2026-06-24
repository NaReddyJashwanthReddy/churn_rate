"""
Churn Rate Prediction Package

A production-level modular package for customer churn prediction.

Modules:
    - config: Configuration constants
    - logger: Logging setup
    - data_loader: Data loading and validation
    - preprocessor: Feature preprocessing and transformation
    - model: Model training and management
    - predictor: Prediction interface for backend use
"""

__version__ = "1.0.0"
__author__ = "Data Science Team"

from src.data_loader import DataLoader
from src.preprocessor import DataPreprocessor
from src.model import ChurnModel
from src.predictor import ChurnPredictor
from utils.logger import get_logger

__all__ = [
    'DataLoader',
    'DataPreprocessor',
    'ChurnModel',
    'ChurnPredictor',
    'get_logger'
]
