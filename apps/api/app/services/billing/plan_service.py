"""
Plan service — resolves plan configuration and handles plan assignments.

Plans are seeded in the database at startup and cached in memory.
All limits and feature flags are read from ``Plan.limits_json`` and
``Plan.features_json`` columns respectively.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.errors import DomainException
from app.models.user import Plan, Subscription, User

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default plan seeds — used during migrations / first-run bootstrap
# ---------------------------------------------------------------------------

PLAN_SEEDS: list[dict] = [
    {
        "name": "free",
        "price_monthly": 0.0,
        "limits_json": {
            "generations_per_month": 10,
            "exports_per_month": 5,
            "api_requests_per_month": 100,
            "workspaces": 1,
            "projects_per_workspace": 3,
            "team_members": 1,
        },
        "features_json": {
            "ai_providers": ["gemini"],
            "bulk_generation": False,
            "priority_support": False,
            "custom_domain_check": False,
            "trademark_analysis": False,
            "logo_recommendations": False,
        },
    },
    {
        "name": "starter",
        "price_monthly": 9.0,
        "limits_json": {
            "generations_per_month": 100,
            "exports_per_month": 50,
            "api_requests_per_month": 1000,
            "workspaces": 2,
            "projects_per_workspace": 10,
            "team_members": 3,
        },
        "features_json": {
            "ai_providers": ["gemini", "openai"],
            "bulk_generation": True,
            "priority_support": False,
            "custom_domain_check": True,
            "trademark_analysis": False,
            "logo_recommendations": False,
        },
    },
    {
        "name": "pro",
        "price_monthly": 29.0,
        "limits_json": {
            "generations_per_month": 500,
            "exports_per_month": 200,
            "api_requests_per_month": 10000,
            "workspaces": 5,
            "projects_per_workspace": 50,
            "team_members": 10,
        },
        "features_json": {
            "ai_providers": ["gemini", "openai", "claude"],
            "bulk_generation": True,
            "priority_support": True,
            "custom_domain_check": True,
            "trademark_analysis": True,
            "logo_recommendations": True,
        },
    },
    {
        "name": "business",
        "price_monthly": 99.0,
        "limits_json": {
            "generations_per_month": 2000,
            "exports_per_month": 1000,
            "api_requests_per_month": 50000,
            "workspaces": 20,
            "projects_per_workspace": 200,
            "team_members": 50,
        },
        "features_json": {
            "ai_providers": ["gemini", "openai", "claude", "ollama"],
            "bulk_generation": True,
            "priority_support": True,
            "custom_domain_check": True,
            "trademark_analysis": True,
            "logo_recommendations": True,
        },
    },
    {
        "name": "enterprise",
        "price_monthly": 0.0,  # Custom pricing
        "limits_json": {
            "generations_per_month": -1,      # -1 = unlimited
            "exports_per_month": -1,
            "api_requests_per_month": -1,
            "workspaces": -1,
            "projects_per_workspace": -1,
            "team_members": -1,
        },
        "features_json": {
            "ai_providers": ["gemini", "openai", "claude", "ollama"],
            "bulk_generation": True,
            "priority_support": True,
            "custom_domain_check": True,
            "trademark_analysis": True,
            "logo_recommendations": True,
            "sso": True,
            "audit_logs": True,
            "custom_ai_models": True,
        },
    },
]


class PlanService:
    """Reads and assigns pricing plan configuration records."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_plan_by_name(self, name: str) -> Optional[Plan]:
        """Returns a Plan record by its slug name (e.g. 'pro')."""
        stmt = select(Plan).where(Plan.name == name.lower(), Plan.deleted_at == None)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_plans(self) -> list[Plan]:
        """Returns all active pricing plans ordered by monthly price."""
        stmt = select(Plan).where(Plan.deleted_at == None).order_by(Plan.price_monthly)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_limit(self, plan_name: str, limit_key: str) -> int:
        """
        Returns a specific numeric limit for a plan.

        Returns ``-1`` for unlimited plans and ``0`` for missing keys.
        """
        plan = await self.get_plan_by_name(plan_name)
        if not plan:
            return 0
        return plan.limits_json.get(limit_key, 0)

    async def has_feature(self, plan_name: str, feature_key: str) -> bool:
        """Returns True when the plan has a boolean feature enabled."""
        plan = await self.get_plan_by_name(plan_name)
        if not plan:
            return False
        value = plan.features_json.get(feature_key, False)
        return bool(value)

    async def assign_plan_to_user(
        self,
        user_id: uuid.UUID,
        plan_name: str,
        provider_subscription_id: Optional[str] = None,
        trial_days: int = 0,
    ) -> Subscription:
        """
        Creates or updates the user's subscription to the given plan.

        If an active subscription already exists it is updated in-place;
        otherwise a new record is created.
        """
        plan_name = plan_name.lower()
        plan = await self.get_plan_by_name(plan_name)
        if not plan:
            raise DomainException(f"Plan '{plan_name}' does not exist.")

        # Map plan name to subscription tier enum
        tier_map = {
            "free": "FREE",
            "starter": "FREE",    # Map starter to FREE tier enum for now
            "pro": "PRO",
            "business": "PRO",
            "enterprise": "ENTERPRISE",
        }
        tier = tier_map.get(plan_name, "FREE")

        # Find existing subscription
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.deleted_at == None,
        ).order_by(Subscription.created_at.desc())
        existing = (await self.db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.tier = tier  # type: ignore[assignment]
            existing.status = "ACTIVE"
            if trial_days > 0:
                existing.limit_reset_at = datetime.now(timezone.utc) + timedelta(days=trial_days)
            else:
                existing.limit_reset_at = datetime.now(timezone.utc) + timedelta(days=30)
            existing.monthly_query_count = 0
            await self.db.flush()
            logger.info("Subscription updated for user %s → %s (%s)", user_id, plan_name, tier)
            return existing

        # Create fresh subscription
        now = datetime.now(timezone.utc)
        reset_at = now + timedelta(days=(trial_days if trial_days > 0 else 30))
        sub = Subscription(
            user_id=user_id,
            tier=tier,
            status="ACTIVE",
            limit_reset_at=reset_at,
            monthly_query_count=0,
        )
        self.db.add(sub)
        await self.db.flush()
        logger.info("Subscription created for user %s → %s (%s)", user_id, plan_name, tier)
        return sub

    async def activate_trial(self, user_id: uuid.UUID, plan_name: str, trial_days: int = 14) -> Subscription:
        """Assigns a plan with a trial period and marks the subscription accordingly."""
        return await self.assign_plan_to_user(user_id, plan_name, trial_days=trial_days)

    async def get_user_subscription(self, user_id: uuid.UUID) -> Optional[Subscription]:
        """Returns the user's most recent active subscription."""
        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.deleted_at == None)
            .order_by(Subscription.created_at.desc())
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
