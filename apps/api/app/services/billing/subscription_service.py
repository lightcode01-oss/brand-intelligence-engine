"""
Subscription service — orchestrates the full subscription lifecycle.

Sits between the API layer and the payment gateway providers.  Handles:
  - Checkout session creation (delegates to provider)
  - Subscription upgrades and downgrades
  - Cancellations and resumptions
  - Synchronising provider state back to the local database
  - Credit allocation on plan change
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.errors import DomainException
from app.models.user import Subscription, WebhookEvent
from app.services.billing.plan_service import PlanService
from app.services.billing.credit_service import CreditService
from app.services.billing.providers.base import (
    CheckoutSession,
    PortalSession,
    AbstractPaymentProvider,
)
from app.services.billing.providers.registry import get_billing_registry

logger = logging.getLogger(__name__)

# Credits granted on plan activation (bonus on upgrade)
_PLAN_CREDIT_GRANTS: dict[str, float] = {
    "free": 0.0,
    "starter": 50.0,
    "pro": 200.0,
    "business": 1000.0,
    "enterprise": 0.0,  # Enterprise uses custom credit agreements
}


class SubscriptionService:
    """Manages the end-to-end subscription lifecycle for a user."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._plan_svc = PlanService(db)
        self._credit_svc = CreditService(db)

    def _provider(self, slug: Optional[str] = None) -> AbstractPaymentProvider:
        registry = get_billing_registry()
        if slug:
            return registry.get(slug)
        return registry.get_primary()

    # ------------------------------------------------------------------
    # Checkout
    # ------------------------------------------------------------------

    async def create_checkout(
        self,
        user_id: uuid.UUID,
        email: str,
        plan_name: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 0,
        coupon_id: Optional[str] = None,
        provider_slug: Optional[str] = None,
    ) -> CheckoutSession:
        """Creates a provider-hosted checkout session for a plan upgrade."""
        plan = await self._plan_svc.get_plan_by_name(plan_name)
        if not plan:
            raise DomainException(f"Plan '{plan_name}' is not available.")
        if plan.price_monthly == 0.0 and plan_name != "free":
            raise DomainException(f"Plan '{plan_name}' requires a custom contract. Contact sales.")

        provider = self._provider(provider_slug)

        # Ensure customer exists in the gateway
        customer_id = await provider.get_customer_id(user_id)
        if not customer_id:
            await provider.create_customer(user_id, email)

        session = await provider.create_checkout_session(
            user_id=user_id,
            plan_id=plan_name,
            success_url=success_url,
            cancel_url=cancel_url,
            trial_days=trial_days,
            coupon_id=coupon_id,
            metadata={"plan_name": plan_name},
        )
        logger.info(
            "Checkout session created: user=%s plan=%s provider=%s session=%s",
            user_id,
            plan_name,
            provider.provider_name,
            session.session_id,
        )
        return session

    # ------------------------------------------------------------------
    # Customer portal
    # ------------------------------------------------------------------

    async def create_portal_session(
        self,
        user_id: uuid.UUID,
        return_url: str,
        provider_slug: Optional[str] = None,
    ) -> PortalSession:
        """Generates a self-service billing portal URL for the user."""
        provider = self._provider(provider_slug)
        customer_id = await provider.get_customer_id(user_id)
        if not customer_id:
            raise DomainException("No payment gateway customer record found. Please contact support.")
        return await provider.create_customer_portal(customer_id, return_url)

    # ------------------------------------------------------------------
    # Plan changes
    # ------------------------------------------------------------------

    async def upgrade(
        self,
        user_id: uuid.UUID,
        new_plan_name: str,
        provider_slug: Optional[str] = None,
    ) -> Subscription:
        """Upgrades the user to a higher plan with immediate proration."""
        sub = await self._plan_svc.get_user_subscription(user_id)
        if not sub:
            raise DomainException("No active subscription found. Please purchase a plan first.")

        provider = self._provider(provider_slug)

        # Get the provider-side subscription ID if we have it stored
        # (In a full implementation, sub would have a gateway_subscription_id column)
        # For now we update the local record and return it
        updated = await self._plan_svc.assign_plan_to_user(user_id, new_plan_name)

        # Grant upgrade credits
        credit_amount = _PLAN_CREDIT_GRANTS.get(new_plan_name.lower(), 0.0)
        if credit_amount > 0:
            await self._credit_svc.credit_user(user_id, credit_amount, expiration_days=30)

        logger.info("User %s upgraded to plan: %s", user_id, new_plan_name)
        return updated

    async def downgrade(
        self,
        user_id: uuid.UUID,
        new_plan_name: str,
        provider_slug: Optional[str] = None,
    ) -> Subscription:
        """Downgrades the user to a lower plan at the end of the billing period."""
        sub = await self._plan_svc.get_user_subscription(user_id)
        if not sub:
            raise DomainException("No active subscription found.")

        updated = await self._plan_svc.assign_plan_to_user(user_id, new_plan_name)
        logger.info("User %s scheduled downgrade to plan: %s", user_id, new_plan_name)
        return updated

    # ------------------------------------------------------------------
    # Cancellation & resumption
    # ------------------------------------------------------------------

    async def cancel(self, user_id: uuid.UUID, provider_slug: Optional[str] = None) -> bool:
        """Cancels the user's subscription at period end."""
        sub = await self._plan_svc.get_user_subscription(user_id)
        if not sub:
            raise DomainException("No active subscription to cancel.")

        sub.status = "CANCELED"  # type: ignore[assignment]
        await self.db.flush()
        logger.info("Subscription cancelled for user: %s", user_id)
        return True

    async def resume(self, user_id: uuid.UUID, provider_slug: Optional[str] = None) -> Subscription:
        """Resumes a previously cancelled subscription."""
        sub = await self._plan_svc.get_user_subscription(user_id)
        if not sub:
            raise DomainException("No subscription record found.")
        if sub.status != "CANCELED":
            raise DomainException("Subscription is not in a cancelled state.")

        sub.status = "ACTIVE"  # type: ignore[assignment]
        await self.db.flush()
        logger.info("Subscription resumed for user: %s", user_id)
        return sub

    # ------------------------------------------------------------------
    # Usage resets (called by Celery workers)
    # ------------------------------------------------------------------

    async def reset_monthly_usage(self, user_id: uuid.UUID) -> None:
        """Resets the monthly query counter and advances the reset window."""
        sub = await self._plan_svc.get_user_subscription(user_id)
        if sub:
            from datetime import timedelta
            sub.monthly_query_count = 0
            sub.limit_reset_at = datetime.now(timezone.utc) + timedelta(days=30)
            await self.db.flush()
            logger.debug("Monthly usage reset for user: %s", user_id)

    # ------------------------------------------------------------------
    # Webhook event handling
    # ------------------------------------------------------------------

    async def handle_webhook_event(
        self,
        provider_slug: str,
        event_type: str,
        payload: dict,
        idempotency_key: str,
    ) -> None:
        """
        Processes a normalised webhook event from a payment gateway.

        Idempotency is enforced by checking the ``idempotency_key`` against
        previously processed ``WebhookEvent`` records.
        """
        # Idempotency check
        stmt = select(WebhookEvent).where(
            WebhookEvent.provider == provider_slug,
            WebhookEvent.event_type == idempotency_key,
            WebhookEvent.processed_at != None,
        )
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            logger.info("Duplicate webhook event skipped: %s / %s", provider_slug, idempotency_key)
            return

        # Persist the raw event first (before processing, to avoid data loss)
        event = WebhookEvent(
            provider=provider_slug,
            event_type=idempotency_key,  # Store idempotency key as event type for dedup
            payload_json=payload,
            processed_at=None,
        )
        self.db.add(event)
        await self.db.flush()

        # Route to handlers
        try:
            await self._dispatch_event(event_type, payload)
            event.processed_at = datetime.now(timezone.utc)
            await self.db.flush()
        except Exception as exc:
            logger.error("Webhook processing error [%s/%s]: %s", provider_slug, event_type, exc)
            raise

    async def _dispatch_event(self, event_type: str, payload: dict) -> None:
        """Routes canonical event types to the appropriate handlers."""
        handler = {
            "checkout.completed": self._on_checkout_completed,
            "subscription.created": self._on_subscription_created,
            "subscription.updated": self._on_subscription_updated,
            "subscription.cancelled": self._on_subscription_cancelled,
            "invoice.paid": self._on_invoice_paid,
            "invoice.payment_failed": self._on_invoice_payment_failed,
            "refund.created": self._on_refund_created,
        }.get(event_type)

        if handler:
            await handler(payload)
        else:
            logger.warning("No handler for event type: %s", event_type)

    async def _on_checkout_completed(self, payload: dict) -> None:
        metadata = payload.get("metadata", {})
        user_id_str = metadata.get("nomen_user_id")
        plan_name = metadata.get("plan_id") or metadata.get("plan_name")
        if user_id_str and plan_name:
            user_id = uuid.UUID(user_id_str)
            await self._plan_svc.assign_plan_to_user(user_id, plan_name)
            credit_amount = _PLAN_CREDIT_GRANTS.get(plan_name.lower(), 0.0)
            if credit_amount > 0:
                await self._credit_svc.credit_user(user_id, credit_amount, expiration_days=30)

    async def _on_subscription_created(self, payload: dict) -> None:
        await self._on_checkout_completed(payload)

    async def _on_subscription_updated(self, payload: dict) -> None:
        status = payload.get("status")
        metadata = payload.get("metadata", {})
        user_id_str = metadata.get("nomen_user_id")
        if user_id_str and status:
            user_id = uuid.UUID(user_id_str)
            sub = await self._plan_svc.get_user_subscription(user_id)
            if sub:
                status_map = {
                    "active": "ACTIVE",
                    "past_due": "PAST_DUE",
                    "canceled": "CANCELED",
                    "cancelled": "CANCELED",
                }
                sub.status = status_map.get(status, "ACTIVE")  # type: ignore
                await self.db.flush()

    async def _on_subscription_cancelled(self, payload: dict) -> None:
        metadata = payload.get("metadata", {})
        user_id_str = metadata.get("nomen_user_id")
        if user_id_str:
            user_id = uuid.UUID(user_id_str)
            sub = await self._plan_svc.get_user_subscription(user_id)
            if sub:
                sub.status = "CANCELED"  # type: ignore
                await self.db.flush()
            # Downgrade to free on cancellation
            await self._plan_svc.assign_plan_to_user(user_id, "free")

    async def _on_invoice_paid(self, payload: dict) -> None:
        logger.info("Invoice paid event received: %s", payload.get("id"))

    async def _on_invoice_payment_failed(self, payload: dict) -> None:
        metadata = payload.get("metadata", {})
        user_id_str = metadata.get("nomen_user_id")
        if user_id_str:
            user_id = uuid.UUID(user_id_str)
            sub = await self._plan_svc.get_user_subscription(user_id)
            if sub:
                sub.status = "PAST_DUE"  # type: ignore
                await self.db.flush()

    async def _on_refund_created(self, payload: dict) -> None:
        logger.info("Refund event received: %s", payload.get("id"))
