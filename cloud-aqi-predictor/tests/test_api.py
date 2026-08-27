"""
Automated Test Suite for Cloud-Based AQI Predictor API
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from src.app import app


def test_api():
    with TestClient(app) as client:
        # 1. Test Root Endpoint
        root_response = client.get("/")
        print("\n[TEST 1] Root Endpoint Response:")
        print(root_response.json())
        assert root_response.status_code == 200
        assert "docs_url" in root_response.json()

        # 2. Test Health Endpoint
        health_response = client.get("/health")
        print("\n[TEST 2] Health Endpoint Response:")
        print(health_response.json())
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
        assert health_response.json()["model_loaded"] is True

        # 3. Test Prediction Endpoint with Sample Payload
        sample_payload = {
            "pm25": 45.2,
            "pm10": 80.1,
            "no2": 22.0,
            "so2": 10.5,
            "co": 1.2,
            "temperature": 30.0,
            "humidity": 60.0
        }
        predict_response = client.post("/predict", json=sample_payload)
        print("\n[TEST 3] Predict Endpoint Response for Sample Payload:")
        print(predict_response.json())

        assert predict_response.status_code == 200
        data = predict_response.json()
        assert "predicted_aqi" in data
        assert isinstance(data["predicted_aqi"], (int, float))
        assert "category" in data
        assert "advisory" in data
        assert "timestamp" in data

        print("\n==========================================")
        print("          PREDICTION TEST RESULT          ")
        print("==========================================")
        print(f" Predicted AQI : {data['predicted_aqi']}")
        print(f" Category      : {data['category']}")
        print(f" Advisory      : {data['advisory']}")
        print(f" Timestamp     : {data['timestamp']}")
        print("==========================================")


if __name__ == "__main__":
    test_api()
