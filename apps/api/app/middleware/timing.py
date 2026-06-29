import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response
from app.core.logging import logger

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs latency metrics and structured parameters for incoming HTTP queries."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        latency_ms = int(process_time * 1000)
        
        # Pull request state parameters
        request_id = getattr(request.state, "request_id", "system")
        correlation_id = getattr(request.state, "correlation_id", "system")
        workspace_id = getattr(request.state, "workspace_id", None)
        user_id = getattr(request.state, "user_id", None)
        
        log_extra = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "latency": latency_ms,
            "response_status": response.status_code,
            "endpoint": f"{request.method} {request.url.path}",
        }
        
        if workspace_id:
            log_extra["workspace_id"] = str(workspace_id)
        if user_id:
            log_extra["user_id"] = str(user_id)
            
        logger.info(
            f"Processed request: {request.method} {request.url.path} -> {response.status_code} in {latency_ms}ms",
            extra=log_extra
        )
        
        return response
