"""
Invoice service — synchronises and retrieves invoice records.

Combines locally-stored Invoice records with live provider data for a
complete billing history view.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Invoice
from app.services.billing.providers.base import ProviderInvoice
from app.services.billing.providers.registry import get_billing_registry

logger = logging.getLogger(__name__)


class InvoiceService:
    """Retrieves and synchronises invoice records from provider and local DB."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_user_invoices(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        provider_slug: Optional[str] = None,
    ) -> list[Invoice]:
        """
        Returns invoice records for the user, preferring local DB records.

        Falls back to live provider data when no local records exist.
        """
        stmt = (
            select(Invoice)
            .where(Invoice.user_id == user_id, Invoice.deleted_at == None)
            .order_by(Invoice.created_at.desc())
            .limit(limit)
        )
        local_invoices = list((await self.db.execute(stmt)).scalars().all())
        if local_invoices:
            return local_invoices

        # Attempt to fetch from provider
        try:
            registry = get_billing_registry()
            provider = registry.get(provider_slug) if provider_slug else registry.get_primary()
            customer_id = await provider.get_customer_id(user_id)
            if customer_id:
                provider_invoices = await provider.list_invoices(customer_id, limit=limit)
                # Persist and return
                synced = await self._sync_provider_invoices(user_id, provider_invoices)
                return synced
        except Exception as exc:
            logger.warning("Failed to fetch provider invoices for user %s: %s", user_id, exc)

        return []

    async def _sync_provider_invoices(
        self, user_id: uuid.UUID, provider_invoices: list[ProviderInvoice]
    ) -> list[Invoice]:
        """Persists provider invoice records locally and returns the Invoice ORM objects."""
        synced: list[Invoice] = []
        for pi in provider_invoices:
            status_map = {"paid": "PAID", "open": "OPEN", "void": "VOID", "uncollectible": "VOID"}
            inv = Invoice(
                user_id=user_id,
                amount=pi.amount_paid,
                currency=pi.currency,
                status=status_map.get(pi.status, "OPEN"),
                billing_reason=f"Subscription invoice via {pi.provider}",
                raw_payload=pi.raw,
            )
            self.db.add(inv)
            synced.append(inv)
        if synced:
            await self.db.flush()
        return synced

    async def get_invoice_by_id(self, invoice_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Invoice]:
        """Returns a specific invoice if it belongs to the given user."""
        stmt = select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id,
            Invoice.deleted_at == None,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
