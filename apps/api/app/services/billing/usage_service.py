"""
Usage service — tracks and enforces consumption limits per user.

All quota checks gate-keep before costly operations.  The ``record_usage``
method is called after successful operations to increment counters.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.errors import RateLimitError
from app.models.user import UsageRecord, Subscription
from app.services.billing.plan_service import PlanService

logger = logging.getLogger(__name__)

# Canonical action keys
ACTION_GENERATION = "generation"
ACTION_EXPORT = "export"
ACTION_API_REQUEST = "api_request"
ACTION_WORKSPACE = "workspace"
ACTION_PROJECT = "project"


class UsageService:
    """Tracks consumption counters and enforces plan quotas."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._plan_svc = PlanService(db)

    async def get_monthly_count(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        action: str,
        period_start: Optional[datetime] = None,
    ) -> int:
        """Returns the consumption count for the current billing period."""
        if period_start is None:
            # Find the subscription reset date
            stmt = select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.deleted_at == None,
            )
            sub = (await self.db.execute(stmt)).scalar_one_or_none()
            period_start = sub.limit_reset_at if sub else datetime.now(timezone.utc)

        # Count usage records since period start
        stmt = select(func.sum(UsageRecord.count)).where(
            UsageRecord.user_id == user_id,
            UsageRecord.workspace_id == workspace_id,
            UsageRecord.action == action,
            UsageRecord.period_start >= period_start,
            UsageRecord.deleted_at == None,
        )
        result = (await self.db.execute(stmt)).scalar()
        return int(result or 0)

    async def get_lifetime_count(self, user_id: uuid.UUID, action: str) -> int:
        """Returns the all-time total count for an action."""
        stmt = select(func.sum(UsageRecord.count)).where(
            UsageRecord.user_id == user_id,
            UsageRecord.action == action,
            UsageRecord.deleted_at == None,
        )
        result = (await self.db.execute(stmt)).scalar()
        return int(result or 0)

    async def record_usage(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        action: str,
        count: int = 1,
    ) -> UsageRecord:
        """Appends a usage record for billing and analytics purposes."""
        record = UsageRecord(
            user_id=user_id,
            workspace_id=workspace_id,
            action=action,
            count=count,
            period_start=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.flush()

        # Also increment the subscription monthly counter
        sub_stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.deleted_at == None,
        )
        sub = (await self.db.execute(sub_stmt)).scalar_one_or_none()
        if sub and action == ACTION_GENERATION:
            sub.monthly_query_count += count
            await self.db.flush()

        return record

    async def get_usage_summary(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> dict:
        """Returns a summary of the user's current period usage across all action types."""
        sub_stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.deleted_at == None,
        )
        sub = (await self.db.execute(sub_stmt)).scalar_one_or_none()
        period_start = sub.limit_reset_at if sub else datetime.now(timezone.utc)
        tier = sub.tier.lower() if sub else "free"

        actions = [ACTION_GENERATION, ACTION_EXPORT, ACTION_API_REQUEST]
        usage: dict = {}
        for action in actions:
            used = await self.get_monthly_count(user_id, workspace_id, action, period_start)
            limit_key = f"{action}s_per_month"
            limit = await self._plan_svc.get_limit(tier, limit_key)
            usage[action] = {
                "used": used,
                "limit": limit,
                "unlimited": limit == -1,
                "remaining": max(0, limit - used) if limit != -1 else None,
                "percent": round((used / limit) * 100, 1) if limit > 0 else 0,
            }

        return {
            "period_start": period_start.isoformat(),
            "period_end": None,
            "tier": tier,
            "actions": usage,
        }

    # ------------------------------------------------------------------
    # Quota enforcement
    # ------------------------------------------------------------------

    async def check_generation_quota(self, user_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
        """
        Raises :class:`RateLimitError` when the user has exhausted their
        monthly generation quota.
        """
        sub_stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.deleted_at == None,
        )
        sub = (await self.db.execute(sub_stmt)).scalar_one_or_none()
        tier = sub.tier.lower() if sub else "free"

        limit = await self._plan_svc.get_limit(tier, "generations_per_month")
        if limit == -1:
            return  # Unlimited

        used = await self.get_monthly_count(
            user_id, workspace_id, ACTION_GENERATION,
            period_start=sub.limit_reset_at if sub else None,
        )
        if used >= limit:
            raise RateLimitError(
                f"Monthly generation quota exceeded ({used}/{limit}). "
                "Upgrade your plan to continue generating names."
            )

    async def check_export_quota(self, user_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
        """Raises :class:`RateLimitError` when the export quota is exhausted."""
        sub_stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.deleted_at == None,
        )
        sub = (await self.db.execute(sub_stmt)).scalar_one_or_none()
        tier = sub.tier.lower() if sub else "free"

        limit = await self._plan_svc.get_limit(tier, "exports_per_month")
        if limit == -1:
            return

        used = await self.get_monthly_count(
            user_id, workspace_id, ACTION_EXPORT,
            period_start=sub.limit_reset_at if sub else None,
        )
        if used >= limit:
            raise RateLimitError(
                f"Monthly export quota exceeded ({used}/{limit}). "
                "Upgrade your plan to export more reports."
            )

    async def check_api_quota(self, user_id: uuid.UUID, workspace_id: uuid.UUID) -> None:
        """Raises :class:`RateLimitError` when the API request quota is exhausted."""
        sub_stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.deleted_at == None,
        )
        sub = (await self.db.execute(sub_stmt)).scalar_one_or_none()
        tier = sub.tier.lower() if sub else "free"

        limit = await self._plan_svc.get_limit(tier, "api_requests_per_month")
        if limit == -1:
            return

        used = await self.get_monthly_count(
            user_id, workspace_id, ACTION_API_REQUEST,
            period_start=sub.limit_reset_at if sub else None,
        )
        if used >= limit:
            raise RateLimitError(
                f"Monthly API request quota exceeded ({used}/{limit}). "
                "Upgrade your plan for higher API limits."
            )

    async def check_credit_balance(self, user_id: uuid.UUID, required_credits: float) -> None:
        """Raises :class:`RateLimitError` when the credit balance is insufficient."""
        from app.services.billing.credit_service import CreditService
        credit_svc = CreditService(self.db)
        balance = await credit_svc.get_balance(user_id)
        if balance < required_credits:
            raise RateLimitError(
                f"Insufficient credit balance. Required: {required_credits}, available: {balance:.2f}. "
                "Purchase additional credits or upgrade your plan."
            )
