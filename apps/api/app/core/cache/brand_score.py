import os
from typing import Optional, Any
from app.core.cache.base import BaseCache

class BrandScoreCache(BaseCache):
    """Caching wrapper for computed brand scores."""
    
    def __init__(self):
        # Default TTL of 1 day (86400s)
        super().__init__(ttl=int(os.getenv("CACHE_TTL_BRAND_SCORE", "86400")))
        self._client: Optional[Any] = None
        self._initialized = False
        
    def _get_redis_client(self) -> Optional[Any]:
        if self._initialized:
            return self._client
            
        self._initialized = True
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self._client = redis.from_url(redis_url, socket_timeout=1)
        except Exception:
            self._client = None
            
        return self._client
