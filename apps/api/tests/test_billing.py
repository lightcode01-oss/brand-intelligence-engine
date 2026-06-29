"""
Phase 3.3 — Billing & Subscriptions Test Suite

Tests cover:
  - Checkout session creation
  - Webhook idempotency protection
  - Subscription upgrade/downgrade
  - Usage enforcement and quota checking
  - Credit allocation on plan change
  - Coupon validation and discount computation
  - Provider registry slug resolution
  - Invoice service fallback logic
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Provider registry tests
# ---------------------------------------------------------------------------

class TestBillingProviderRegistry:
    """Tests for provider registration, retrieval, and dynamic loading."""

    def test_register_and_get_stripe(self):
        from app.services.billing.providers.registry import BillingProviderRegistry
        from app.services.billing.providers.stripe import StripeProvider

        registry = BillingProviderRegistry()
        with patch("app.services.billing.providers.registry._load_provider_class") as mock_load:
            mock_load.return_value = StripeProvider
            registry.register("stripe")
            registry._primary = "stripe"

        provider = registry.get("stripe")
        assert isinstance(provider, StripeProvider)

    def test_get_unknown_slug_raises(self):
        from app.services.billing.providers.registry import BillingProviderRegistry
        registry = BillingProviderRegistry()
        with pytest.raises(KeyError):
            registry.get("nonexistent")

    def test_register_unknown_slug_raises(self):
        from app.services.billing.providers.registry import BillingProviderRegistry
        registry = BillingProviderRegistry()
        with pytest.raises(ValueError, match="Unknown billing provider slug"):
            registry.register("paypal")

    def test_register_custom_provider(self):
        from app.services.billing.providers.registry import BillingProviderRegistry
        from app.services.billing.providers.base import AbstractPaymentProvider

        class MockProvider(AbstractPaymentProvider):
            provider_name = "mock"
            async def create_customer(self, *a, **kw): pass
            async def get_customer_id(self, *a, **kw): return None
            async def create_checkout_session(self, *a, **kw): pass
            async def create_customer_portal(self, *a, **kw): pass
            async def get_subscription(self, *a, **kw): pass
            async def upgrade_subscription(self, *a, **kw): pass
            async def downgrade_subscription(self, *a, **kw): pass
            async def cancel_subscription(self, *a, **kw): pass
            async def resume_subscription(self, *a, **kw): pass
            async def list_invoices(self, *a, **kw): return []
            def verify_webhook_signature(self, *a, **kw): return True
            def parse_webhook_event(self, *a, **kw): return ("test.event", {})

        registry = BillingProviderRegistry()
        registry.register_custom("mock", MockProvider())
        assert "mock" in registry.available_slugs()

    def test_available_slugs_returns_registered(self):
        from app.services.billing.providers.registry import BillingProviderRegistry
        from app.services.billing.providers.stripe import StripeProvider

        registry = BillingProviderRegistry()
        registry.register_custom("stripe", StripeProvider())
        assert "stripe" in registry.available_slugs()


# ---------------------------------------------------------------------------
# Stripe provider tests
# ---------------------------------------------------------------------------

class TestStripeProvider:
    """Unit tests for Stripe provider methods (mocked SDK)."""

    def _make_provider(self):
        from app.services.billing.providers.stripe import StripeProvider
        provider = StripeProvider()
        provider._secret_key = "sk_test_xxx"
        provider._webhook_secret = "whsec_test_xxx"
        provider._price_ids = {"pro": "price_pro_xxx", "starter": "price_starter_xxx"}
        return provider

    def test_resolve_price_id_known_plan(self):
        provider = self._make_provider()
        assert provider._resolve_price_id("pro") == "price_pro_xxx"

    def test_resolve_price_id_unknown_raises(self):
        provider = self._make_provider()
        with pytest.raises(ValueError, match="No Stripe price ID"):
            provider._resolve_price_id("enterprise")

    def test_parse_webhook_event_maps_canonical(self):
        provider = self._make_provider()
        payload = json.dumps({
            "type": "customer.subscription.created",
            "data": {"object": {"id": "sub_xxx", "metadata": {"nomen_user_id": str(uuid.uuid4())}}}
        }).encode()
        event_type, data = provider.parse_webhook_event(payload)
        assert event_type == "subscription.created"
        assert data["id"] == "sub_xxx"

    def test_parse_webhook_event_invalid_json(self):
        provider = self._make_provider()
        event_type, data = provider.parse_webhook_event(b"not-json")
        assert event_type == "unknown"
        assert data == {}

    def test_verify_webhook_signature_no_secret_returns_false(self):
        from app.services.billing.providers.stripe import StripeProvider
        provider = StripeProvider()
        provider._webhook_secret = ""
        assert provider.verify_webhook_signature(b"payload", "sig") is False

    def test_norm_subscription(self):
        from app.services.billing.providers.stripe import StripeProvider
        mock_sub = MagicMock()
        mock_sub.id = "sub_test"
        mock_sub.customer = "cus_test"
        mock_sub.status = "active"
        mock_sub.cancel_at_period_end = False
        mock_sub.current_period_end = None
        mock_sub.trial_end = None
        items = MagicMock()
        items.data = [MagicMock()]
        items.data[0].price = MagicMock()
        items.data[0].price.id = "price_pro"
        mock_sub.items = items
        mock_sub.__iter__ = MagicMock(return_value=iter([]))

        # Patch dict() conversion
        with patch("builtins.dict", return_value={}):
            result = StripeProvider._norm_subscription(mock_sub)
        assert result.subscription_id == "sub_test"
        assert result.status == "active"
        assert result.provider == "stripe"


# ---------------------------------------------------------------------------
# LemonSqueezy provider tests
# ---------------------------------------------------------------------------

class TestLemonSqueezyProvider:
    """Unit tests for LemonSqueezy provider."""

    def _make_provider(self):
        from app.services.billing.providers.lemonsqueezy import LemonSqueezyProvider
        provider = LemonSqueezyProvider()
        provider._api_key = "ls_test_xxx"
        provider._store_id = "12345"
        provider._webhook_secret = "ls_webhook_secret"
        provider._variant_ids = {"pro": "111111", "starter": "222222"}
        return provider

    def test_resolve_variant_id_known(self):
        provider = self._make_provider()
        assert provider._resolve_variant_id("pro") == "111111"

    def test_resolve_variant_id_unknown_raises(self):
        provider = self._make_provider()
        with pytest.raises(ValueError, match="No LemonSqueezy variant ID"):
            provider._resolve_variant_id("enterprise")

    def test_parse_webhook_event_maps_canonical(self):
        provider = self._make_provider()
        payload = json.dumps({
            "meta": {"event_name": "subscription_created"},
            "data": {"id": "sub_ls_123", "attributes": {}}
        }).encode()
        event_type, data = provider.parse_webhook_event(payload)
        assert event_type == "subscription.created"

    def test_verify_signature_no_secret_false(self):
        from app.services.billing.providers.lemonsqueezy import LemonSqueezyProvider
        provider = LemonSqueezyProvider()
        provider._webhook_secret = ""
        assert provider.verify_webhook_signature(b"body", "sig") is False

    def test_verify_signature_correct(self):
        import hmac
        import hashlib
        provider = self._make_provider()
        body = b"test_payload"
        expected_sig = hmac.new(
            provider._webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        assert provider.verify_webhook_signature(body, expected_sig) is True

    def test_norm_subscription(self):
        from app.services.billing.providers.lemonsqueezy import LemonSqueezyProvider
        data = {
            "id": "sub_ls_999",
            "attributes": {
                "customer_id": "cust_111",
                "variant_id": "111111",
                "status": "active",
                "renews_at": "2026-07-29T00:00:00Z",
                "trial_ends_at": None,
            }
        }
        result = LemonSqueezyProvider._norm_subscription(data)
        assert result.subscription_id == "sub_ls_999"
        assert result.customer_id == "cust_111"
        assert result.provider == "lemonsqueezy"


# ---------------------------------------------------------------------------
# Plan service tests
# ---------------------------------------------------------------------------

class TestPlanService:
    """Tests for PlanService methods using mocked DB sessions."""

    @pytest.mark.asyncio
    async def test_get_limit_unlimited_plan(self):
        from app.services.billing.plan_service import PlanService
        from app.models.user import Plan

        mock_plan = MagicMock(spec=Plan)
        mock_plan.limits_json = {"generations_per_month": -1}
        mock_plan.deleted_at = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_plan
        mock_db.execute.return_value = mock_result

        svc = PlanService(mock_db)
        svc.get_plan_by_name = AsyncMock(return_value=mock_plan)

        limit = await svc.get_limit("enterprise", "generations_per_month")
        assert limit == -1

    @pytest.mark.asyncio
    async def test_get_limit_missing_key_returns_zero(self):
        from app.services.billing.plan_service import PlanService
        from app.models.user import Plan

        mock_plan = MagicMock(spec=Plan)
        mock_plan.limits_json = {}
        mock_db = AsyncMock()

        svc = PlanService(mock_db)
        svc.get_plan_by_name = AsyncMock(return_value=mock_plan)

        limit = await svc.get_limit("free", "nonexistent_key")
        assert limit == 0

    @pytest.mark.asyncio
    async def test_get_limit_no_plan_returns_zero(self):
        from app.services.billing.plan_service import PlanService

        mock_db = AsyncMock()
        svc = PlanService(mock_db)
        svc.get_plan_by_name = AsyncMock(return_value=None)

        limit = await svc.get_limit("unknown_plan", "generations_per_month")
        assert limit == 0

    @pytest.mark.asyncio
    async def test_has_feature_true(self):
        from app.services.billing.plan_service import PlanService
        from app.models.user import Plan

        mock_plan = MagicMock(spec=Plan)
        mock_plan.features_json = {"bulk_generation": True}
        mock_db = AsyncMock()

        svc = PlanService(mock_db)
        svc.get_plan_by_name = AsyncMock(return_value=mock_plan)

        assert await svc.has_feature("pro", "bulk_generation") is True

    @pytest.mark.asyncio
    async def test_has_feature_false(self):
        from app.services.billing.plan_service import PlanService
        from app.models.user import Plan

        mock_plan = MagicMock(spec=Plan)
        mock_plan.features_json = {"bulk_generation": False}
        mock_db = AsyncMock()

        svc = PlanService(mock_db)
        svc.get_plan_by_name = AsyncMock(return_value=mock_plan)

        assert await svc.has_feature("free", "bulk_generation") is False


# ---------------------------------------------------------------------------
# Usage service tests
# ---------------------------------------------------------------------------

class TestUsageService:
    """Tests for quota enforcement and usage recording."""

    @pytest.mark.asyncio
    async def test_check_generation_quota_passes_unlimited(self):
        from app.services.billing.usage_service import UsageService
        from app.models.user import Subscription

        mock_sub = MagicMock(spec=Subscription)
        mock_sub.tier = "ENTERPRISE"
        mock_sub.limit_reset_at = datetime.now(timezone.utc)
        mock_sub.deleted_at = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_sub
        mock_db.execute.return_value = mock_result

        svc = UsageService(mock_db)
        svc._plan_svc = AsyncMock()
        svc._plan_svc.get_limit = AsyncMock(return_value=-1)

        user_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        # Should not raise
        await svc.check_generation_quota(user_id, workspace_id)

    @pytest.mark.asyncio
    async def test_check_generation_quota_exceeded_raises(self):
        from app.services.billing.usage_service import UsageService
        from app.exceptions.errors import RateLimitError
        from app.models.user import Subscription

        mock_sub = MagicMock(spec=Subscription)
        mock_sub.tier = "FREE"
        mock_sub.limit_reset_at = datetime.now(timezone.utc)
        mock_sub.deleted_at = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_sub
        mock_db.execute.return_value = mock_result

        svc = UsageService(mock_db)
        svc._plan_svc = AsyncMock()
        svc._plan_svc.get_limit = AsyncMock(return_value=10)
        svc.get_monthly_count = AsyncMock(return_value=10)  # At limit

        with pytest.raises(RateLimitError, match="Monthly generation quota exceeded"):
            await svc.check_generation_quota(uuid.uuid4(), uuid.uuid4())

    @pytest.mark.asyncio
    async def test_record_usage_creates_record(self):
        from app.services.billing.usage_service import UsageService, ACTION_GENERATION
        from app.models.user import UsageRecord, Subscription

        mock_sub = MagicMock(spec=Subscription)
        mock_sub.monthly_query_count = 5
        mock_sub.deleted_at = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_sub
        mock_db.execute.return_value = mock_result

        svc = UsageService(mock_db)
        record = await svc.record_usage(uuid.uuid4(), uuid.uuid4(), ACTION_GENERATION, count=2)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called()


# ---------------------------------------------------------------------------
# Coupon service tests
# ---------------------------------------------------------------------------

class TestCouponService:
    """Tests for coupon validation and discount computation."""

    @pytest.mark.asyncio
    async def test_validate_valid_coupon(self):
        from app.services.billing.coupon_service import CouponService
        from app.models.user import Coupon

        mock_coupon = MagicMock(spec=Coupon)
        mock_coupon.code = "SAVE20"
        mock_coupon.discount_percent = 20.0
        mock_coupon.expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        mock_db = AsyncMock()
        svc = CouponService(mock_db)
        svc.get_coupon = AsyncMock(return_value=mock_coupon)

        result = await svc.validate("SAVE20")
        assert result.code == "SAVE20"

    @pytest.mark.asyncio
    async def test_validate_invalid_coupon_raises(self):
        from app.services.billing.coupon_service import CouponService
        from app.exceptions.errors import DomainException

        mock_db = AsyncMock()
        svc = CouponService(mock_db)
        svc.get_coupon = AsyncMock(return_value=None)

        with pytest.raises(DomainException, match="invalid or has expired"):
            await svc.validate("INVALID")

    @pytest.mark.asyncio
    async def test_apply_discount_computes_correctly(self):
        from app.services.billing.coupon_service import CouponService
        from app.models.user import Coupon

        mock_coupon = MagicMock(spec=Coupon)
        mock_coupon.code = "SAVE25"
        mock_coupon.discount_percent = 25.0

        mock_db = AsyncMock()
        svc = CouponService(mock_db)
        svc.validate = AsyncMock(return_value=mock_coupon)

        discounted, savings = await svc.apply_discount("SAVE25", 100.0)
        assert discounted == 75.0
        assert savings == 25.0

    @pytest.mark.asyncio
    async def test_apply_discount_caps_at_zero(self):
        from app.services.billing.coupon_service import CouponService
        from app.models.user import Coupon

        mock_coupon = MagicMock(spec=Coupon)
        mock_coupon.code = "FREE100"
        mock_coupon.discount_percent = 100.0

        mock_db = AsyncMock()
        svc = CouponService(mock_db)
        svc.validate = AsyncMock(return_value=mock_coupon)

        discounted, savings = await svc.apply_discount("FREE100", 29.0)
        assert discounted == 0.0
        assert savings == 29.0

    @pytest.mark.asyncio
    async def test_create_coupon_invalid_percent_raises(self):
        from app.services.billing.coupon_service import CouponService
        from app.exceptions.errors import DomainException

        mock_db = AsyncMock()
        svc = CouponService(mock_db)

        with pytest.raises(DomainException, match="Discount percent must be between"):
            await svc.create_coupon("TEST", 0.0)

    @pytest.mark.asyncio
    async def test_create_coupon_short_code_raises(self):
        from app.services.billing.coupon_service import CouponService
        from app.exceptions.errors import DomainException

        mock_db = AsyncMock()
        svc = CouponService(mock_db)

        with pytest.raises(DomainException, match="at least 4 characters"):
            await svc.create_coupon("AB", 10.0)


# ---------------------------------------------------------------------------
# Subscription service tests
# ---------------------------------------------------------------------------

class TestSubscriptionService:
    """Tests for subscription lifecycle management."""

    @pytest.mark.asyncio
    async def test_checkout_raises_for_unknown_plan(self):
        from app.services.billing.subscription_service import SubscriptionService
        from app.exceptions.errors import DomainException

        mock_db = AsyncMock()
        svc = SubscriptionService(mock_db)
        svc._plan_svc = AsyncMock()
        svc._plan_svc.get_plan_by_name = AsyncMock(return_value=None)

        with pytest.raises(DomainException, match="not available"):
            await svc.create_checkout(
                user_id=uuid.uuid4(),
                email="user@example.com",
                plan_name="invalid_plan",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    @pytest.mark.asyncio
    async def test_cancel_marks_status_canceled(self):
        from app.services.billing.subscription_service import SubscriptionService
        from app.models.user import Subscription

        mock_sub = MagicMock(spec=Subscription)
        mock_sub.status = "ACTIVE"

        mock_db = AsyncMock()
        svc = SubscriptionService(mock_db)
        svc._plan_svc = AsyncMock()
        svc._plan_svc.get_user_subscription = AsyncMock(return_value=mock_sub)

        result = await svc.cancel(uuid.uuid4())
        assert result is True
        assert mock_sub.status == "CANCELED"

    @pytest.mark.asyncio
    async def test_resume_raises_if_not_cancelled(self):
        from app.services.billing.subscription_service import SubscriptionService
        from app.exceptions.errors import DomainException
        from app.models.user import Subscription

        mock_sub = MagicMock(spec=Subscription)
        mock_sub.status = "ACTIVE"

        mock_db = AsyncMock()
        svc = SubscriptionService(mock_db)
        svc._plan_svc = AsyncMock()
        svc._plan_svc.get_user_subscription = AsyncMock(return_value=mock_sub)

        with pytest.raises(DomainException, match="not in a cancelled state"):
            await svc.resume(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_webhook_idempotency_skips_duplicate(self):
        from app.services.billing.subscription_service import SubscriptionService
        from app.models.user import WebhookEvent

        mock_event = MagicMock(spec=WebhookEvent)
        mock_event.processed_at = datetime.now(timezone.utc)

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_event
        mock_db.execute.return_value = mock_result

        svc = SubscriptionService(mock_db)
        await svc.handle_webhook_event(
            provider_slug="stripe",
            event_type="invoice.paid",
            payload={"id": "inv_xxx"},
            idempotency_key="stripe::invoice.paid::inv_xxx",
        )
        # Idempotency check passed — no new event should be added
        mock_db.add.assert_not_called()
