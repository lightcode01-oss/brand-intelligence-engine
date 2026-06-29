from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.core.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects essential security headers into every API response."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        return response

class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """Intercepts requests and returns a 503 Service Unavailable if maintenance mode is enabled."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if settings.MAINTENANCE_MODE and request.url.path not in ["/health", "/ready", "/live"]:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "Nomen is currently undergoing scheduled maintenance. Please try again shortly.",
                    "data": None,
                    "meta": {},
                    "errors": ["MAINTENANCE_MODE_ACTIVE"]
                }
            )
        return await call_next(request)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Placeholder middleware for request rate limiting."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Placeholder limit check block
        # In the future, this checks request.client.host or user credentials count in Redis cache
        return await call_next(request)
