import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_startup_and_openapi() -> None:
    """Verifies that the FastAPI application starts and compiles the OpenAPI schema."""
    assert app.title == "Nomen API"
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]

def test_health_endpoints() -> None:
    """Verifies that all health and liveness checkpoints conform to the envelope contract."""
    endpoints = ["/api/v1/health", "/api/v1/ready", "/api/v1/live", "/api/v1/version", "/api/v1/metrics"]
    for path in endpoints:
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        
        # Verify standard envelope structure
        assert payload["success"] is True
        assert "data" in payload
        assert "meta" in payload
        assert "request_id" in payload["meta"]
        assert "timestamp" in payload["meta"]
        assert "api_version" in payload["meta"]
        assert payload["errors"] == []

def test_security_headers_and_trace_middleware() -> None:
    """Verifies that request tracing and custom security headers are injected."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    # Trace headers
    assert "X-Request-Id" in response.headers
    assert "X-Correlation-Id" in response.headers
    
    # Security headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_validation_error_envelope() -> None:
    """Verifies that validation failures are caught and returned in the envelope structure."""
    # Register with missing password
    response = client.post("/api/v1/auth/register", json={"email": "invalid_email_format"})
    assert response.status_code == 422
    payload = response.json()
    
    assert payload["success"] is False
    assert "data" in payload
    assert payload["data"] is None
    assert len(payload["errors"]) > 0
    # Checks that specific fields failures are detailed in errors list
    assert any("email" in err or "password" in err for err in payload["errors"])
