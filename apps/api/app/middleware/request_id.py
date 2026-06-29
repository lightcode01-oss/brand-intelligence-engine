import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique X-Request-ID and X-Correlation-ID into every request state and response header."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check if request has correlation headers, fallback to generation
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-Id", request_id)
        
        # Attach to request state
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Set response headers
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Correlation-Id"] = correlation_id
        return response
