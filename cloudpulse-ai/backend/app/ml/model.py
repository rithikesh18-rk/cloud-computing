"""Machine Learning Forecasting Models for CloudPulse AI.

Provides:
- RandomForestRegressor forecasting for CPU and Memory workloads
- DummyRegressor persistence baseline model for evaluation comparisons
- Test-set evaluation metrics (MAE and RMSE)
- Multi-step recursive autoregressive forward forecasting for arbitrary horizons (3, 6, 12 steps)
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.dummy import DummyRegressor as SklearnDummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.ml.preprocessor import (
    create_features,
    extract_features_and_targets,
    FEATURE_TARGETS,
)


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Root Mean Squared Error across true and predicted arrays."""
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


class DummyRegressor(BaseEstimator, RegressorMixin):
    """Persistence and baseline dummy regressor for time-series forecasting.

    Supports:
    - strategy='last': True time-series persistence model. Uses target_lag_1 if present in X,
      or falls back to the final observed value from the training target.
    - Standard scikit-learn strategies: 'mean', 'median', 'quantile', 'constant'.
    """

    def __init__(
        self,
        strategy: str = "last",
        target_name: Optional[str] = None,
        constant: Optional[float] = None,
        quantile: Optional[float] = None,
    ):
        self.strategy = strategy
        self.target_name = target_name
        self.constant = constant
        self.quantile = quantile
        self._last_val: float = 0.0
        self._sklearn_dummy: Optional[SklearnDummyRegressor] = None

    def fit(self, X, y):
        """Fit baseline on training targets."""
        y_arr = np.asarray(y).ravel()
        if len(y_arr) > 0:
            self._last_val = float(y_arr[-1])

        if self.strategy != "last":
            self._sklearn_dummy = SklearnDummyRegressor(
                strategy=self.strategy,
                constant=self.constant,
                quantile=self.quantile,
            )
            self._sklearn_dummy.fit(X, y)

        return self

    def predict(self, X) -> np.ndarray:
        """Predict target values."""
        if self.strategy != "last":
            if self._sklearn_dummy is None:
                raise RuntimeError("Baseline model has not been fitted.")
            return self._sklearn_dummy.predict(X)

        n_samples = len(X)
        if isinstance(X, pd.DataFrame) and self.target_name:
            lag_col = f"{self.target_name}_lag_1"
            if lag_col in X.columns:
                return X[lag_col].to_numpy(dtype=float)

        return np.full(n_samples, self._last_val, dtype=float)


class WorkloadForecaster:
    """Predictive forecasting system for CPU and Memory workloads."""

    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int = 42,
    ):
        self.random_state = random_state
        self.n_estimators = n_estimators

        # Core Random Forest Models
        self.cpu_rf = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
        )
        self.mem_rf = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
        )

        # Baseline Persistence Models
        self.cpu_baseline = DummyRegressor(strategy="last", target_name="cpu_usage")
        self.mem_baseline = DummyRegressor(strategy="last", target_name="memory_usage")

        self.feature_columns: List[str] = []
        self.is_fitted: bool = False

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
    ) -> "WorkloadForecaster":
        """Train Random Forest and persistence baselines for both CPU and Memory.

        Args:
            X_train: Engineered feature DataFrame.
            y_train: DataFrame containing 'cpu_usage' and 'memory_usage'.

        Returns:
            Self instance.
        """
        self.feature_columns = list(X_train.columns)

        # Train CPU models
        self.cpu_rf.fit(X_train, y_train["cpu_usage"])
        self.cpu_baseline.fit(X_train, y_train["cpu_usage"])

        # Train Memory models
        self.mem_rf.fit(X_train, y_train["memory_usage"])
        self.mem_baseline.fit(X_train, y_train["memory_usage"])

        self.is_fitted = True
        return self

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.DataFrame,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Compute test-set MAE and RMSE metrics for Random Forest and Baseline.

        Returns structured metrics dictionary:
        {
            "cpu": {
                "random_forest": {"mae": float, "rmse": float},
                "baseline": {"mae": float, "rmse": float}
            },
            "memory": {
                "random_forest": {"mae": float, "rmse": float},
                "baseline": {"mae": float, "rmse": float}
            }
        }
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot evaluate model before fitting.")

        # Predictions
        cpu_pred_rf = self.cpu_rf.predict(X_test[self.feature_columns])
        cpu_pred_base = self.cpu_baseline.predict(X_test)

        mem_pred_rf = self.mem_rf.predict(X_test[self.feature_columns])
        mem_pred_base = self.mem_baseline.predict(X_test)

        cpu_true = y_test["cpu_usage"].to_numpy()
        mem_true = y_test["memory_usage"].to_numpy()

        metrics = {
            "cpu": {
                "random_forest": {
                    "mae": float(round(mean_absolute_error(cpu_true, cpu_pred_rf), 4)),
                    "rmse": float(round(calculate_rmse(cpu_true, cpu_pred_rf), 4)),
                },
                "baseline": {
                    "mae": float(round(mean_absolute_error(cpu_true, cpu_pred_base), 4)),
                    "rmse": float(round(calculate_rmse(cpu_true, cpu_pred_base), 4)),
                },
            },
            "memory": {
                "random_forest": {
                    "mae": float(round(mean_absolute_error(mem_true, mem_pred_rf), 4)),
                    "rmse": float(round(calculate_rmse(mem_true, mem_pred_rf), 4)),
                },
                "baseline": {
                    "mae": float(round(mean_absolute_error(mem_true, mem_pred_base), 4)),
                    "rmse": float(round(calculate_rmse(mem_true, mem_pred_base), 4)),
                },
            },
        }

        return metrics

    def predict_multi_step(
        self,
        history_df: pd.DataFrame,
        horizon_steps: int = 12,
        interval_minutes: int = 5,
    ) -> pd.DataFrame:
        """Autoregressive multi-step forward inference for configurable horizons.

        Args:
            history_df: Recent raw telemetry DataFrame with timestamp and metric columns.
                        Must contain at least 7 preceding records to build lag/rolling features.
            horizon_steps: Number of forward prediction steps (e.g., 3, 6, 12).
            interval_minutes: Step duration in minutes (default: 5).

        Returns:
            DataFrame containing forecasted timestamps, predicted cpu_usage, and memory_usage.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before generating forecasts.")

        if len(history_df) < 7:
            raise ValueError("history_df must contain at least 7 rows for lag/rolling windows.")

        # Work on a copy of history records
        working_data = history_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(working_data["timestamp"]):
            working_data["timestamp"] = pd.to_datetime(working_data["timestamp"])
        working_data = working_data.sort_values("timestamp").reset_index(drop=True)

        forecast_rows: List[Dict[str, Any]] = []

        for step in range(1, horizon_steps + 1):
            # 1. Feature engineering on current known + forecasted history
            feature_df = create_features(working_data, drop_na=True)
            if feature_df.empty:
                raise ValueError("Insufficient history to calculate feature window.")

            # Extract the last row representing t (predicting t+1)
            last_feature_row = feature_df.iloc[[-1]]
            X_step = last_feature_row[self.feature_columns]

            # 2. Predict next step
            pred_cpu = float(np.clip(self.cpu_rf.predict(X_step)[0], 0.0, 100.0))
            pred_mem = float(np.clip(self.mem_rf.predict(X_step)[0], 0.0, 100.0))

            # Timestamp for next step
            last_ts = working_data["timestamp"].iloc[-1]
            next_ts = last_ts + pd.Timedelta(minutes=interval_minutes)

            # Estimate auxiliary metrics from previous trend for feature feedback
            last_req = working_data["request_count"].iloc[-1] if "request_count" in working_data else 500
            last_resp = working_data["response_time"].iloc[-1] if "response_time" in working_data else 30.0

            # Store forecast result
            forecast_rows.append(
                {
                    "step": step,
                    "timestamp": next_ts,
                    "cpu_usage": round(pred_cpu, 2),
                    "memory_usage": round(pred_mem, 2),
                }
            )

            # Append new predicted observation to working_data for subsequent lags
            next_record = pd.DataFrame(
                [
                    {
                        "timestamp": next_ts,
                        "cpu_usage": pred_cpu,
                        "memory_usage": pred_mem,
                        "request_count": last_req,
                        "response_time": last_resp,
                    }
                ]
            )
            working_data = pd.concat([working_data, next_record], ignore_index=True)

        return pd.DataFrame(forecast_rows)
