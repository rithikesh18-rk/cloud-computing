"""API Integration Tests for CloudPulse AI REST Endpoints.

Tests:
1. System Health Check
2. Dataset preview, sample CSV download, and upload validation
3. Forecast model training and forward multi-step prediction
4. Simulation comparative run, history retrieval, and CSV timeline export
5. System settings fetch and boundary update
"""

import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.schemas import SystemSettings


@pytest.fixture(scope="module")
def client():
    """Create a test client with an initialized database."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed settings if absent
        if not db.query(SystemSettings).filter(SystemSettings.id == 1).first():
            db.add(SystemSettings(id=1))
            db.commit()
    finally:
        db.close()

    from pathlib import Path
    active_csv = Path(__file__).resolve().parents[1] / "data" / "active_workload.csv"
    if active_csv.exists():
        active_csv.unlink()

    with TestClient(app) as test_client:
        yield test_client

    if active_csv.exists():
        active_csv.unlink()


def test_health_check(client):
    """Verify health check endpoint returns 200 OK and timestamp."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["service"] == "CloudPulse AI"


def test_dataset_sample_download(client):
    """Verify pre-generated sample dataset is downloadable as CSV."""
    response = client.get("/api/dataset/sample")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    assert "timestamp,cpu_usage,memory_usage,request_count,response_time" in content


def test_dataset_preview(client):
    """Verify dataset preview returns valid metadata and top 50 rows."""
    response = client.get("/api/dataset/preview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] > 0
    assert "time_bounds" in data
    assert "null_counts" in data
    assert len(data["rows"]) <= 50

    sample_row = data["rows"][0]
    for key in ["timestamp", "cpu_usage", "memory_usage", "request_count", "response_time"]:
        assert key in sample_row


def test_dataset_upload_valid_csv(client):
    """Verify uploading a compliant CSV succeeds and returns record counts."""
    valid_csv = (
        "timestamp,cpu_usage,memory_usage,request_count,response_time\n"
        "2026-03-01 00:00:00,20.5,45.0,200,25.0\n"
        "2026-03-01 00:05:00,25.0,46.2,250,26.5\n"
        "2026-03-01 00:10:00,28.2,47.1,300,28.0\n"
    )
    files = {"file": ("test_upload.csv", io.BytesIO(valid_csv.encode("utf-8")), "text/csv")}
    response = client.post("/api/dataset/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["valid_rows"] == 3


def test_dataset_upload_invalid_headers(client):
    """Verify upload with missing required columns is rejected with 422."""
    bad_csv = "time,cpu,mem\n1,2,3\n"
    files = {"file": ("invalid.csv", io.BytesIO(bad_csv.encode("utf-8")), "text/csv")}
    response = client.post("/api/dataset/upload", files=files)
    assert response.status_code == 422
    assert "validation failed" in response.json()["detail"].lower()


def test_forecast_train_model(client):
    """Verify model training endpoint returns MAE and RMSE for RF and Baseline."""
    payload = {"n_estimators": 30, "random_state": 42}
    response = client.post("/api/forecast/train", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "metrics" in data
    assert "cpu" in data["metrics"] and "memory" in data["metrics"]

    for resource in ["cpu", "memory"]:
        for model in ["random_forest", "baseline"]:
            mae = data["metrics"][resource][model]["mae"]
            rmse = data["metrics"][resource][model]["rmse"]
            assert isinstance(mae, float) and mae >= 0.0
            assert isinstance(rmse, float) and rmse >= 0.0


def test_forecast_predict_horizon(client):
    """Verify forward prediction endpoint returns horizon forecasts."""
    payload = {"horizon_steps": 6}
    response = client.post("/api/forecast/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["horizon_steps"] == 6
    assert len(data["forecasts"]) == 6
    for i, step in enumerate(data["forecasts"]):
        assert step["step"] == i + 1
        assert 0.0 <= step["cpu_usage"] <= 100.0
        assert 0.0 <= step["memory_usage"] <= 100.0


def test_simulation_comparative_run_and_history(client):
    """Verify comparative simulation run executes, records to SQLite, and updates history."""
    payload = {
        "profile": "Spike",
        "steps": 40,
        "initial_instances": 2,
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    sim_id = data["id"]
    assert sim_id > 0
    assert "reactive" in data and "predictive" in data
    assert len(data["timeline"]) == 40
    assert "cost_savings_pct" in data
    assert "sla_reduction_pct" in data

    # Verify history listing includes newly created simulation run
    hist_response = client.get("/api/simulation/history")
    assert hist_response.status_code == 200
    history = hist_response.json()
    assert len(history) > 0
    assert any(item["id"] == sim_id for item in history)

    # Verify CSV export for this run
    export_response = client.get(f"/api/simulation/export/{sim_id}")
    assert export_response.status_code == 200
    assert "text/csv" in export_response.headers.get("content-type", "")
    assert f"attachment; filename=cloudpulse_simulation_{sim_id}_spike.csv" in export_response.headers.get("content-disposition", "")
    csv_text = export_response.text
    assert "tick,demand_rps,reactive_instances,predictive_instances" in csv_text


def test_settings_get_and_update(client):
    """Verify reading and updating system configuration settings."""
    # 1. Fetch current settings
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    orig_settings = get_res.json()
    assert orig_settings["min_instances"] >= 1

    # 2. Update settings
    update_payload = {
        "min_instances": 3,
        "max_instances": 25,
        "cooldown_ticks": 4,
        "target_utilization": 0.75,
        "hourly_cost_per_node": 0.06,
    }
    put_res = client.put("/api/settings", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()

    assert updated["min_instances"] == 3
    assert updated["max_instances"] == 25
    assert updated["cooldown_ticks"] == 4
    assert updated["target_utilization"] == 0.75
    assert updated["hourly_cost_per_node"] == 0.06

    # 3. Test invalid min > max validation
    invalid_payload = {"min_instances": 30, "max_instances": 10}
    bad_res = client.put("/api/settings", json=invalid_payload)
    assert bad_res.status_code == 400
