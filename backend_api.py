"""
Backend API example for churn prediction.

This module demonstrates how to use the ChurnPredictor class
in a backend API context (e.g., Flask, FastAPI).
"""

from typing import Dict, List
import joblib
import os

from src.predictor import ChurnPredictor
from churn_rate.utils.logger import get_logger
from src.config import MODEL_DIR

logger = get_logger(__name__)


class PredictionService:
    """
    Service class for handling churn predictions in a backend environment.
    
    This class loads the trained model and preprocessor once at initialization
    and provides methods for making predictions through API endpoints.
    """
    
    def __init__(self) -> None:
        """Initialize the prediction service by loading model and preprocessor."""
        model_path = os.path.join(MODEL_DIR, "churn_model.pkl")
        preprocessor_path = os.path.join(MODEL_DIR, "preprocessor.pkl")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found at {preprocessor_path}")
        
        logger.info("Loading model and preprocessor...")
        
        # Load model and preprocessor
        self.model = joblib.load(model_path)
        processor = joblib.load(preprocessor_path)
        
        # Create dummy preprocessor object to wrap the loaded transformer
        from src.preprocessor import DataPreprocessor
        self.preprocessor = DataPreprocessor()
        self.preprocessor.processor = processor
        
        # Initialize predictor
        self.predictor = ChurnPredictor(self.model, self.preprocessor)
        
        logger.info("Prediction service initialized successfully")
    
    def predict_customer_churn(
        self,
        customer_data: Dict,
        threshold: float = 0.5
    ) -> Dict:
        """
        Predict churn for a single customer.
        
        Args:
            customer_data: Dictionary with customer features
            threshold: Churn probability threshold (default: 0.5)
            
        Returns:
            Dict with prediction results
            
        Example:
            >>> service = PredictionService()
            >>> customer = {
            ...     'plan_type': 'Premium',
            ...     'tenure_days': 365,
            ...     'watch_hours_30d': 50,
            ...     'login_count_30d': 25,
            ...     'days_since_last_login': 2,
            ...     'support_ticket_count': 1,
            ...     'payment_failure_count': 0,
            ...     'monthly_revenue': 15
            ... }
            >>> result = service.predict_customer_churn(customer)
            >>> print(result)
        """
        return self.predictor.predict_single(customer_data, threshold=threshold)
    
    def predict_customers_batch(
        self,
        customers_data: List[Dict],
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Predict churn for multiple customers.
        
        Args:
            customers_data: List of dictionaries with customer features
            threshold: Churn probability threshold (default: 0.5)
            
        Returns:
            List of dictionaries with prediction results
        """
        results_df = self.predictor.predict_batch(
            customers_data,
            threshold=threshold,
            return_probabilities=True
        )
        
        # Convert to list of dicts
        return results_df.to_dict('records')


# Example FastAPI implementation
def create_fastapi_app():
    """
    Create a FastAPI application with churn prediction endpoints.
    
    Returns:
        FastAPI app instance
    """
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        
        app = FastAPI(title="Churn Prediction API", version="1.0.0")
        service = PredictionService()
        
        # Define request models
        class CustomerData(BaseModel):
            plan_type: str
            tenure_days: int
            watch_hours_30d: float
            login_count_30d: int
            days_since_last_login: int
            support_ticket_count: int
            payment_failure_count: int
            monthly_revenue: float
        
        class BatchPredictionRequest(BaseModel):
            customers: List[CustomerData]
            threshold: float = 0.5
        
        # Health check endpoint
        @app.get("/health")
        def health_check():
            """Health check endpoint."""
            return {"status": "healthy"}
        
        # Single prediction endpoint
        @app.post("/predict")
        def predict_churn(customer: CustomerData, threshold: float = 0.5):
            """Predict churn for a single customer."""
            try:
                result = service.predict_customer_churn(
                    customer.model_dump(),
                    threshold=threshold
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Batch prediction endpoint
        @app.post("/predict-batch")
        def predict_batch(request: BatchPredictionRequest):
            """Predict churn for multiple customers."""
            try:
                results = service.predict_customers_batch(
                    [c.model_dump() for c in request.customers],
                    threshold=request.threshold
                )
                return {"predictions": results}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        return app
    
    except ImportError:
        logger.warning("FastAPI not installed. Skipping FastAPI app creation.")
        return None


if __name__ == "__main__":
    # Example usage
    logger.info("Initializing Prediction Service...")
    service = PredictionService()
    
    # Example single prediction
    sample_customer = {
        'plan_type': 'Premium',
        'tenure_days': 365,
        'watch_hours_30d': 50,
        'login_count_30d': 25,
        'days_since_last_login': 2,
        'support_ticket_count': 1,
        'payment_failure_count': 0,
        'monthly_revenue': 15
    }
    
    logger.info("\nMaking single prediction...")
    result = service.predict_customer_churn(sample_customer)
    logger.info(f"Prediction result: {result}")
