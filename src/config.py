"""
Configuration module for the churn prediction application.

This module contains all configuration constants used across the application.
"""

import os
from typing import List

# Path Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
CSV_PATH = os.path.join(DATA_DIR, "churn_analytics_data.csv")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Model Configuration
MODEL_RANDOM_STATE = 42
MODEL_N_SPLITS = 5
MODEL_SCORING_METRIC = "f1"
MODEL_MAX_ITER = 1000

# Column Configuration
CATEGORICAL_COLUMNS: List[str] = ["plan_type"]
NUMERIC_COLUMNS_EXCLUDE: List[str] = ["churn_flag", "customer_id"]
TARGET_COLUMN: str = "churn_flag"
CUSTOMER_ID_COLUMN: str = "customer_id"

# Preprocessing Configuration
MIN_MAX_SCALER_FEATURE_RANGE = (0, 1)
ONEHOT_SPARSE_OUTPUT = False
ONEHOT_HANDLE_UNKNOWN = "ignore"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
