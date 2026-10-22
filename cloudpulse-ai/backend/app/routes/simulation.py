"""Simulation execution, history, and CSV export routes for CloudPulse AI."""

import json
from datetime import datetime
import io
import csv
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import (
    SimulationRun,
    SystemSettings,
    SimulationRunRequest,
    SimulationComparisonResponse,
    SimulationHistoryItem,
    PolicySimulationSummary,
)
from app.simulation.engine import (
    ResourceSimulationEngine,
    WorkloadProfile,
    generate_profile_workload,
)
from app.simulation.policies import ReactivePolicy, PredictivePolicy

router = APIRouter(prefix="/simulation", tags=["Simulation"])


def get_or_create_settings(db: Session) -> SystemSettings:
    """Fetch current system settings, creating defaults if not present."""
    settings = db.query(SystemSettings).filter(SystemSettings.id == 1).first()
    if not settings:
        settings = SystemSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.post("/run", response_model=SimulationComparisonResponse)
def run_simulation(
    request: SimulationRunRequest = SimulationRunRequest(),
    db: Session = Depends(get_db),
) -> SimulationComparisonResponse:
    """Execute head-to-head comparative autoscaling simulation (Reactive vs Predictive).

    Persists experiment run and aggregate telemetry to SQLite.
    """
    settings = get_or_create_settings(db)

    # 1. Determine demand series
    if request.custom_demand and len(request.custom_demand) > 0:
        demand_series = [float(d) for d in request.custom_demand]
        profile_name = "Custom"
    else:
        profile_name = request.profile
        demand_series = generate_profile_workload(
            profile=profile_name,
            steps=request.steps,
            seed=42,
        )

    # 2. Instantiate policies using configured thresholds
    reactive_policy = ReactivePolicy(
        min_instances=settings.min_instances,
        max_instances=settings.max_instances,
        cooldown_ticks=settings.cooldown_ticks,
    )
    predictive_policy = PredictivePolicy(
        min_instances=settings.min_instances,
        max_instances=settings.max_instances,
        cooldown_ticks=settings.cooldown_ticks,
        target_utilization=settings.target_utilization,
        capacity_per_instance_rps=settings.capacity_per_instance_rps,
    )

    # 3. Initialize simulation engine
    engine = ResourceSimulationEngine(
        instance_capacity_rps=settings.capacity_per_instance_rps,
        provision_delay_ticks=1,
        r_base_ms=25.0,
        hourly_cost_per_node=settings.hourly_cost_per_node,
        tick_duration_minutes=5.0,
    )

    # 4. Execute simulations
    reactive_res = engine.run(
        policy=reactive_policy,
        demand_series=demand_series,
        initial_instances=request.initial_instances,
    )
    predictive_res = engine.run(
        policy=predictive_policy,
        demand_series=demand_series,
        initial_instances=request.initial_instances,
    )

    # 5. Comparative calculations
    react_cost = reactive_res["total_cost_usd"]
    pred_cost = predictive_res["total_cost_usd"]
    cost_diff_pct = 0.0
    if react_cost > 0:
        cost_diff_pct = round(((react_cost - pred_cost) / react_cost) * 100.0, 2)

    react_sla = reactive_res["sla_violations_count"]
    pred_sla = predictive_res["sla_violations_count"]
    sla_reduction_pct = 0.0
    if react_sla > 0:
        sla_reduction_pct = round(((react_sla - pred_sla) / react_sla) * 100.0, 2)
    elif pred_sla == 0:
        sla_reduction_pct = 0.0

    # 6. Build unified comparative timeline
    merged_timeline: List[Dict[str, Any]] = []
    r_timeline = reactive_res["timeline"]
    p_timeline = predictive_res["timeline"]

    for i in range(len(demand_series)):
        merged_timeline.append(
            {
                "tick": i,
                "demand_rps": demand_series[i],
                "reactive_instances": r_timeline[i]["active_instances"],
                "predictive_instances": p_timeline[i]["active_instances"],
                "reactive_capacity": r_timeline[i]["capacity_rps"],
                "predictive_capacity": p_timeline[i]["capacity_rps"],
                "reactive_latency": r_timeline[i]["response_time_ms"],
                "predictive_latency": p_timeline[i]["response_time_ms"],
                "reactive_sla": r_timeline[i]["sla_violation"],
                "predictive_sla": p_timeline[i]["sla_violation"],
                "reactive_action": r_timeline[i]["action"],
                "predictive_action": p_timeline[i]["action"],
            }
        )

    # 7. Persist to Database
    db_run = SimulationRun(
        workload_profile=profile_name,
        total_steps=len(demand_series),
        initial_instances=request.initial_instances,
        reactive_sla_violations=react_sla,
        predictive_sla_violations=pred_sla,
        reactive_p95_latency=reactive_res["p95_response_time_ms"],
        predictive_p95_latency=predictive_res["p95_response_time_ms"],
        reactive_cost=react_cost,
        predictive_cost=pred_cost,
        cost_savings_pct=cost_diff_pct,
        summary_json=json.dumps(
            {
                "reactive": {k: v for k, v in reactive_res.items() if k != "timeline"},
                "predictive": {k: v for k, v in predictive_res.items() if k != "timeline"},
            }
        ),
        timeline_json=json.dumps(merged_timeline),
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    return SimulationComparisonResponse(
        id=db_run.id,
        timestamp=db_run.timestamp.isoformat() + "Z",
        workload_profile=profile_name,
        total_steps=len(demand_series),
        reactive=PolicySimulationSummary(**{k: v for k, v in reactive_res.items() if k != "timeline"}),
        predictive=PolicySimulationSummary(**{k: v for k, v in predictive_res.items() if k != "timeline"}),
        cost_savings_pct=cost_diff_pct,
        sla_reduction_pct=sla_reduction_pct,
        timeline=merged_timeline,
        disclaimer=(
            "DISCLAIMER: All cluster telemetry, autoscaling events, and latency values "
            "are synthetic discrete-event simulations for optimization planning."
        ),
    )


@router.get("/history", response_model=List[SimulationHistoryItem])
def get_simulation_history(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[SimulationHistoryItem]:
    """Retrieve historical comparative simulation experiments."""
    runs = db.query(SimulationRun).order_by(SimulationRun.timestamp.desc()).limit(limit).all()
    return [
        SimulationHistoryItem(
            id=r.id,
            timestamp=r.timestamp.isoformat() + "Z",
            workload_profile=r.workload_profile,
            total_steps=r.total_steps,
            reactive_cost=r.reactive_cost,
            predictive_cost=r.predictive_cost,
            cost_savings_pct=r.cost_savings_pct,
            reactive_sla_violations=r.reactive_sla_violations,
            predictive_sla_violations=r.predictive_sla_violations,
        )
        for r in runs
    ]


@router.get("/export/{simulation_id}")
def export_simulation_csv(
    simulation_id: int,
    db: Session = Depends(get_db),
):
    """Export detailed step-by-step timeline log as a downloadable CSV."""
    db_run = db.query(SimulationRun).filter(SimulationRun.id == simulation_id).first()
    if not db_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation run with id {simulation_id} not found.",
        )

    timeline_data = json.loads(db_run.timeline_json)

    output = io.StringIO()
    if timeline_data and len(timeline_data) > 0:
        fieldnames = list(timeline_data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in timeline_data:
            writer.writerow(row)

    csv_content = output.getvalue()
    filename = f"cloudpulse_simulation_{simulation_id}_{db_run.workload_profile.lower()}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
