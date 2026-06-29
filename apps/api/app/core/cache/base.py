import json
from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseCache(ABC):
    """Abstract interface defining cache operations and serializations."""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        # Local memory fallback dict
        self._local_storage: dict[str, str] = {}
        
    @abstractmethod
    def _get_redis_client(self) -> Optional[Any]:
        """Lazy loads and returns the active Redis client if available."""
        pass
        
    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Retrieves a JSON-deserialized object from the cache."""
        client = self._get_redis_client()
        if client:
            try:
                data = client.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                pass
                
        # Fallback to local store
        val = self._local_storage.get(key)
        return json.loads(val) if val else None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Serializes and saves an object to the cache with an optional TTL."""
        target_ttl = ttl if ttl is not None else self.ttl
        serialized = json.dumps(value)
        
        client = self._get_redis_client()
        if client:
            try:
                client.set(key, serialized, ex=target_ttl)
                return
            except Exception:
                pass
                
        # Fallback to local store
        self._local_storage[key] = serialized
        
    def delete(self, key: str) -> None:
        """Removes a key from the cache."""
        client = self._get_redis_client()
        if client:
            try:
                client.delete(key)
                return
            except Exception:
                pass
                
        self._local_storage.pop(key, None)
