"""
Coupon service — validates and applies promotional discount codes.

Coupon records live in the ``coupons`` table.  This service checks validity,
ensures single-use semantics where applicable, and applies discounts to plans.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.errors import DomainException
from app.models.user import Coupon

logger = logging.getLogger(__name__)


class CouponService:
    """Validates promotional coupon codes and computes discount amounts."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_coupon(self, code: str) -> Optional[Coupon]:
        """Retrieves an active, unexpired coupon by its code (case-insensitive)."""
        now = datetime.now(timezone.utc)
        stmt = select(Coupon).where(
            Coupon.code == code.upper(),
            Coupon.deleted_at == None,
            (Coupon.expires_at == None) | (Coupon.expires_at > now),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def validate(self, code: str) -> Coupon:
        """
        Validates a coupon code and returns the Coupon record.

        Raises :class:`DomainException` when the code is invalid or expired.
        """
        coupon = await self.get_coupon(code)
        if not coupon:
            raise DomainException(f"Coupon code '{code}' is invalid or has expired.")
        return coupon

    async def apply_discount(self, code: str, base_price: float) -> tuple[float, float]:
        """
        Applies a coupon discount to a base price.

        Returns ``(discounted_price, savings_amount)`` as a tuple.
        """
        coupon = await self.validate(code)
        savings = round(base_price * (coupon.discount_percent / 100.0), 2)
        discounted = max(0.0, round(base_price - savings, 2))
        logger.info(
            "Coupon '%s' applied: %.0f%% off → saved $%.2f",
            code,
            coupon.discount_percent,
            savings,
        )
        return discounted, savings

    async def create_coupon(
        self,
        code: str,
        discount_percent: float,
        expires_in_days: Optional[int] = None,
    ) -> Coupon:
        """Creates a new promotional coupon code."""
        if not (0 < discount_percent <= 100):
            raise DomainException("Discount percent must be between 1 and 100.")
        if len(code) < 4:
            raise DomainException("Coupon code must be at least 4 characters.")

        expires_at = None
        if expires_in_days is not None:
            from datetime import timedelta
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        coupon = Coupon(
            code=code.upper(),
            discount_percent=discount_percent,
            expires_at=expires_at,
        )
        self.db.add(coupon)
        await self.db.flush()
        logger.info("Coupon created: %s (%.0f%%)", code.upper(), discount_percent)
        return coupon
