"""Health check endpoint for CloudPulse AI."""

from datetime import datetime
from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return system operational status and server timestamp."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z",
        service="CloudPulse AI",
    )
