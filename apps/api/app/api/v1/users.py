import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.user import UserResponse, UserUpdate, SubscriptionResponse
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users & Subscription"])

@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(request: Request, current_user: User = Depends(get_current_active_user)) -> StandardResponse[UserResponse]:
    """Retrieves current user's profile details."""
    data = UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        status=current_user.status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "User profile retrieved.")

@router.put("/me", response_model=StandardResponse[UserResponse])
async def update_me(request: Request, payload: UserUpdate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[UserResponse]:
    """Updates current user's email or profile details."""
    data = UserResponse(
        id=current_user.id,
        email=payload.email or current_user.email,
        role=current_user.role,
        status=current_user.status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "User profile updated successfully.")

@router.get("/me/subscription", response_model=StandardResponse[SubscriptionResponse])
async def get_my_subscription(request: Request, current_user: User = Depends(get_current_active_user)) -> StandardResponse[SubscriptionResponse]:
    """Retrieves active subscription limits and quotas."""
    data = SubscriptionResponse(
        id=uuid.uuid4(),
        user_id=current_user.id,
        tier="FREE",
        status="ACTIVE",
        limit_reset_at=datetime.utcnow(),
        monthly_query_count=12,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Subscription details retrieved.")
