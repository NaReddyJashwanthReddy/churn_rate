"""
Training orchestration script for the churn prediction model.

This script orchestrates the entire training pipeline:
1. Load data
2. Validate data
3. Preprocess features
4. Train model
5. Save model and preprocessor
"""

from src.data_loader import DataLoader
from src.preprocessor import DataPreprocessor
from src.model import ChurnModel
from utils.logger import get_logger
import joblib
import os
from src.config import MODEL_DIR

logger = get_logger(__name__)


def train_pipeline() -> None:
    """
    Execute the complete training pipeline.
    
    Raises:
        Exception: If any step in the pipeline fails
    """
    logger.info("=" * 60)
    logger.info("Starting Churn Prediction Model Training Pipeline")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load Data
        logger.info("\n[Step 1/5] Loading data...")
        data_loader = DataLoader()
        df = data_loader.load_data()
        
        # Step 2: Validate Data
        logger.info("\n[Step 2/5] Validating data...")
        data_loader.validate_data()
        
        # Step 3: Get features and preprocess
        logger.info("\n[Step 3/5] Preprocessing features...")
        X, y = data_loader.get_features_and_target()
        cat_cols, num_cols = data_loader.get_feature_columns()
        
        preprocessor = DataPreprocessor()
        preprocessor.build_processor(num_cols, cat_cols)
        X_transformed = preprocessor.fit_transform(X)
        
        # Step 4: Train Model
        logger.info("\n[Step 4/5] Training model...")
        model = ChurnModel()
        cv_results = model.train(X_transformed, y)
        
        # Log training results
        logger.info("\nTraining Results:")
        logger.info(f"  - Number of folds: {len(cv_results['test_score'])}")
        logger.info(f"  - Fold scores: {[f'{score:.4f}' for score in cv_results['test_score']]}")
        logger.info(f"  - Mean score: {sum(cv_results['test_score']) / len(cv_results['test_score']):.4f}")
        
        # Step 5: Save Model and Preprocessor
        logger.info("\n[Step 5/5] Saving model and preprocessor...")
        model_path = model.save_model("churn_model.pkl")
        
        # Save preprocessor
        preprocessor_path = os.path.join(MODEL_DIR, "preprocessor.pkl")
        joblib.dump(preprocessor.get_processor(), preprocessor_path)
        logger.info(f"Preprocessor saved to: {preprocessor_path}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Training Pipeline Completed Successfully!")
        logger.info("=" * 60)
        logger.info(f"\nArtifacts saved to: {MODEL_DIR}")
        
    except Exception as e:
        logger.error(f"\n{'=' * 60}")
        logger.error("Training Pipeline Failed!")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    train_pipeline()
