import pytest
import time
import os
import sys
from unittest.mock import MagicMock

# Mock database modules before imports
for m in [
    'sqlalchemy',
    'sqlalchemy.ext',
    'sqlalchemy.ext.asyncio',
    'sqlalchemy.orm',
    'sqlalchemy.future',
    'sqlalchemy.sql',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.sql.functions'
]:
    sys.modules[m] = MagicMock()

# Mock models base class attributes
class MockBase:
    metadata = MagicMock()

sys.modules['app.models.base'] = MagicMock()
sys.modules['app.models.base'].Base = MockBase
sys.modules['app.models.base'].StandardBase = MockBase
sys.modules['app.models.base'].ImmutableBase = MockBase

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.rate_limit import RedisRateLimiterMiddleware
from app.services.storage.local import LocalStorageProvider
from app.services.storage.s3 import S3StorageProvider

# Mock Redis class for sliding window testing
class MockRedis:
    def __init__(self):
        self.storage = {}
        
    class MockPipeline:
        def __init__(self, parent):
            self.parent = parent
            self.commands = []
            
        def zremrangebyscore(self, key, min_val, max_val):
            self.commands.append(("zrem", key, min_val, max_val))
            return self
            
        def zcard(self, key):
            self.commands.append(("zcard", key))
            return self
            
        def zadd(self, key, mapping):
            self.commands.append(("zadd", key, mapping))
            return self
            
        def expire(self, key, ttl):
            self.commands.append(("expire", key, ttl))
            return self
            
        def execute(self):
            # Simulate returning: (removed_count, card, add_status, expire_status)
            # Default mock hit count: returns 10 hits
            return (0, 10, 1, True)
            
    def pipeline(self):
        return self.MockPipeline(self)

def test_rate_limiter_middleware_bypass() -> None:
    # 1. Create a dummy FastAPI app
    app = FastAPI()
    
    # Register rate limiter with custom limit of 5 requests
    mock_redis = MockRedis()
    app.add_middleware(RedisRateLimiterMiddleware, redis_client=mock_redis, requests_limit=5, window_secs=60)
    
    @app.get("/test-route")
    def route():
        return {"status": "ok"}
        
    client = TestClient(app)
    
    # 2. Query endpoint. Since MockRedis.pipeline().execute() returns 10 hits (which is > 5),
    # the middleware should trigger HTTP 429 Too Many Requests.
    response = client.get("/test-route")
    assert response.status_code == 429
    assert response.json()["status"] == "error"

def test_metrics_endpoint() -> None:
    from app.api.v1.metrics import router
    app = FastAPI()
    app.include_router(router)
    
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "nomen_api_uptime_seconds" in response.text

@pytest.mark.asyncio
async def test_local_storage_provider() -> None:
    provider = LocalStorageProvider(base_dir="./scratch/test_storage")
    
    # Write a test file
    test_file = "./scratch/test_file.txt"
    os.makedirs("./scratch", exist_ok=True)
    with open(test_file, "w") as f:
        f.write("Local Storage verification content.")
        
    # Upload
    url = await provider.upload(test_file, "verify.txt")
    assert url.startswith("file://")
    
    # Download
    downloaded_file = "./scratch/downloaded_verify.txt"
    downloaded = await provider.download("verify.txt", downloaded_file)
    assert downloaded is True
    
    with open(downloaded_file, "r") as f:
        assert f.read() == "Local Storage verification content."
        
    # Delete
    deleted = await provider.delete("verify.txt")
    assert deleted is True
    
    # Clean up local scratch files
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)
