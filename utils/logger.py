"""
Logging module for the churn prediction application.

This module provides centralized logging configuration.
"""

import logging
from src.config import LOG_LEVEL, LOG_FORMAT


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a logger instance with standardized configuration.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    
    return logger
