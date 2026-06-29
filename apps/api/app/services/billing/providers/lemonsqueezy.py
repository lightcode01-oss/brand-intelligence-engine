"""
Lemon Squeezy payment gateway provider.

Implements :class:`AbstractPaymentProvider` using the Lemon Squeezy REST API v1.
LemonSqueezy is the secondary/alternative provider; no heavy dependency on an
official SDK — all calls are made via ``httpx`` for testability.

Configuration keys expected in ``settings``:
    LEMONSQUEEZY_API_KEY          - Lemon Squeezy API key
    LEMONSQUEEZY_STORE_ID         - Store ID integer
    LEMONSQUEEZY_WEBHOOK_SECRET   - Signing secret for webhook verification
    LEMONSQUEEZY_VARIANT_IDS      - JSON dict mapping plan slugs to variant IDs
                                    e.g. {"pro": "123456", "business": "234567"}
"""

import hashlib
import hmac
import json
import logging
import uuid
from typing import Optional

import httpx

from app.core.config import settings
from app.services.billing.providers.base import (
    AbstractPaymentProvider,
    CheckoutSession,
    PortalSession,
    ProviderSubscription,
    ProviderInvoice,
)

logger = logging.getLogger(__name__)

_LS_BASE = "https://api.lemonsqueezy.com/v1"

_EVENT_MAP: dict[str, str] = {
    "order_created": "checkout.completed",
    "subscription_created": "subscription.created",
    "subscription_updated": "subscription.updated",
    "subscription_cancelled": "subscription.cancelled",
    "subscription_resumed": "subscription.created",
    "subscription_expired": "subscription.cancelled",
    "subscription_paused": "subscription.updated",
    "subscription_unpaused": "subscription.updated",
    "subscription_payment_success": "invoice.paid",
    "subscription_payment_failed": "invoice.payment_failed",
    "subscription_payment_refunded": "refund.created",
}


class LemonSqueezyProvider(AbstractPaymentProvider):
    """
    Lemon Squeezy gateway integration.

    Uses the REST API directly — no official Python SDK dependency.
    """

    provider_name = "lemonsqueezy"

    def __init__(self) -> None:
        self._api_key: str = getattr(settings, "LEMONSQUEEZY_API_KEY", "")
        self._store_id: str = str(getattr(settings, "LEMONSQUEEZY_STORE_ID", ""))
        self._webhook_secret: str = getattr(settings, "LEMONSQUEEZY_WEBHOOK_SECRET", "")
        self._variant_ids: dict[str, str] = {}
        raw = getattr(settings, "LEMONSQUEEZY_VARIANT_IDS", "{}")
        if isinstance(raw, str):
            try:
                self._variant_ids = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("LEMONSQUEEZY_VARIANT_IDS is not valid JSON — defaulting to empty dict.")
        elif isinstance(raw, dict):
            self._variant_ids = raw

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }

    def _resolve_variant_id(self, plan_id: str) -> str:
        variant_id = self._variant_ids.get(plan_id)
        if not variant_id:
            raise ValueError(
                f"No LemonSqueezy variant ID configured for plan '{plan_id}'. "
                "Add it to the LEMONSQUEEZY_VARIANT_IDS setting."
            )
        return variant_id

    async def _get(self, path: str, params: Optional[dict] = None) -> dict:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{_LS_BASE}{path}", headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    async def _post(self, path: str, body: dict) -> dict:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{_LS_BASE}{path}",
                headers=self._headers(),
                content=json.dumps(body),
            )
            response.raise_for_status()
            return response.json()

    async def _patch(self, path: str, body: dict) -> dict:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.patch(
                f"{_LS_BASE}{path}",
                headers=self._headers(),
                content=json.dumps(body),
            )
            response.raise_for_status()
            return response.json()

    async def _delete(self, path: str) -> None:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.delete(f"{_LS_BASE}{path}", headers=self._headers())
            response.raise_for_status()

    @staticmethod
    def _norm_subscription(data: dict) -> ProviderSubscription:
        attrs = data.get("attributes", {})
        return ProviderSubscription(
            subscription_id=str(data.get("id", "")),
            customer_id=str(attrs.get("customer_id", "")),
            plan_id=str(attrs.get("variant_id", "")),
            status=attrs.get("status", "active"),
            current_period_end=attrs.get("renews_at"),
            trial_end=attrs.get("trial_ends_at"),
            cancel_at_period_end=(attrs.get("status") == "cancelled"),
            provider="lemonsqueezy",
            raw=data,
        )

    @staticmethod
    def _norm_invoice(order: dict) -> ProviderInvoice:
        attrs = order.get("attributes", {})
        total_cents = attrs.get("total", 0) or 0
        return ProviderInvoice(
            invoice_id=str(order.get("id", "")),
            customer_id=str(attrs.get("customer_id", "")),
            amount_paid=total_cents / 100.0,
            currency=(attrs.get("currency", "USD") or "USD").upper(),
            status="paid" if attrs.get("status") == "paid" else "open",
            invoice_url=attrs.get("urls", {}).get("receipt"),
            pdf_url=None,
            created_at=attrs.get("created_at"),
            provider="lemonsqueezy",
            raw=order,
        )

    # ------------------------------------------------------------------
    # Customer lifecycle
    # ------------------------------------------------------------------

    async def create_customer(self, user_id: uuid.UUID, email: str, name: Optional[str] = None) -> str:
        """
        LemonSqueezy creates customers implicitly on checkout completion.
        We search for an existing customer or return a sentinel tag so the
        checkout URL carries the pre-filled email.
        """
        # Return a virtual customer identifier for pre-fill purposes
        return f"ls_prefill_{user_id}"

    async def get_customer_id(self, user_id: uuid.UUID) -> Optional[str]:
        try:
            result = await self._get(
                "/customers",
                params={"filter[email]": str(user_id)},
            )
            items = result.get("data", [])
            return str(items[0]["id"]) if items else None
        except Exception as exc:
            logger.warning("LemonSqueezy get_customer_id failed: %s", exc)
            return None

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
        variant_id = self._resolve_variant_id(plan_id)
        body: dict = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "custom_price": None,
                    "product_options": {
                        "redirect_url": success_url,
                    },
                    "checkout_options": {
                        "embed": False,
                    },
                    "checkout_data": {
                        "custom": {
                            "nomen_user_id": str(user_id),
                            "plan_id": plan_id,
                            **(metadata or {}),
                        }
                    },
                },
                "relationships": {
                    "store": {"data": {"type": "stores", "id": self._store_id}},
                    "variant": {"data": {"type": "variants", "id": variant_id}},
                },
            }
        }
        if coupon_id:
            body["data"]["attributes"]["checkout_data"]["discount_code"] = coupon_id

        result = await self._post("/checkouts", body)
        attrs = result["data"]["attributes"]
        return CheckoutSession(
            session_id=str(result["data"]["id"]),
            checkout_url=attrs["url"],
            provider="lemonsqueezy",
            metadata={"plan_id": plan_id},
        )

    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSession:
        """
        LemonSqueezy does not have an API-driven customer portal — the portal
        URL is static and customer-specific.  Return the store orders page.
        """
        portal_url = f"https://app.lemonsqueezy.com/my-orders"
        return PortalSession(portal_url=portal_url, provider="lemonsqueezy")

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    async def get_subscription(self, subscription_id: str) -> ProviderSubscription:
        result = await self._get(f"/subscriptions/{subscription_id}")
        return self._norm_subscription(result["data"])

    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> ProviderSubscription:
        variant_id = self._resolve_variant_id(new_plan_id)
        result = await self._patch(
            f"/subscriptions/{subscription_id}",
            {
                "data": {
                    "type": "subscriptions",
                    "id": subscription_id,
                    "attributes": {"variant_id": int(variant_id)},
                }
            },
        )
        return self._norm_subscription(result["data"])

    async def downgrade_subscription(self, subscription_id: str, new_plan_id: str) -> ProviderSubscription:
        # LemonSqueezy applies variant changes at renewal — same API call
        return await self.upgrade_subscription(subscription_id, new_plan_id)

    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        await self._delete(f"/subscriptions/{subscription_id}")
        return True

    async def resume_subscription(self, subscription_id: str) -> ProviderSubscription:
        result = await self._patch(
            f"/subscriptions/{subscription_id}",
            {
                "data": {
                    "type": "subscriptions",
                    "id": subscription_id,
                    "attributes": {"cancelled": False},
                }
            },
        )
        return self._norm_subscription(result["data"])

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    async def list_invoices(self, customer_id: str, limit: int = 20) -> list[ProviderInvoice]:
        try:
            result = await self._get(
                "/orders",
                params={"filter[customer_id]": customer_id, "page[size]": min(limit, 100)},
            )
            return [self._norm_invoice(order) for order in result.get("data", [])]
        except Exception as exc:
            logger.warning("LemonSqueezy list_invoices failed for customer %s: %s", customer_id, exc)
            return []

    # ------------------------------------------------------------------
    # Webhook handling
    # ------------------------------------------------------------------

    def verify_webhook_signature(self, payload: bytes, signature_header: str) -> bool:
        if not self._webhook_secret:
            logger.warning("LEMONSQUEEZY_WEBHOOK_SECRET not set — skipping verification.")
            return False
        try:
            expected = hmac.new(
                self._webhook_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, signature_header)
        except Exception as exc:
            logger.warning("LemonSqueezy webhook verification failed: %s", exc)
            return False

    def parse_webhook_event(self, payload: bytes) -> tuple[str, dict]:
        try:
            body = json.loads(payload)
        except json.JSONDecodeError:
            return ("unknown", {})
        raw_type: str = body.get("meta", {}).get("event_name", "unknown")
        canonical = _EVENT_MAP.get(raw_type, raw_type)
        return (canonical, body.get("data", {}))
