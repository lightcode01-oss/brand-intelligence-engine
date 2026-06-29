import time
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class RedisRateLimiterMiddleware(BaseHTTPMiddleware):
    """Resilience middleware applying sliding-window rate-limiting checks via Redis sorted sets."""
    
    def __init__(self, app, redis_client=None, requests_limit: int = 100, window_secs: int = 60):
        super().__init__(app)
        self.limit = requests_limit
        self.window = window_secs
        self._redis = redis_client
        self._initialized = False
        
    def _get_redis(self):
        if self._initialized:
            return self._redis
            
        self._initialized = True
        if not self._redis:
            try:
                import redis
                self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis = None
        return self._redis

    async def dispatch(self, request: Request, call_next) -> Response:
        redis_client = self._get_redis()
        if not redis_client:
            # Fallback bypass mode if Redis is offline (production resilience rule)
            return await call_next(request)
            
        # Determine rate limiting key
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        workspace_id = getattr(request.state, "workspace_id", None)
        
        # Build composite keys
        if workspace_id:
            key = f"rate_limit:workspace:{workspace_id}"
        elif user_id:
            key = f"rate_limit:user:{user_id}"
        else:
            key = f"rate_limit:ip:{client_ip}"
            
        now = time.time()
        clear_before = now - self.window
        
        try:
            # Pipeline atomic transactions
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, clear_before)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window)
            _, current_requests, _, _ = pipe.execute()
            
            if current_requests > self.limit:
                # Return standard API Envelope error
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "status": "error",
                        "timestamp": int(now),
                        "message": "Rate limit exceeded. Too many requests.",
                        "errors": [f"Maximum requests limit of {self.limit} per {self.window}s exceeded."]
                    }
                )
        except Exception:
            # Fallback bypass on transient Redis connection exceptions
            pass
            
        return await call_next(request)
