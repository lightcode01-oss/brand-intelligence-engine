from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from fastapi import Request

T = TypeVar("T")

class ResponseMetadata(BaseModel):
    """Metadata parameters returned in every standard API response."""
    request_id: str = Field(..., description="Unique trace identifier of the request.")
    timestamp: datetime = Field(..., description="UTC completion timestamp of the request.")
    api_version: str = Field(..., description="Current semantic version of the API.")

class StandardResponse(BaseModel, Generic[T]):
    """Standardized response envelope wrapping all successes and failures."""
    success: bool = Field(..., description="Indicates if the query was resolved successfully.")
    message: str = Field("", description="Human-readable informational message.")
    data: Optional[T] = Field(None, description="The resource payload returned by the endpoint.")
    meta: ResponseMetadata = Field(..., description="Response telemetry metadata.")
    errors: list[str] = Field(default_factory=list, description="List of error codes or validation alerts.")

# Health Endpoint Schemas
class HealthResponseData(BaseModel):
    status: str = Field("healthy", description="Status indicator.")
    environment: str = Field(..., description="Target system environment.")

class ReadyResponseData(BaseModel):
    status: str = Field("ready", description="Status indicator.")
    database_connected: bool = Field(..., description="Connection status to the main database.")
    broker_connected: Optional[bool] = Field(None, description="Connection status to the message broker.")
    celery_connected: Optional[bool] = Field(None, description="Celery worker presence status.")

class LiveResponseData(BaseModel):
    status: str = Field("live", description="Liveness check indicator.")
    uptime_seconds: float = Field(..., description="Liveness uptime metrics.")

class VersionResponseData(BaseModel):
    version: str = Field(..., description="Semantic API version.")
    commit_sha: str = Field("unknown", description="Target repository commit SHA.")

class MetricsResponseData(BaseModel):
    active_connections: int = Field(0, description="Active connection pooling count placeholder.")
    jobs_processed_total: int = Field(0, description="Cumulative jobs execution count placeholder.")

def wrap_success_response(data: T, request: Request, message: str = "", api_version: str = "1.0.0") -> StandardResponse[T]:
    """Wraps a payload with success metadata, request ID, and timestamp."""
    from datetime import timezone
    return StandardResponse(
        success=True,
        message=message,
        data=data,
        meta=ResponseMetadata(
            request_id=getattr(request.state, "request_id", "system"),
            timestamp=datetime.now(timezone.utc),
            api_version=api_version
        ),
        errors=[]
    )

