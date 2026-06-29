import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.main import app
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.models.integration import WorkspaceIntegration, WorkspaceWebhook
from app.services.brand_engine.providers.circuit_breaker import CircuitBreaker
from app.services.brand_engine.providers.registry import ProviderRegistry
from app.core.cache.semantic import SemanticCache, get_embedding, cosine_similarity
from app.services.integrations.registry import integration_registry

@pytest.fixture
def mock_user() -> User:
    return User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="dev@nomen.ai",
        password_hash="pw",
        role="FREE_USER"
    )

@pytest.fixture(autouse=True)
def override_dependencies(db_session: AsyncSession, mock_user: User):
    async def get_test_db():
        yield db_session

    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    app.dependency_overrides[get_db_session] = get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_circuit_breaker_states() -> None:
    cb = CircuitBreaker("mock_test_provider", threshold=2, cooldown=1.0)
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True
    
    # Record first failure
    cb.record_failure()
    assert cb.state == "CLOSED"
    
    # Record second failure (trips threshold of 2)
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_execute() is False
    
    # Verify half-open cooldown recovery
    import time
    time.sleep(1.1)
    assert cb.can_execute() is True
    assert cb.state == "HALF_OPEN"
    
    # Success closes circuit
    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.failures == 0

@pytest.mark.asyncio
async def test_cosine_similarity() -> None:
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert cosine_similarity(v1, v2) == 1.0
    
    v3 = [0.0, 1.0, 0.0]
    assert cosine_similarity(v1, v3) == 0.0

@pytest.mark.asyncio
async def test_semantic_cache_isolation() -> None:
    cache = SemanticCache()
    ws1 = str(uuid.uuid4())
    ws2 = str(uuid.uuid4())
    prompt = "A premium agentic AI pair programming application"
    names = ["Antigravity", "Lightcode", "BrandIntel"]
    
    cache.save(ws1, prompt, names)
    
    # Check ws1 cache hit
    hit1 = cache.lookup(ws1, prompt)
    assert hit1 is not None
    assert hit1[0] == names
    
    # Check ws2 cache miss due to workspace isolation
    hit2 = cache.lookup(ws2, prompt)
    assert hit2 is None
    
    # Invalidate workspace 1
    cache.invalidate_workspace(ws1)
    assert cache.lookup(ws1, prompt) is None

@pytest.mark.asyncio
async def test_integrations_adapters_dispatch() -> None:
    # Test Email adapter
    success = await integration_registry.dispatch(
        "email",
        {"title": "Test Email", "message": "Verify email adapter works."},
        {"to_email": "test@nomen.ai"}
    )
    assert success is True
    
    # Test Slack adapter (invalid url returns false, but handles exception)
    success_slack = await integration_registry.dispatch(
        "slack",
        {"title": "Test Slack", "message": "Verify Slack fails cleanly without webhook_url"},
        {}
    )
    assert success_slack is False

@pytest.mark.asyncio
async def test_integrations_api_flow(db_session: AsyncSession) -> None:
    # Create integration
    payload = {
        "provider_slug": "slack",
        "settings_json": {"webhook_url": "https://hooks.slack.com/services/test/url"},
        "is_active": True
    }
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/integrations/", json=payload)
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["provider_slug"] == "slack"
        integration_id = data["id"]
        
        # List integrations
        res_list = await ac.get("/api/v1/integrations/")
        assert res_list.status_code == 200
        assert len(res_list.json()["data"]) > 0
        
        # Webhooks CRUD test
        webhook_payload = {
            "url": "https://callback.mycompany.com/webhook",
            "secret_key": "sec_12345",
            "events_json": ["generation.success", "generation.failed"],
            "is_active": True
        }
        res_wh = await ac.post("/api/v1/integrations/webhooks", json=webhook_payload)
        assert res_wh.status_code == 201
        wh_data = res_wh.json()["data"]
        assert wh_data["url"] == "https://callback.mycompany.com/webhook"
        webhook_id = wh_data["id"]
        
        # Cleanup webhook
        res_del_wh = await ac.delete(f"/api/v1/integrations/webhooks/{webhook_id}")
        assert res_del_wh.status_code == 200
        
        # Cleanup integration
        res_del = await ac.delete(f"/api/v1/integrations/{integration_id}")
        assert res_del.status_code == 200

@pytest.mark.asyncio
async def test_api_keys_flow(db_session: AsyncSession) -> None:
    # Create Key
    payload = {
        "name": "Dev Script API Key",
        "scopes": ["generation.read", "generation.write"],
        "expiration_days": 30
    }
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/api-keys/", json=payload)
        assert res.status_code == 201
        data = res.json()["data"]
        assert "raw_key" in data
        assert data["raw_key"].startswith("nm_live_")
        
        # List active keys
        res_list = await ac.get("/api/v1/api-keys/")
        assert res_list.status_code == 200
        items = res_list.json()["data"]
        assert len(items) > 0
        key_id = items[0]["id"]
        
        # Revoke Key
        res_del = await ac.delete(f"/api/v1/api-keys/{key_id}")
        assert res_del.status_code == 200
