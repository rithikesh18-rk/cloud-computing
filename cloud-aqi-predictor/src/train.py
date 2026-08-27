"""
Cloud-Based AQI Predictor - Model Training Script

This script handles:
1. Programmatic directory creation (data/ and models/).
2. Realistic synthetic dataset generation using EPA AQI breakpoints if dataset does not exist.
3. Loading and preprocessing data (handling missing values, train/test split).
4. Training an XGBoost Regressor model.
5. Evaluating model performance (RMSE, MAE, R2 score).
6. Serializing the trained model to disk using joblib.
"""

import os
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Base paths setup
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DATA_PATH = DATA_DIR / "aqi_dataset.csv"
MODEL_PATH = MODELS_DIR / "aqi_model.joblib"


def ensure_directories_exist():
    """Ensure data/ and models/ directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Verified directories: '{DATA_DIR}' and '{MODELS_DIR}'")


def calculate_sub_index(conc: float, breakpoints: list) -> float:
    """
    Calculate the sub-index for a single pollutant based on EPA piecewise linear formula:
    I = ((I_hi - I_lo) / (BP_hi - BP_lo)) * (Cp - BP_lo) + I_lo
    """
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if bp_lo <= conc <= bp_hi:
            return ((i_hi - i_lo) / (bp_hi - bp_lo)) * (conc - bp_lo) + i_lo
    # If above the maximum defined breakpoint, extrapolate linearly from top bucket
    bp_lo, bp_hi, i_lo, i_hi = breakpoints[-1]
    if conc > bp_hi:
        return ((i_hi - i_lo) / (bp_hi - bp_lo)) * (conc - bp_lo) + i_lo
    return 0.0


def calculate_epa_aqi(pm25: float, pm10: float, no2: float, so2: float, co: float) -> float:
    """Calculate the EPA AQI as the maximum of individual pollutant sub-indices."""
    # EPA Breakpoints: (BP_Low, BP_High, I_Low, I_High)
    pm25_bp = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.0, 301, 500)
    ]
    pm10_bp = [
        (0.0, 54.0, 0, 50),
        (55.0, 154.0, 51, 100),
        (155.0, 254.0, 101, 150),
        (255.0, 354.0, 151, 200),
        (355.0, 424.0, 201, 300),
        (425.0, 600.0, 301, 500)
    ]
    no2_bp = [
        (0.0, 53.0, 0, 50),
        (54.0, 100.0, 51, 100),
        (101.0, 360.0, 101, 150),
        (361.0, 649.0, 151, 200),
        (650.0, 1249.0, 201, 300),
        (1250.0, 2049.0, 301, 500)
    ]
    so2_bp = [
        (0.0, 35.0, 0, 50),
        (36.0, 75.0, 51, 100),
        (76.0, 185.0, 101, 150),
        (186.0, 304.0, 151, 200),
        (305.0, 604.0, 201, 300),
        (605.0, 1004.0, 301, 500)
    ]
    co_bp = [
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.0, 301, 500)
    ]

    i_pm25 = calculate_sub_index(pm25, pm25_bp)
    i_pm10 = calculate_sub_index(pm10, pm10_bp)
    i_no2 = calculate_sub_index(no2, no2_bp)
    i_so2 = calculate_sub_index(so2, so2_bp)
    i_co = calculate_sub_index(co, co_bp)

    return max(i_pm25, i_pm10, i_no2, i_so2, i_co)


def generate_synthetic_data(num_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic air quality dataset.
    Features:
    - PM2.5 (0 to 500 ug/m3)
    - PM10 (0 to 600 ug/m3)
    - NO2 (0 to 200 ppb)
    - SO2 (0 to 100 ppb)
    - CO (0 to 10 ppm)
    - Temperature (10 to 45 C)
    - Humidity (20 to 95 %)
    - AQI (computed via EPA standard breakpoints with realistic noise)
    """
    logger.info(f"Generating {num_samples} synthetic samples based on EPA standards...")
    np.random.seed(random_state)

    # Use gamma/beta distributions for realistic skewed air pollution data + some high extremes
    pm25 = np.random.uniform(0.0, 500.0, size=num_samples)
    pm10 = np.clip(pm25 * np.random.uniform(1.1, 1.8, size=num_samples), 0.0, 600.0)
    no2 = np.random.uniform(0.0, 200.0, size=num_samples)
    so2 = np.random.uniform(0.0, 100.0, size=num_samples)
    co = np.random.uniform(0.0, 10.0, size=num_samples)
    temperature = np.random.uniform(10.0, 45.0, size=num_samples)
    humidity = np.random.uniform(20.0, 95.0, size=num_samples)

    aqi_values = []
    for i in range(num_samples):
        base_aqi = calculate_epa_aqi(pm25[i], pm10[i], no2[i], so2[i], co[i])
        
        # Add slight environmental modulation (temperature & humidity) and random noise
        temp_mod = (temperature[i] - 25.0) * 0.15
        humidity_mod = (humidity[i] - 50.0) * 0.1
        noise = np.random.normal(0, 2.5)
        
        final_aqi = np.clip(base_aqi + temp_mod + humidity_mod + noise, 0.0, 500.0)
        aqi_values.append(round(final_aqi, 2))

    df = pd.DataFrame({
        "PM2.5": np.round(pm25, 2),
        "PM10": np.round(pm10, 2),
        "NO2": np.round(no2, 2),
        "SO2": np.round(so2, 2),
        "CO": np.round(co, 2),
        "Temperature": np.round(temperature, 2),
        "Humidity": np.round(humidity, 2),
        "AQI": aqi_values
    })

    df.to_csv(DATA_PATH, index=False)
    logger.info(f"Synthetic dataset saved to '{DATA_PATH}' (Shape: {df.shape})")
    return df


def load_and_preprocess_data() -> pd.DataFrame:
    """Load dataset from disk or create it if missing, and handle missing values."""
    if not DATA_PATH.exists():
        logger.warning(f"Dataset not found at '{DATA_PATH}'. Generating synthetic dataset...")
        df = generate_synthetic_data()
    else:
        logger.info(f"Loading existing dataset from '{DATA_PATH}'...")
        df = pd.read_csv(DATA_PATH)

    # Check for missing values
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        logger.warning(f"Found {missing_count} missing values. Imputing with median values...")
        df = df.fillna(df.median())
    else:
        logger.info("No missing values found in dataset.")

    return df


def train_and_evaluate_model():
    """Execute complete workflow: directory check, data prep, model training, evaluation, and saving."""
    ensure_directories_exist()
    
    # 1. Load Data
    df = load_and_preprocess_data()
    logger.info(f"Dataset summary:\n{df.describe().round(2)}")

    feature_cols = ["PM2.5", "PM10", "NO2", "SO2", "CO", "Temperature", "Humidity"]
    target_col = "AQI"

    X = df[feature_cols]
    y = df[target_col]

    # 2. Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    logger.info(f"Train set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    # 3. Model Training
    logger.info("Training XGBoost Regressor (n_estimators=150, learning_rate=0.05, max_depth=5)...")
    model = XGBRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    logger.info("Model training completed successfully.")

    # 4. Evaluation
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    logger.info("==========================================")
    logger.info("         MODEL EVALUATION METRICS         ")
    logger.info("==========================================")
    logger.info(f" Root Mean Squared Error (RMSE) : {rmse:.4f}")
    logger.info(f" Mean Absolute Error (MAE)      : {mae:.4f}")
    logger.info(f" R-squared Score (R2)           : {r2:.4f}")
    logger.info("==========================================")

    # 5. Save Model Artifact
    joblib.dump(model, MODEL_PATH)
    logger.info(f"Trained model artifact successfully saved to '{MODEL_PATH}'")


if __name__ == "__main__":
    logger.info("Starting Cloud-Based AQI Predictor training pipeline...")
    train_and_evaluate_model()
    logger.info("Training pipeline execution finished.")
