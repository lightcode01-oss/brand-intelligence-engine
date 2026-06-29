import time
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.core.config import settings
from app.dependencies.database import get_db_session
from app.schemas.response import (
    StandardResponse, HealthResponseData, ReadyResponseData, 
    LiveResponseData, VersionResponseData, MetricsResponseData,
    wrap_success_response
)

router = APIRouter(tags=["Health & Status"])

# Record start time for uptime measurements
START_TIME = time.time()

@router.get("/health", response_model=StandardResponse[HealthResponseData])
async def get_health(request: Request) -> StandardResponse[HealthResponseData]:
    """Base system status check."""
    data = HealthResponseData(status="healthy", environment=settings.ENV)
    return wrap_success_response(data, request, "System is healthy.")

@router.get("/ready", response_model=StandardResponse[ReadyResponseData])
async def get_ready(request: Request, db: AsyncSession = Depends(get_db_session)) -> StandardResponse[ReadyResponseData]:
    """Checks if the service and database connection are fully initialized."""
    db_connected = False
    try:
        # Run a fast ping statement
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        pass
        
    data = ReadyResponseData(status="ready" if db_connected else "not_ready", database_connected=db_connected)
    message = "Service is ready to handle traffic." if db_connected else "Service database connection is down."
    return wrap_success_response(data, request, message)

@router.get("/live", response_model=StandardResponse[LiveResponseData])
async def get_live(request: Request) -> StandardResponse[LiveResponseData]:
    """Simple check to monitor container liveness and process uptime."""
    uptime = time.time() - START_TIME
    data = LiveResponseData(status="live", uptime_seconds=uptime)
    return wrap_success_response(data, request, "Container is live.")

@router.get("/version", response_model=StandardResponse[VersionResponseData])
async def get_version(request: Request) -> StandardResponse[VersionResponseData]:
    """Retrieves current API runtime version parameters."""
    data = VersionResponseData(version=settings.API_VERSION, commit_sha="unknown")
    return wrap_success_response(data, request, "Version info retrieved.")

@router.get("/metrics", response_model=StandardResponse[MetricsResponseData])
async def get_metrics(request: Request) -> StandardResponse[MetricsResponseData]:
    """Telemetry placeholder endpoint."""
    data = MetricsResponseData(active_connections=1, jobs_processed_total=0)
    return wrap_success_response(data, request, "Telemetry metrics retrieved.")
