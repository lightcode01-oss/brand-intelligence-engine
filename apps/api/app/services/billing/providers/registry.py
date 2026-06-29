"""
Provider registry — discovers and manages active billing gateway providers.

Providers are resolved at application startup from ``settings.BILLING_PROVIDER``
(default: ``"stripe"``).  Additional providers can be registered at runtime.

Usage::

    registry = BillingProviderRegistry.from_settings()
    provider = registry.get("stripe")
    session = await provider.create_checkout_session(...)
"""

import logging
from typing import Optional

from app.core.config import settings
from app.services.billing.providers.base import AbstractPaymentProvider

logger = logging.getLogger(__name__)

# Lazy imports to avoid hard-coupling at module load time
_PROVIDER_MAP: dict[str, str] = {
    "stripe": "app.services.billing.providers.stripe.StripeProvider",
    "lemonsqueezy": "app.services.billing.providers.lemonsqueezy.LemonSqueezyProvider",
}


def _load_provider_class(dotted_path: str) -> type:
    """Dynamically imports and returns a provider class from a dotted module path."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class BillingProviderRegistry:
    """
    Thread-safe registry that holds one singleton instance per provider slug.

    Priority is determined by ``settings.BILLING_PROVIDER`` (primary) and
    ``settings.BILLING_PROVIDER_FALLBACK`` (secondary).  The ``get_primary()``
    method returns the highest-priority *healthy* provider.
    """

    def __init__(self) -> None:
        self._instances: dict[str, AbstractPaymentProvider] = {}
        self._primary: str = ""
        self._fallback: Optional[str] = None

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_settings(cls) -> "BillingProviderRegistry":
        """Bootstraps the registry from application settings."""
        registry = cls()
        primary = getattr(settings, "BILLING_PROVIDER", "stripe").lower()
        fallback = getattr(settings, "BILLING_PROVIDER_FALLBACK", None)
        if fallback:
            fallback = fallback.lower()

        # Register primary
        registry.register(primary)
        registry._primary = primary

        # Register fallback if configured
        if fallback and fallback != primary:
            registry.register(fallback)
            registry._fallback = fallback

        logger.info(
            "BillingProviderRegistry initialised — primary=%s fallback=%s",
            primary,
            fallback,
        )
        return registry

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, slug: str) -> None:
        """
        Instantiates and stores a provider by its slug.

        Only slugs present in ``_PROVIDER_MAP`` are accepted.  To add a new
        gateway, add an entry there and create the concrete class.
        """
        slug = slug.lower()
        if slug in self._instances:
            return  # Already registered
        if slug not in _PROVIDER_MAP:
            raise ValueError(
                f"Unknown billing provider slug '{slug}'. "
                f"Available: {list(_PROVIDER_MAP.keys())}"
            )
        ProviderClass = _load_provider_class(_PROVIDER_MAP[slug])
        self._instances[slug] = ProviderClass()
        logger.debug("Registered billing provider: %s", slug)

    def register_custom(self, slug: str, instance: AbstractPaymentProvider) -> None:
        """Registers an externally instantiated provider (useful in tests)."""
        self._instances[slug.lower()] = instance

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, slug: str) -> AbstractPaymentProvider:
        """Returns a specific provider by slug, raising ``KeyError`` if not found."""
        slug = slug.lower()
        if slug not in self._instances:
            raise KeyError(f"Provider '{slug}' is not registered.")
        return self._instances[slug]

    def get_primary(self) -> AbstractPaymentProvider:
        """Returns the primary configured provider."""
        return self.get(self._primary)

    def get_fallback(self) -> Optional[AbstractPaymentProvider]:
        """Returns the fallback provider, or None if none is configured."""
        if self._fallback:
            return self.get(self._fallback)
        return None

    def available_slugs(self) -> list[str]:
        """Returns the slugs of all currently registered providers."""
        return list(self._instances.keys())


# ---------------------------------------------------------------------------
# Module-level singleton — initialised once at import time
# ---------------------------------------------------------------------------
_registry_instance: Optional[BillingProviderRegistry] = None


def get_billing_registry() -> BillingProviderRegistry:
    """
    Returns the module-level singleton registry.

    Creates and initialises it on first call.  Thread-safe for CPython
    (GIL guarantees atomic assignment).
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = BillingProviderRegistry.from_settings()
    return _registry_instance
