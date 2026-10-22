"""SQLAlchemy ORM models and Pydantic v2 schemas for CloudPulse AI."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from app.database import Base


# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================

class SimulationRun(Base):
    """Database record of a simulated autoscaling experiment."""
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    workload_profile = Column(String(50), nullable=False)
    total_steps = Column(Integer, nullable=False)
    initial_instances = Column(Integer, nullable=False)

    # Comparative Metrics
    reactive_sla_violations = Column(Integer, default=0)
    predictive_sla_violations = Column(Integer, default=0)
    reactive_p95_latency = Column(Float, default=0.0)
    predictive_p95_latency = Column(Float, default=0.0)
    reactive_cost = Column(Float, default=0.0)
    predictive_cost = Column(Float, default=0.0)
    cost_savings_pct = Column(Float, default=0.0)

    # Serialized JSON blobs for detailed playback and CSV export
    summary_json = Column(Text, nullable=False)
    timeline_json = Column(Text, nullable=False)


class SystemSettings(Base):
    """System-wide autoscaling parameters and cost thresholds."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, default=1)
    min_instances = Column(Integer, default=2)
    max_instances = Column(Integer, default=20)
    cooldown_ticks = Column(Integer, default=3)
    target_utilization = Column(Float, default=0.70)
    capacity_per_instance_rps = Column(Float, default=200.0)
    hourly_cost_per_node = Column(Float, default=0.05)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Pydantic Schemas (v2)
# ============================================================================

class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str
    service: str = "CloudPulse AI"


# Dataset Schemas
class DatasetRow(BaseModel):
    timestamp: str
    cpu_usage: float
    memory_usage: float
    request_count: int
    response_time: float


class DatasetPreviewResponse(BaseModel):
    total_rows: int
    time_bounds: Dict[str, str]
    null_counts: Dict[str, int]
    rows: List[DatasetRow]


class DatasetUploadResponse(BaseModel):
    message: str
    total_rows: int
    valid_rows: int
    time_bounds: Dict[str, str]


# Forecasting Schemas
class TrainModelRequest(BaseModel):
    n_estimators: int = Field(default=100, ge=10, le=300)
    random_state: int = Field(default=42)


class EvaluationMetrics(BaseModel):
    mae: float
    rmse: float


class ResourceMetrics(BaseModel):
    random_forest: EvaluationMetrics
    baseline: EvaluationMetrics


class TrainModelResponse(BaseModel):
    message: str
    trained_at: str
    train_samples: int
    test_samples: int
    metrics: Dict[str, ResourceMetrics]


class PredictRequest(BaseModel):
    horizon_steps: int = Field(default=6, ge=1, le=24, description="Horizon steps (e.g., 3, 6, 12)")


class ForecastItem(BaseModel):
    step: int
    timestamp: str
    cpu_usage: float
    memory_usage: float


class PredictResponse(BaseModel):
    horizon_steps: int
    historical_context_steps: int
    forecasts: List[ForecastItem]


# Simulation Schemas
class SimulationRunRequest(BaseModel):
    profile: str = Field(default="Spike", description="Profile: Normal, Spike, Ramp-up, Drop")
    steps: int = Field(default=50, ge=10, le=200)
    initial_instances: int = Field(default=2, ge=1, le=20)
    custom_demand: Optional[List[float]] = None


class PolicySimulationSummary(BaseModel):
    policy_name: str
    total_ticks: int
    sla_violations_count: int
    sla_violation_rate_pct: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    avg_cpu_utilization_pct: float
    over_provisioned_node_hours: float
    under_provisioned_node_hours: float
    scale_up_actions: int
    scale_down_actions: int
    total_scaling_actions: int
    total_cost_usd: float


class SimulationComparisonResponse(BaseModel):
    id: int
    timestamp: str
    workload_profile: str
    total_steps: int
    reactive: PolicySimulationSummary
    predictive: PolicySimulationSummary
    cost_savings_pct: float
    sla_reduction_pct: float
    timeline: List[Dict[str, Any]]
    disclaimer: str


class SimulationHistoryItem(BaseModel):
    id: int
    timestamp: str
    workload_profile: str
    total_steps: int
    reactive_cost: float
    predictive_cost: float
    cost_savings_pct: float
    reactive_sla_violations: int
    predictive_sla_violations: int

    model_config = ConfigDict(from_attributes=True)


# Settings Schemas
class SettingsUpdate(BaseModel):
    min_instances: Optional[int] = Field(default=None, ge=1, le=50)
    max_instances: Optional[int] = Field(default=None, ge=1, le=100)
    cooldown_ticks: Optional[int] = Field(default=None, ge=0, le=20)
    target_utilization: Optional[float] = Field(default=None, ge=0.3, le=0.95)
    capacity_per_instance_rps: Optional[float] = Field(default=None, ge=10.0, le=5000.0)
    hourly_cost_per_node: Optional[float] = Field(default=None, ge=0.001, le=10.0)


class SettingsResponse(BaseModel):
    min_instances: int
    max_instances: int
    cooldown_ticks: int
    target_utilization: float
    capacity_per_instance_rps: float
    hourly_cost_per_node: float
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
