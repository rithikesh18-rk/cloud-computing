"""
Cloud-Based AQI Predictor - Request & Response Pydantic Schemas
"""

from pydantic import BaseModel, Field


class AQIPredictRequest(BaseModel):
    """Input payload schema for AQI prediction."""
    pm25: float = Field(
        ...,
        gt=0,
        description="Particulate Matter 2.5 concentration in ug/m3",
        examples=[45.5]
    )
    pm10: float = Field(
        ...,
        gt=0,
        description="Particulate Matter 10 concentration in ug/m3",
        examples=[85.0]
    )
    no2: float = Field(
        ...,
        gt=0,
        description="Nitrogen Dioxide concentration in ppb",
        examples=[32.4]
    )
    so2: float = Field(
        ...,
        gt=0,
        description="Sulfur Dioxide concentration in ppb",
        examples=[14.2]
    )
    co: float = Field(
        ...,
        gt=0,
        description="Carbon Monoxide concentration in ppm",
        examples=[1.8]
    )
    temperature: float = Field(
        ...,
        gt=0,
        description="Ambient Temperature in Celsius",
        examples=[28.5]
    )
    humidity: float = Field(
        ...,
        gt=0,
        description="Relative Humidity percentage",
        examples=[55.0]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "pm25": 45.5,
                "pm10": 85.0,
                "no2": 32.4,
                "so2": 14.2,
                "co": 1.8,
                "temperature": 28.5,
                "humidity": 55.0
            }
        }
    }


class AQIPredictResponse(BaseModel):
    """Output response schema for AQI prediction."""
    predicted_aqi: float = Field(
        ...,
        description="Predicted Air Quality Index value"
    )
    category: str = Field(
        ...,
        description="EPA AQI category"
    )
    advisory: str = Field(
        ...,
        description="Health advisory corresponding to the AQI category"
    )
    timestamp: str = Field(
        ...,
        description="Prediction timestamp (ISO 8601 formatted string)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "predicted_aqi": 125.4,
                "category": "Unhealthy for Sensitive Groups",
                "advisory": "Sensitive individuals should reduce exertion",
                "timestamp": "2026-08-27T19:58:00Z"
            }
        }
    }
