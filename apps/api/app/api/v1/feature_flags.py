import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.user import FeatureFlagResponse
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/feature-flags", tags=["Feature Rollouts"])

@router.get("/", response_model=StandardResponse[list[FeatureFlagResponse]])
async def list_feature_flags(request: Request, current_user: User = Depends(get_current_active_user)) -> StandardResponse[list[FeatureFlagResponse]]:
    """Retrieves all active feature rollout toggles for client checking."""
    data = [
        FeatureFlagResponse(
            id=uuid.uuid4(),
            name="ai-search-generation",
            is_enabled=True,
            description="Enables LLM name generation pipeline.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        FeatureFlagResponse(
            id=uuid.uuid4(),
            name="uspto-trademark-clearance",
            is_enabled=False,
            description="Enables live TSDR scraping checks.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    return wrap_success_response(data, request, "Feature flags retrieved.")
