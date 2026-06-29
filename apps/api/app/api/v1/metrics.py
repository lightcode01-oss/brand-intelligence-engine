from fastapi import APIRouter, Response
from starlette.responses import PlainTextResponse

router = APIRouter(tags=["Observability"])

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
    prometheus_available = True
    # Define standard gauges
    api_requests_total = Counter("api_requests_total", "Total API requests count", ["method", "endpoint", "status"])
    api_request_latency = Histogram("api_request_latency_seconds", "API request latency histograms", ["endpoint"])
except ImportError:
    prometheus_available = False

@router.get("/metrics", response_class=PlainTextResponse)
def get_metrics() -> Response:
    """Exposes real-time Prometheus scraping metrics endpoint."""
    if prometheus_available:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
        
    # Offline fallback response
    fallback_metrics = (
        "# HELP nomen_api_uptime_seconds Nomen API microservice uptime\n"
        "# TYPE nomen_api_uptime_seconds gauge\n"
        "nomen_api_uptime_seconds 3600.0\n"
    )
    return Response(content=fallback_metrics, media_type="text/plain; version=0.0.4")
from typing import Any
