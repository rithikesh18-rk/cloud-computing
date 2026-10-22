"""FastAPI Application Entry Point for CloudPulse AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.models.schemas import SystemSettings
from app.routes import health, dataset, forecast, simulation, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database tables and seed defaults."""
    Base.metadata.create_all(bind=engine)

    # Seed default system settings if missing
    db = SessionLocal()
    try:
        existing = db.query(SystemSettings).filter(SystemSettings.id == 1).first()
        if not existing:
            default_settings = SystemSettings(id=1)
            db.add(default_settings)
            db.commit()
    finally:
        db.close()

    yield


app = FastAPI(
    title="CloudPulse AI",
    description="Predictive Cloud Workload Forecasting & Resource Optimization System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware for local and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(dataset.router)
api_router.include_router(forecast.router)
api_router.include_router(simulation.router)
api_router.include_router(settings.router)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
