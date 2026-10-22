"""Workload Preprocessor and Feature Engineering Pipeline.

Provides:
- Cyclical temporal embeddings (sin/cos of hour-of-day and day-of-week)
- Multi-step autoregressive lag features (t-1, t-2, t-3, t-6)
- Rolling historical statistics (mean and std over 3 and 6 steps)
- Strict chronological train/test splitting to prevent future lookahead leakage
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd


# Core feature columns used for modeling
FEATURE_TARGETS = ["cpu_usage", "memory_usage"]
AUXILIARY_METRICS = ["request_count", "response_time"]
ALL_METRICS = FEATURE_TARGETS + AUXILIARY_METRICS

DEFAULT_LAGS = [1, 2, 3, 6]
DEFAULT_WINDOWS = [3, 6]


def create_features(
    df: pd.DataFrame,
    metrics: Optional[List[str]] = None,
    lags: Optional[List[int]] = None,
    windows: Optional[List[int]] = None,
    drop_na: bool = True,
) -> pd.DataFrame:
    """Transform raw cloud telemetry into an engineered feature matrix.

    Args:
        df: Input DataFrame containing 'timestamp' and metric columns.
        metrics: List of metrics to compute lags/rolling features for (default: ALL_METRICS).
        lags: Time steps to lag back (default: [1, 2, 3, 6]).
        windows: Rolling window sizes in steps (default: [3, 6]).
        drop_na: Whether to drop initial rows with NaN values resulting from lags.

    Returns:
        Engineered pd.DataFrame sorted chronologically with added feature columns.
    """
    if metrics is None:
        metrics = [m for m in ALL_METRICS if m in df.columns]
    if lags is None:
        lags = DEFAULT_LAGS
    if windows is None:
        windows = DEFAULT_WINDOWS

    data = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(data["timestamp"]):
        data["timestamp"] = pd.to_datetime(data["timestamp"])

    data = data.sort_values("timestamp").reset_index(drop=True)

    # 1. Cyclical Time Features
    hour_float = data["timestamp"].dt.hour + (data["timestamp"].dt.minute / 60.0)
    data["hour_sin"] = np.sin(2.0 * np.pi * hour_float / 24.0)
    data["hour_cos"] = np.cos(2.0 * np.pi * hour_float / 24.0)

    day_of_week = data["timestamp"].dt.dayofweek
    data["dow_sin"] = np.sin(2.0 * np.pi * day_of_week / 7.0)
    data["dow_cos"] = np.cos(2.0 * np.pi * day_of_week / 7.0)

    # 2. Historical Lag Features (autoregressive)
    for metric in metrics:
        for lag in lags:
            data[f"{metric}_lag_{lag}"] = data[metric].shift(lag)

    # 3. Rolling Window Statistics (strictly shifted by 1 to prevent target leakage)
    for metric in metrics:
        shifted = data[metric].shift(1)
        for w in windows:
            data[f"{metric}_roll_mean_{w}"] = shifted.rolling(window=w).mean()
            data[f"{metric}_roll_std_{w}"] = shifted.rolling(window=w).std().fillna(0.0)

    if drop_na:
        data = data.dropna().reset_index(drop=True)

    return data


def chronological_train_test_split(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Perform a strict forward-in-time chronological train/test split.

    Guarantees no random shuffling, ensuring test data strictly succeeds train data.

    Args:
        df: Input DataFrame with 'timestamp' column.
        train_ratio: Ratio of data allocated to training (default: 0.8).

    Returns:
        Tuple of (train_df, test_df).
    """
    if not (0.0 < train_ratio < 1.0):
        raise ValueError("train_ratio must be strictly between 0.0 and 1.0")

    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    split_index = int(len(df_sorted) * train_ratio)

    train_df = df_sorted.iloc[:split_index].copy().reset_index(drop=True)
    test_df = df_sorted.iloc[split_index:].copy().reset_index(drop=True)

    # Verify absence of lookahead leakage
    if len(train_df) > 0 and len(test_df) > 0:
        assert train_df["timestamp"].max() < test_df["timestamp"].min(), (
            "Data leakage detected! Training timestamps overlap with test timestamps."
        )

    return train_df, test_df


def extract_features_and_targets(
    df: pd.DataFrame,
    target_columns: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """Separate input features from target columns and metadata.

    Args:
        df: Engineered DataFrame from create_features.
        target_columns: Target columns to predict (default: ['cpu_usage', 'memory_usage']).

    Returns:
        Tuple of (X, y, feature_column_names)
    """
    if target_columns is None:
        target_columns = FEATURE_TARGETS

    exclude_cols = set(["timestamp"] + target_columns)
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    X = df[feature_cols].copy()
    y = df[target_columns].copy()

    return X, y, feature_cols
