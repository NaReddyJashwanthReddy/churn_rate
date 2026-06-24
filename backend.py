"""
Backend API for churn prediction — extended with CSV-based endpoints for the dashboard frontend.

This builds directly on top of the PredictionService class you provided. Three things were
added so the frontend has something to call:

    POST /predict-demo     -> runs predictions on the saved demo/sample CSV (TEST_CSV_FILE)
    POST /predict-upload    -> saves an uploaded CSV into the data directory, then predicts on it
    GET  /feature-importance -> ranks features by importance from the trained model

ASSUMPTIONS YOU SHOULD VERIFY AGAINST YOUR ACTUAL CODEBASE
-----------------------------------------------------------
1. `src.config` is assumed to also expose `TEST_CSV_FILE` (path to your demo/sample CSV) and
   `DATA_DIR` (folder where uploaded CSVs should be saved). If those names don't exist in your
   config.py, the fallbacks below kick in (data/test_customers.csv, ./data) — update as needed.
2. `service.predictor.predict_batch(...)` is assumed to return a DataFrame with a probability
   column and/or a flag column, but the exact column names depend on your ChurnPredictor
   implementation (which wasn't included). `_normalize_prediction()` below tries several common
   names (churn_probability/probability/score, churn_flag/prediction/is_churn/churn) and falls
   back to deriving the flag from probability + threshold. If your real column names differ,
   add them to the `prob_keys` / `flag_keys` lists.
3. Feature importance assumes a scikit-learn-style model exposing `feature_importances_`
   (tree models) or `coef_` (linear models). If your model wraps something else, adjust
   `_get_feature_importance()`.
4. CORS is opened to "*" so the static frontend (opened from a different origin/port, or as a
   local file) can call this API. Tighten `allow_origins` before deploying anywhere real.

Run with:
    pip install fastapi uvicorn pandas python-multipart joblib
    uvicorn app:app --reload --port 8000
"""

from typing import Dict, List, Optional
import os
import shutil
from datetime import datetime

import joblib
import pandas as pd

from src.predictor import ChurnPredictor
from utils.logger import get_logger
from src.config import MODEL_DIR

logger = get_logger(__name__)

# --- config with graceful fallbacks (see assumption #1 above) ---
try:
    from src.config import TEST_CSV_FILE, DATA_DIR
except ImportError:
    TEST_CSV_FILE = os.path.join("data", "churn_test_data.csv")
    DATA_DIR = "data"
    logger.warning(
        "TEST_CSV_FILE / DATA_DIR not found in src.config — using fallback paths "
        f"({TEST_CSV_FILE}, {DATA_DIR}). Update src/config.py and re-import to fix."
    )

os.makedirs(DATA_DIR, exist_ok=True)

EXPECTED_FEATURES = [
    "plan_type",
    "tenure_days",
    "watch_hours_30d",
    "login_count_30d",
    "days_since_last_login",
    "support_ticket_count",
    "payment_failure_count",
    "monthly_revenue",
]


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

        self.model = joblib.load(model_path)
        processor = joblib.load(preprocessor_path)

        from src.preprocessor import DataPreprocessor
        self.preprocessor = DataPreprocessor()
        self.preprocessor.processor = processor

        self.predictor = ChurnPredictor(self.model, self.preprocessor)

        logger.info("Prediction service initialized successfully")

    def predict_customer_churn(self, customer_data: Dict, threshold: float = 0.5) -> Dict:
        """Predict churn for a single customer."""
        return self.predictor.predict_single(customer_data, threshold=threshold)

    def predict_customers_batch(self, customers_data: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """Predict churn for multiple customers."""
        results_df = self.predictor.predict_batch(
            customers_data, threshold=threshold, return_probabilities=True
        )
        return results_df.to_dict("records")


# --- helpers used by the new CSV-based endpoints ---

def _normalize_prediction(record: Dict, threshold: float) -> Dict:
    """Map whatever key names ChurnPredictor used onto churn_probability / churn_flag."""
    prob_keys = ["churn_probability", "probability", "churn_prob", "score"]
    flag_keys = ["churn_flag", "prediction", "is_churn", "churn"]

    prob = next((record[k] for k in prob_keys if k in record and record[k] is not None), None)
    flag = next((record[k] for k in flag_keys if k in record and record[k] is not None), None)

    if flag is None and prob is not None:
        flag = prob >= threshold

    record["churn_probability"] = float(prob) if prob is not None else None
    record["churn_flag"] = bool(flag) if flag is not None else None
    return record


def _get_feature_importance(top_n: int = 10) -> List[Dict]:
    """Rank features by importance from the trained model. Returns [] if unsupported."""
    try:
        model = service.model

        try:
            feature_names = list(service.preprocessor.processor.get_feature_names_out())
        except Exception:
            feature_names = EXPECTED_FEATURES

        if hasattr(model, "feature_importances_"):
            importances = list(model.feature_importances_)
        elif hasattr(model, "coef_"):
            importances = [abs(v) for v in model.coef_.flatten()]
        else:
            logger.warning("Model exposes neither feature_importances_ nor coef_; skipping ranking.")
            return []

        pairs = list(zip(feature_names, importances))
        pairs.sort(key=lambda x: x[1], reverse=True)
        total = sum(v for _, v in pairs) or 1

        return [
            {
                "rank": i + 1,
                "feature": name,
                "importance": float(val),
                "importance_pct": round(float(val) / total * 100, 1),
            }
            for i, (name, val) in enumerate(pairs[:top_n])
        ]
    except Exception as e:
        logger.warning(f"Could not compute feature importance: {e}")
        return []


def _predict_dataframe(df: pd.DataFrame, threshold: float = 0.5) -> Dict:
    """Run predictions on a dataframe of customers and build the full dashboard payload."""
    missing = [c for c in EXPECTED_FEATURES if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {missing}")

    df = df.reset_index(drop=True).copy()
    df = df.where(pd.notnull(df), None)  # avoid NaN leaking into JSON

    if "customer_id" not in df.columns:
        df["customer_id"] = [f"CUST-{i + 1:04d}" for i in range(len(df))]

    records = df[EXPECTED_FEATURES].to_dict("records")

    try:
        results_df = service.predictor.predict_batch(
            records, threshold=threshold, return_probabilities=True
        ).reset_index(drop=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    extra_cols = [c for c in results_df.columns if c not in df.columns]
    combined = pd.concat([df, results_df[extra_cols]], axis=1)

    predictions = [_normalize_prediction(row, threshold) for row in combined.to_dict("records")]

    churn_count = sum(1 for p in predictions if p["churn_flag"])
    total = len(predictions)

    return {
        "summary": {
            "total": total,
            "churn": churn_count,
            "retained": total - churn_count,
            "churn_rate": round(churn_count / total * 100, 1) if total else 0,
        },
        "feature_importance": _get_feature_importance(),
        "predictions": predictions,
    }


# --- FastAPI app ---

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(title="Churn Prediction API", version="1.1.0")
    service = PredictionService()

    # Allow the dashboard frontend (different origin/port, or a local file) to call this API.
    # Tighten allow_origins to your actual frontend URL before deploying anywhere real.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.post("/predict")
    def predict_churn(customer: CustomerData, threshold: float = 0.5):
        """Predict churn for a single customer."""
        try:
            return service.predict_customer_churn(customer.model_dump(), threshold=threshold)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/predict-batch")
    def predict_batch(request: BatchPredictionRequest):
        """Predict churn for multiple customers."""
        try:
            results = service.predict_customers_batch(
                [c.model_dump() for c in request.customers], threshold=request.threshold
            )
            return {"predictions": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ----- NEW: endpoints the dashboard frontend calls -----

    @app.post("/predict-demo")
    def predict_demo(threshold: float = 0.5):
        """Run predictions on the saved demo/sample CSV (TEST_CSV_FILE)."""
        if not os.path.exists(TEST_CSV_FILE):
            raise HTTPException(status_code=404, detail=f"Demo CSV not found at {TEST_CSV_FILE}")
        df = pd.read_csv(TEST_CSV_FILE)
        return _predict_dataframe(df, threshold)

    @app.post("/predict-upload")
    def predict_upload(file: UploadFile = File(...), threshold: float = Form(0.5)):
        """Save an uploaded CSV into the data directory, then run predictions on it."""
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only .csv files are supported")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_name = f"{timestamp}_{file.filename}"
        saved_path = os.path.join(DATA_DIR, saved_name)

        with open(saved_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            df = pd.read_csv(saved_path)
            result = _predict_dataframe(df, threshold)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")

        result["saved_as"] = saved_path
        return result

    @app.get("/feature-importance")
    def feature_importance(top_n: int = 10):
        """Standalone feature-importance ranking, in case the frontend wants to refresh it alone."""
        return {"feature_importance": _get_feature_importance(top_n)}

except ImportError:
    logger.warning("FastAPI not installed. Skipping FastAPI app creation.")

if __name__ == "__main__":
    pass
