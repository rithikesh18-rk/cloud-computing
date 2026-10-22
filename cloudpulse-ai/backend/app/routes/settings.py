"""System configuration settings management routes for CloudPulse AI."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import SystemSettings, SettingsUpdate, SettingsResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


def get_or_create_settings(db: Session) -> SystemSettings:
    """Retrieve active settings or initialize with factory defaults."""
    settings = db.query(SystemSettings).filter(SystemSettings.id == 1).first()
    if not settings:
        settings = SystemSettings(
            id=1,
            min_instances=2,
            max_instances=20,
            cooldown_ticks=3,
            target_utilization=0.70,
            capacity_per_instance_rps=200.0,
            hourly_cost_per_node=0.05,
            updated_at=datetime.utcnow(),
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)) -> SettingsResponse:
    """Fetch current system configuration and scaling thresholds."""
    settings = get_or_create_settings(db)
    return SettingsResponse(
        min_instances=settings.min_instances,
        max_instances=settings.max_instances,
        cooldown_ticks=settings.cooldown_ticks,
        target_utilization=settings.target_utilization,
        capacity_per_instance_rps=settings.capacity_per_instance_rps,
        hourly_cost_per_node=settings.hourly_cost_per_node,
        updated_at=settings.updated_at.isoformat() + "Z",
    )


@router.put("", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """Update runtime parameters, instance limits, and cost figures."""
    settings = get_or_create_settings(db)

    # Validate relative instance constraints
    new_min = payload.min_instances if payload.min_instances is not None else settings.min_instances
    new_max = payload.max_instances if payload.max_instances is not None else settings.max_instances

    if new_min > new_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"min_instances ({new_min}) cannot exceed max_instances ({new_max}).",
        )

    for field, val in payload.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(settings, field, val)

    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)

    return SettingsResponse(
        min_instances=settings.min_instances,
        max_instances=settings.max_instances,
        cooldown_ticks=settings.cooldown_ticks,
        target_utilization=settings.target_utilization,
        capacity_per_instance_rps=settings.capacity_per_instance_rps,
        hourly_cost_per_node=settings.hourly_cost_per_node,
        updated_at=settings.updated_at.isoformat() + "Z",
    )
