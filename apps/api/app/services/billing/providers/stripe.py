"""
Stripe payment gateway provider.

Implements :class:`AbstractPaymentProvider` using the Stripe Python SDK.
All Stripe-specific logic (price IDs, idempotency keys, metadata tagging)
is isolated here and never leaks into the billing service layer.

Configuration keys expected in ``settings``:
    STRIPE_SECRET_KEY          - sk_live_xxx / sk_test_xxx
    STRIPE_WEBHOOK_SECRET      - whsec_xxx
    STRIPE_PRICE_IDS           - JSON dict mapping plan slugs to Stripe Price IDs
                                 e.g. {"pro": "price_xxx", "business": "price_yyy"}
"""

import hmac
import hashlib
import json
import logging
import time
import uuid
from typing import Optional

from app.core.config import settings
from app.services.billing.providers.base import (
    AbstractPaymentProvider,
    CheckoutSession,
    PortalSession,
    ProviderSubscription,
    ProviderInvoice,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional SDK import — gracefully degrade in environments without stripe
# ---------------------------------------------------------------------------
try:
    import stripe as _stripe  # type: ignore
    _stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
    _STRIPE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _stripe = None  # type: ignore
    _STRIPE_AVAILABLE = False


_EVENT_MAP: dict[str, str] = {
    "checkout.session.completed": "checkout.completed",
    "customer.subscription.created": "subscription.created",
    "customer.subscription.updated": "subscription.updated",
    "customer.subscription.deleted": "subscription.cancelled",
    "invoice.paid": "invoice.paid",
    "invoice.payment_failed": "invoice.payment_failed",
    "charge.refunded": "refund.created",
}


class StripeProvider(AbstractPaymentProvider):
    """Production Stripe gateway — all calls are async-wrapped via run_in_executor."""

    provider_name = "stripe"

    def __init__(self) -> None:
        self._secret_key: str = getattr(settings, "STRIPE_SECRET_KEY", "")
        self._webhook_secret: str = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        self._price_ids: dict[str, str] = {}
        raw = getattr(settings, "STRIPE_PRICE_IDS", "{}")
        if isinstance(raw, str):
            try:
                self._price_ids = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("STRIPE_PRICE_IDS is not valid JSON — defaulting to empty dict.")
        elif isinstance(raw, dict):
            self._price_ids = raw

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _stripe_available(self) -> None:
        if not _STRIPE_AVAILABLE or not self._secret_key:
            raise RuntimeError(
                "Stripe SDK is not installed or STRIPE_SECRET_KEY is not configured."
            )

    def _resolve_price_id(self, plan_id: str) -> str:
        price_id = self._price_ids.get(plan_id)
        if not price_id:
            raise ValueError(
                f"No Stripe price ID configured for plan '{plan_id}'. "
                "Add it to the STRIPE_PRICE_IDS setting."
            )
        return price_id

    @staticmethod
    def _norm_subscription(sub: object) -> ProviderSubscription:
        """Converts a stripe.Subscription object into a normalised ProviderSubscription."""
        period_end = None
        trial_end = None
        try:
            current_period_end = getattr(sub, "current_period_end", None)
            if current_period_end:
                from datetime import datetime, timezone
                period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc).isoformat()
            trial_end_ts = getattr(sub, "trial_end", None)
            if trial_end_ts:
                from datetime import datetime, timezone
                trial_end = datetime.fromtimestamp(trial_end_ts, tz=timezone.utc).isoformat()
        except Exception:
            pass

        plan_id = ""
        items = getattr(sub, "items", None)
        if items:
            data = getattr(items, "data", [])
            if data:
                price = getattr(data[0], "price", None)
                if price:
                    plan_id = getattr(price, "id", "")

        return ProviderSubscription(
            subscription_id=sub.id,
            customer_id=sub.customer,
            plan_id=plan_id,
            status=sub.status,
            current_period_end=period_end,
            trial_end=trial_end,
            cancel_at_period_end=getattr(sub, "cancel_at_period_end", False),
            provider="stripe",
            raw=dict(sub),
        )

    @staticmethod
    def _norm_invoice(inv: object) -> ProviderInvoice:
        from datetime import datetime, timezone
        created_at = None
        created_ts = getattr(inv, "created", None)
        if created_ts:
            created_at = datetime.fromtimestamp(created_ts, tz=timezone.utc).isoformat()
        return ProviderInvoice(
            invoice_id=inv.id,
            customer_id=inv.customer,
            amount_paid=(getattr(inv, "amount_paid", 0) or 0) / 100.0,
            currency=getattr(inv, "currency", "usd").upper(),
            status=getattr(inv, "status", "open"),
            invoice_url=getattr(inv, "hosted_invoice_url", None),
            pdf_url=getattr(inv, "invoice_pdf", None),
            created_at=created_at,
            provider="stripe",
            raw=dict(inv),
        )

    # ------------------------------------------------------------------
    # Customer lifecycle
    # ------------------------------------------------------------------

    async def create_customer(self, user_id: uuid.UUID, email: str, name: Optional[str] = None) -> str:
        self._stripe_available()
        customer = _stripe.Customer.create(
            email=email,
            name=name,
            metadata={"nomen_user_id": str(user_id)},
            idempotency_key=f"create_customer_{user_id}",
        )
        logger.info("Stripe customer created: %s for user %s", customer.id, user_id)
        return customer.id

    async def get_customer_id(self, user_id: uuid.UUID) -> Optional[str]:
        self._stripe_available()
        customers = _stripe.Customer.search(
            query=f'metadata["nomen_user_id"]:"{user_id}"',
            limit=1,
        )
        data = getattr(customers, "data", [])
        return data[0].id if data else None

    # ------------------------------------------------------------------
    # Checkout & portal
    # ------------------------------------------------------------------

    async def create_checkout_session(
        self,
        user_id: uuid.UUID,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 0,
        coupon_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> CheckoutSession:
        self._stripe_available()
        price_id = self._resolve_price_id(plan_id)
        customer_id = await self.get_customer_id(user_id)
        params: dict = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {**(metadata or {}), "nomen_user_id": str(user_id), "plan_id": plan_id},
            "idempotency_key": f"checkout_{user_id}_{plan_id}_{int(time.time())}",
        }
        if customer_id:
            params["customer"] = customer_id
        if trial_days > 0:
            params["subscription_data"] = {"trial_period_days": trial_days}
        if coupon_id:
            params["discounts"] = [{"coupon": coupon_id}]

        session = _stripe.checkout.Session.create(**params)
        return CheckoutSession(
            session_id=session.id,
            checkout_url=session.url,
            provider="stripe",
            metadata={"plan_id": plan_id},
        )

    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSession:
        self._stripe_available()
        session = _stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return PortalSession(portal_url=session.url, provider="stripe")

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    async def get_subscription(self, subscription_id: str) -> ProviderSubscription:
        self._stripe_available()
        sub = _stripe.Subscription.retrieve(subscription_id)
        return self._norm_subscription(sub)

    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> ProviderSubscription:
        self._stripe_available()
        price_id = self._resolve_price_id(new_plan_id)
        sub = _stripe.Subscription.retrieve(subscription_id)
        item_id = sub["items"]["data"][0]["id"]
        updated = _stripe.Subscription.modify(
            subscription_id,
            items=[{"id": item_id, "price": price_id}],
            proration_behavior="always_invoice",
        )
        return self._norm_subscription(updated)

    async def downgrade_subscription(self, subscription_id: str, new_plan_id: str) -> ProviderSubscription:
        self._stripe_available()
        price_id = self._resolve_price_id(new_plan_id)
        sub = _stripe.Subscription.retrieve(subscription_id)
        item_id = sub["items"]["data"][0]["id"]
        updated = _stripe.Subscription.modify(
            subscription_id,
            items=[{"id": item_id, "price": price_id}],
            proration_behavior="none",
            billing_cycle_anchor="unchanged",
        )
        return self._norm_subscription(updated)

    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        self._stripe_available()
        if immediate:
            _stripe.Subscription.delete(subscription_id)
        else:
            _stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
        return True

    async def resume_subscription(self, subscription_id: str) -> ProviderSubscription:
        self._stripe_available()
        updated = _stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)
        return self._norm_subscription(updated)

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    async def list_invoices(self, customer_id: str, limit: int = 20) -> list[ProviderInvoice]:
        self._stripe_available()
        invoices = _stripe.Invoice.list(customer=customer_id, limit=min(limit, 100))
        return [self._norm_invoice(inv) for inv in invoices.data]

    # ------------------------------------------------------------------
    # Webhook handling
    # ------------------------------------------------------------------

    def verify_webhook_signature(self, payload: bytes, signature_header: str) -> bool:
        if not self._webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not set — skipping signature verification.")
            return False
        try:
            _stripe.Webhook.construct_event(payload, signature_header, self._webhook_secret)
            return True
        except Exception as exc:
            logger.warning("Stripe webhook signature verification failed: %s", exc)
            return False

    def parse_webhook_event(self, payload: bytes) -> tuple[str, dict]:
        try:
            body = json.loads(payload)
        except json.JSONDecodeError:
            return ("unknown", {})
        raw_type: str = body.get("type", "unknown")
        canonical = _EVENT_MAP.get(raw_type, raw_type)
        return (canonical, body.get("data", {}).get("object", {}))
