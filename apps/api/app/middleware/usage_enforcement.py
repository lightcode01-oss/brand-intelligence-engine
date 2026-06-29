"""
Usage enforcement middleware.

Intercepts requests to metered API endpoints and runs quota checks
before the handler is invoked.  Returns HTTP 429 with a structured
error body when any quota is exceeded.

Metered routes are matched by path prefix patterns.
"""

import json
import logging
import uuid
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Route → action mapping
# Routes that should trigger usage checks, mapped to the action type.
# ---------------------------------------------------------------------------
_METERED_PATTERNS: list[tuple[str, str]] = [
    ("/api/v1/projects/", "generation"),   # POST to generate
    ("/api/v1/exports/", "export"),        # POST to export
]

_API_KEY_PATTERN = "/api/v1/"            # All API-key-authenticated requests


def _extract_workspace_id(request: Request) -> Optional[uuid.UUID]:
    """Extracts workspace_id from request state, path params, or headers."""
    # Set by get_current_workspace_id dependency if called earlier in pipeline
    ws_id = getattr(request.state, "workspace_id", None)
    if ws_id:
        return ws_id
    # Fall back to path parameter
    ws_str = request.path_params.get("workspace_id")
    if not ws_str:
        ws_str = request.headers.get("X-Workspace-Id")
    if ws_str:
        try:
            return uuid.UUID(ws_str)
        except ValueError:
            pass
    return None


class UsageEnforcementMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that enforces usage quotas on metered endpoints.

    Only runs checks on POST requests (writes) to avoid double-counting on GETs.
    Quota check failures short-circuit the request with HTTP 429 before any
    handler logic runs.
    """

    async def dispatch(self, request: Request, call_next):
        # Only apply to POST writes on metered routes
        if request.method not in ("POST", "PUT"):
            return await call_next(request)

        path = request.url.path
        action = self._get_action(path)
        if not action:
            return await call_next(request)

        # Resolve user from request state (set by auth dependency)
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            # Not authenticated — let auth middleware handle it
            return await call_next(request)

        workspace_id = _extract_workspace_id(request)
        if not workspace_id:
            return await call_next(request)

        # Run quota check
        quota_error = await self._check_quota(request, user_id, workspace_id, action)
        if quota_error:
            return quota_error

        return await call_next(request)

    def _get_action(self, path: str) -> Optional[str]:
        for pattern, action in _METERED_PATTERNS:
            if pattern in path:
                return action
        return None

    async def _check_quota(
        self,
        request: Request,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        action: str,
    ) -> Optional[JSONResponse]:
        """Runs the appropriate quota check and returns a 429 response on failure."""
        try:
            # Get DB session from app state
            from app.db.session import AsyncSessionLocal
            from app.services.billing.usage_service import UsageService

            async with AsyncSessionLocal() as db:
                usage_svc = UsageService(db)
                if action == "generation":
                    await usage_svc.check_generation_quota(user_id, workspace_id)
                elif action == "export":
                    await usage_svc.check_export_quota(user_id, workspace_id)
                elif action == "api_request":
                    await usage_svc.check_api_quota(user_id, workspace_id)
            return None

        except Exception as exc:
            from app.exceptions.errors import RateLimitError
            if isinstance(exc, RateLimitError):
                logger.info("Usage quota exceeded for user %s [%s]: %s", user_id, action, exc.message)
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": exc.message,
                        "data": None,
                        "errors": [exc.message],
                        "meta": {
                            "request_id": getattr(request.state, "request_id", "system"),
                            "api_version": "1.0.0",
                        },
                    },
                )
            # For non-quota errors, log and allow the request through
            logger.warning("Usage check error for user %s: %s", user_id, exc)
            return None
