"""
Abstract base interface for all external payment gateway providers.

Every concrete provider must implement this contract so the billing layer
can remain fully provider-agnostic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class CheckoutSession:
    """Represents a hosted checkout URL returned by a provider."""
    session_id: str
    checkout_url: str
    provider: str
    metadata: dict = field(default_factory=dict)


@dataclass
class PortalSession:
    """Represents a customer billing-portal URL returned by a provider."""
    portal_url: str
    provider: str


@dataclass
class ProviderSubscription:
    """Normalised subscription record from any provider."""
    subscription_id: str
    customer_id: str
    plan_id: str
    status: str          # active | canceled | past_due | trialing | paused
    current_period_end: Optional[str] = None
    trial_end: Optional[str] = None
    cancel_at_period_end: bool = False
    provider: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class ProviderInvoice:
    """Normalised invoice record from any provider."""
    invoice_id: str
    customer_id: str
    amount_paid: float       # in major units (USD)
    currency: str
    status: str              # paid | open | void | uncollectible
    invoice_url: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: Optional[str] = None
    provider: str = ""
    raw: dict = field(default_factory=dict)


class AbstractPaymentProvider(ABC):
    """
    Abstract gateway contract that every payment provider must implement.

    Concrete implementations: StripeProvider, LemonSqueezyProvider.
    New providers simply subclass this and register themselves in the registry.
    """

    # Unique slug, e.g. "stripe", "lemonsqueezy".  Set in each subclass.
    provider_name: str = ""

    # -----------------------------------------------------------------
    # Customer lifecycle
    # -----------------------------------------------------------------

    @abstractmethod
    async def create_customer(self, user_id: uuid.UUID, email: str, name: Optional[str] = None) -> str:
        """
        Registers the user as a customer in the payment gateway.

        Returns the provider-assigned customer ID (e.g. ``cus_xxx``).
        """

    @abstractmethod
    async def get_customer_id(self, user_id: uuid.UUID) -> Optional[str]:
        """
        Retrieves the stored provider customer ID for a user.

        Returns ``None`` when the user has not yet been registered.
        """

    # -----------------------------------------------------------------
    # Checkout & portal
    # -----------------------------------------------------------------

    @abstractmethod
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
        """
        Creates a hosted checkout page for a subscription purchase.

        Returns a :class:`CheckoutSession` containing the redirect URL.
        """

    @abstractmethod
    async def create_customer_portal(self, customer_id: str, return_url: str) -> PortalSession:
        """
        Generates a short-lived customer self-service portal URL.

        Customers use this to update payment methods, download invoices and
        manage their subscription without contacting support.
        """

    # -----------------------------------------------------------------
    # Subscription management
    # -----------------------------------------------------------------

    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> ProviderSubscription:
        """Retrieves the current state of a subscription from the gateway."""

    @abstractmethod
    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> ProviderSubscription:
        """
        Switches the customer to a higher-tier plan immediately with proration.
        """

    @abstractmethod
    async def downgrade_subscription(self, subscription_id: str, new_plan_id: str) -> ProviderSubscription:
        """
        Switches the customer to a lower-tier plan at the next billing cycle.
        """

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """
        Cancels a subscription.

        When ``immediate=False`` (default) the subscription remains active until
        the end of the current billing period.  When ``True`` it is terminated
        instantly and no refund is issued.
        """

    @abstractmethod
    async def resume_subscription(self, subscription_id: str) -> ProviderSubscription:
        """
        Re-activates a subscription that was previously scheduled for cancellation.

        Only valid when ``cancel_at_period_end=True`` and the period has not yet ended.
        """

    # -----------------------------------------------------------------
    # Invoices
    # -----------------------------------------------------------------

    @abstractmethod
    async def list_invoices(self, customer_id: str, limit: int = 20) -> list[ProviderInvoice]:
        """Returns the most recent invoices for a customer, newest first."""

    # -----------------------------------------------------------------
    # Webhook verification
    # -----------------------------------------------------------------

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature_header: str) -> bool:
        """
        Validates the HMAC / asymmetric signature on an incoming webhook payload.

        Returns ``True`` when the signature is authentic, ``False`` otherwise.
        Raise no exception; return False on any verification failure so callers
        can return HTTP 400 safely.
        """

    @abstractmethod
    def parse_webhook_event(self, payload: bytes) -> tuple[str, dict]:
        """
        Parses the raw webhook body into a normalised ``(event_type, data)`` pair.

        ``event_type`` values follow the canonical Nomen schema:
        ``checkout.completed``, ``subscription.created``, ``subscription.updated``,
        ``subscription.cancelled``, ``invoice.paid``, ``invoice.payment_failed``,
        ``refund.created``.
        """
