"""Model training and multi-step inference API routes for CloudPulse AI."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status
import pandas as pd

from app.models.schemas import (
    TrainModelRequest,
    TrainModelResponse,
    PredictRequest,
    PredictResponse,
    ForecastItem,
    ResourceMetrics,
    EvaluationMetrics,
)
from app.ml.model import WorkloadForecaster
from app.ml.preprocessor import (
    create_features,
    chronological_train_test_split,
    extract_features_and_targets,
)
from app.ml.generator import generate_synthetic_workload

router = APIRouter(prefix="/forecast", tags=["Forecasting"])

BASE_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SAMPLE_CSV_PATH = BASE_DATA_DIR / "sample_workload.csv"
ACTIVE_CSV_PATH = BASE_DATA_DIR / "active_workload.csv"

# Global cached forecaster in memory
GLOBAL_FORECASTER: Optional[WorkloadForecaster] = None


def get_dataset_df() -> pd.DataFrame:
    """Load current active or sample dataset, guaranteeing sufficient rows."""
    if ACTIVE_CSV_PATH.exists():
        try:
            active_df = pd.read_csv(ACTIVE_CSV_PATH)
            if len(active_df) >= 50:
                return active_df
        except Exception:
            pass

    if not SAMPLE_CSV_PATH.exists():
        generate_synthetic_workload(days=14, output_path=SAMPLE_CSV_PATH)

    return pd.read_csv(SAMPLE_CSV_PATH)



@router.post("/train", response_model=TrainModelResponse)
def train_forecaster(request: TrainModelRequest = TrainModelRequest()) -> TrainModelResponse:
    """Train Random Forest regression models and baseline persistence models on telemetry.

    Calculates and returns test-set MAE and RMSE metrics for both CPU and Memory.
    """
    global GLOBAL_FORECASTER

    raw_df = get_dataset_df()
    if len(raw_df) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset must contain at least 50 observations for model training.",
        )

    # 1. Feature Engineering
    featured_df = create_features(raw_df, drop_na=True)

    # 2. Chronological Split (Strict forward in time, 80% train / 20% test)
    train_df, test_df = chronological_train_test_split(featured_df, train_ratio=0.8)

    X_train, y_train, _ = extract_features_and_targets(train_df)
    X_test, y_test, _ = extract_features_and_targets(test_df)

    # 3. Model Training
    forecaster = WorkloadForecaster(
        n_estimators=request.n_estimators,
        random_state=request.random_state,
    )
    forecaster.fit(X_train, y_train)

    # 4. Evaluation Metrics
    raw_metrics = forecaster.evaluate(X_test, y_test)

    # Store active forecaster
    GLOBAL_FORECASTER = forecaster

    formatted_metrics = {
        "cpu": ResourceMetrics(
            random_forest=EvaluationMetrics(**raw_metrics["cpu"]["random_forest"]),
            baseline=EvaluationMetrics(**raw_metrics["cpu"]["baseline"]),
        ),
        "memory": ResourceMetrics(
            random_forest=EvaluationMetrics(**raw_metrics["memory"]["random_forest"]),
            baseline=EvaluationMetrics(**raw_metrics["memory"]["baseline"]),
        ),
    }

    return TrainModelResponse(
        message="Workload forecasting models successfully trained and evaluated.",
        trained_at=datetime.utcnow().isoformat() + "Z",
        train_samples=len(X_train),
        test_samples=len(X_test),
        metrics=formatted_metrics,
    )


@router.post("/predict", response_model=PredictResponse)
def generate_forecast(request: PredictRequest = PredictRequest()) -> PredictResponse:
    """Generate multi-step forward horizon forecast (e.g., 3, 6, 12 steps ahead)."""
    global GLOBAL_FORECASTER

    raw_df = get_dataset_df()
    if len(raw_df) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient dataset history to run forward forecasting.",
        )

    # Train model if not already trained
    if GLOBAL_FORECASTER is None or not GLOBAL_FORECASTER.is_fitted:
        featured_df = create_features(raw_df, drop_na=True)
        train_df, _ = chronological_train_test_split(featured_df, train_ratio=0.8)
        X_train, y_train, _ = extract_features_and_targets(train_df)
        GLOBAL_FORECASTER = WorkloadForecaster(n_estimators=50, random_state=42)
        GLOBAL_FORECASTER.fit(X_train, y_train)

    # Use the 30 most recent observations for rolling context
    recent_history = raw_df.iloc[-30:].copy()

    forecast_df = GLOBAL_FORECASTER.predict_multi_step(
        history_df=recent_history,
        horizon_steps=request.horizon_steps,
        interval_minutes=5,
    )

    items = [
        ForecastItem(
            step=int(row["step"]),
            timestamp=str(row["timestamp"]),
            cpu_usage=float(row["cpu_usage"]),
            memory_usage=float(row["memory_usage"]),
        )
        for _, row in forecast_df.iterrows()
    ]

    return PredictResponse(
        horizon_steps=request.horizon_steps,
        historical_context_steps=len(recent_history),
        forecasts=items,
    )
