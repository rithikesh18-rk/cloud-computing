"""
Cloud-Based AQI Predictor - FastAPI REST API Application
"""

import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.schemas import AQIPredictRequest, AQIPredictResponse
from src.utils import get_aqi_category

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "aqi_model.joblib"

# Global model state dictionary
ml_models: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load and clean up ML model artifacts."""
    logger.info("Initializing application startup...")
    if not MODEL_PATH.exists():
        logger.error(f"Model file not found at '{MODEL_PATH}'")
        ml_models["aqi_model"] = None
    else:
        try:
            ml_models["aqi_model"] = joblib.load(MODEL_PATH)
            logger.info(f"Model successfully loaded from '{MODEL_PATH}'")
        except Exception as exc:
            logger.error(f"Failed to load model from '{MODEL_PATH}': {exc}")
            ml_models["aqi_model"] = None

    yield

    logger.info("Application shutdown: cleaning up resources...")
    ml_models.clear()


# Initialize FastAPI App
app = FastAPI(
    title="Cloud-Based AQI Predictor API",
    version="1.0.0",
    description="Scalable Cloud API for predicting Air Quality Index (AQI) with EPA health advisories.",
    lifespan=lifespan
)

# Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint providing service metadata and link to Swagger UI documentation."""
    return {
        "message": "Welcome to the Cloud-Based AQI Predictor API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify server status and model readiness."""
    is_model_loaded = ml_models.get("aqi_model") is not None
    current_time = datetime.now(timezone.utc).isoformat()

    return {
        "status": "healthy",
        "timestamp": current_time,
        "model_loaded": is_model_loaded
    }


@app.post(
    "/predict",
    response_model=AQIPredictResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"]
)
async def predict_aqi(payload: AQIPredictRequest):
    """
    Predict Air Quality Index (AQI) from environmental and pollutant measurements.
    """
    model = ml_models.get("aqi_model")
    if model is None:
        logger.error("Inference requested but AQI model is not loaded.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AQI model artifact is not loaded or missing. Please ensure models/aqi_model.joblib exists."
        )

    try:
        # Match the exact feature columns used during training
        input_data = pd.DataFrame([{
            "PM2.5": payload.pm25,
            "PM10": payload.pm10,
            "NO2": payload.no2,
            "SO2": payload.so2,
            "CO": payload.co,
            "Temperature": payload.temperature,
            "Humidity": payload.humidity
        }])

        # Perform inference
        raw_prediction = model.predict(input_data)[0]
        predicted_aqi = round(float(np.clip(raw_prediction, 0.0, 500.0)), 2)

        # Get EPA category and health advisory
        category, advisory = get_aqi_category(predicted_aqi)
        current_time = datetime.now(timezone.utc).isoformat()

        logger.info(
            f"Prediction completed: AQI={predicted_aqi}, Category='{category}' for payload: {payload.model_dump()}"
        )

        return AQIPredictResponse(
            predicted_aqi=predicted_aqi,
            category=category,
            advisory=advisory,
            timestamp=current_time
        )
    except Exception as exc:
        logger.error(f"Error during model prediction: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during prediction: {str(exc)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
