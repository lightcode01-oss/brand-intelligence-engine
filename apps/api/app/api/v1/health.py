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
    """Checks if the service, database, and broker connection are fully initialized."""
    db_connected = False
    try:
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        pass
        
    broker_connected = False
    celery_connected = False
    try:
        import redis
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url, socket_timeout=0.5)
        client.ping()
        broker_connected = True
    except Exception:
        pass
        
    try:
        from app.workers.celery_app import celery_app
        if hasattr(celery_app, "control"):
            insp = celery_app.control.inspect(timeout=0.1)
            celery_connected = True
        else:
            celery_connected = broker_connected
    except Exception:
        pass
        
    all_ready = db_connected and broker_connected
    data = ReadyResponseData(
        status="ready" if all_ready else "not_ready",
        database_connected=db_connected,
        broker_connected=broker_connected,
        celery_connected=celery_connected
    )
    message = "Service is ready to handle traffic." if all_ready else "Service database/broker connection is down."
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
