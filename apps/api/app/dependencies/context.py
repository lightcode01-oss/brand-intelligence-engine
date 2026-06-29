import uuid
from typing import Generator
import logging
from fastapi import Request, Depends
from app.core.config import Settings, settings
from app.core.logging import logger

def get_settings() -> Settings:
    """Dependency provider supplying system configuration settings."""
    return settings

def get_logger() -> logging.Logger:
    """Dependency provider supplying the app structured logger."""
    return logger

def get_request_id(request: Request) -> str:
    """Dependency provider supplying the current trace request ID."""
    return getattr(request.state, "request_id", "system")

def get_workspace_id_context(request: Request) -> Optional[uuid.UUID]:
    """Dependency provider supplying the active workspace context parsed from request state."""
    return getattr(request.state, "workspace_id", None)

def get_active_feature_flags() -> list[str]:
    """Dependency provider supplying enabled feature flags."""
    # Placeholder: returns mocked enabled flags list
    return ["ai-search-generation", "premium-export-downloads"]
