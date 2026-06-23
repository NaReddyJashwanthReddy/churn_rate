# Churn Rate Prediction - Modular Production Code

This directory contains production-level modular Python code for customer churn prediction.

## Project Structure

```
src/
├── __init__.py              # Package initialization
├── config.py                # Configuration constants
├── data_loader.py          # Data loading and validation
├── preprocessor.py         # Feature preprocessing and transformation
├── model.py                # Model training and management
├── predictor.py            # Prediction interface (backend-ready)
├── train.py                # Training orchestration script
└── backend_api.py          # Backend API integration example
```

## Modules Overview

### 1. **config.py**
- Centralized configuration management
- All constants in one place
- Easy to modify for different environments

### 2. **logger.py**
- Standardized logging across all modules
- Production-level logging configuration

### 3. **data_loader.py** (`DataLoader` class)
- Load CSV data
- Validate data quality
- Extract categorical and numeric columns
- Get features and target variables

### 4. **preprocessor.py** (`DataPreprocessor` class)
- Build column transformer
- Scale numeric features (MinMaxScaler)
- Encode categorical features (OneHotEncoder)
- Transform new data using fitted preprocessor

### 5. **model.py** (`ChurnModel` class)
- Train RandomForestClassifier with cross-validation
- Select best model from folds
- Save/load trained model
- Access cross-validation results

### 6. **predictor.py** (`ChurnPredictor` class)
- Make predictions on single customers
- Batch predictions for multiple customers
- Return prediction probabilities
- Configurable probability threshold
- **Backend-ready interface for API integration**

### 7. **train.py**
- Complete training pipeline orchestration
- Loads data, validates, preprocesses, trains, and saves model
- Can be run as main script: `python -m src.train`

### 8. **backend_api.py**
- `PredictionService` class for backend integration
- Example FastAPI implementation
- Ready for Flask, FastAPI, or Django integration

## Usage Examples

### Training the Model

```python
from src.train import train_pipeline

# Run complete training pipeline
train_pipeline()
```

Or from command line:
```bash
python -m src.train
```

### Using the Predictor (Backend)

```python
from src.backend_api import PredictionService

# Initialize service
service = PredictionService()

# Predict for single customer
customer = {
    'plan_type': 'Premium',
    'tenure_days': 365,
    'watch_hours_30d': 50,
    'login_count_30d': 25,
    'days_since_last_login': 2,
    'support_ticket_count': 1,
    'payment_failure_count': 0,
    'monthly_revenue': 15
}

result = service.predict_customer_churn(customer)
# Output: {
#     'churn_prediction': 0,
#     'churn_probability': 0.25,
#     'retention_probability': 0.75,
#     'threshold_used': 0.5
# }

# Batch predictions
customers = [customer1, customer2, customer3]
results = service.predict_customers_batch(customers)
```

### Direct Module Usage

```python
from src.data_loader import DataLoader
from src.preprocessor import DataPreprocessor
from src.model import ChurnModel
from src.predictor import ChurnPredictor

# Load and prepare data
loader = DataLoader()
df = loader.load_data()
loader.validate_data()
X, y = loader.get_features_and_target()
cat_cols, num_cols = loader.get_feature_columns()

# Preprocess
preprocessor = DataPreprocessor()
preprocessor.build_processor(num_cols, cat_cols)
X_transformed = preprocessor.fit_transform(X)

# Train
model_trainer = ChurnModel()
model_trainer.train(X_transformed, y)
trained_model = model_trainer.get_model()

# Predict
predictor = ChurnPredictor(trained_model, preprocessor)
predictions = predictor.predict(X)
```

## Features

✅ **Modular Design** - Each component is independent and reusable
✅ **Production-Ready** - Type hints, error handling, logging
✅ **Documented** - Comprehensive docstrings for all classes and methods
✅ **Backend-Friendly** - Easy integration with API frameworks
✅ **Configurable** - All settings in config.py
✅ **Tested** - Works with provided data structure
✅ **Scalable** - Batch prediction support
✅ **Persistent** - Model and preprocessor serialization

## Requirements

See `requirements.txt` for all dependencies.

Install with:
```bash
pip install -r requirements.txt
```

## Key Classes

| Class | Purpose |
|-------|---------|
| `DataLoader` | Load and validate data |
| `DataPreprocessor` | Transform features |
| `ChurnModel` | Train and manage models |
| `ChurnPredictor` | Make predictions |
| `PredictionService` | Backend integration wrapper |

## Production Considerations

- ✅ Error handling and validation throughout
- ✅ Comprehensive logging for debugging
- ✅ Configuration centralization for easy deployment
- ✅ Model and preprocessor serialization for production serving
- ✅ Type hints for better IDE support and type checking
- ✅ Batch processing for high-throughput scenarios
- ✅ Threshold customization for different business needs

## Integration with Web Frameworks

### FastAPI
```python
from src.backend_api import create_fastapi_app

app = create_fastapi_app()

# Run with: uvicorn src.backend_api:app --reload
```

### Flask
```python
from src.backend_api import PredictionService
from flask import Flask, request, jsonify

app = Flask(__name__)
service = PredictionService()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    result = service.predict_customer_churn(data)
    return jsonify(result)
```

## Notes

- The preprocessor must be fitted on training data before use
- Model selection is based on F1 score from cross-validation
- Probability threshold can be adjusted based on business requirements
- All data paths are relative to project root for flexibility
