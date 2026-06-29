"""
Billing API routes — exposes subscription management, checkout, and usage data.

Routes:
    POST   /billing/checkout          — Create checkout session
    POST   /billing/portal            — Launch customer billing portal
    GET    /billing/plans             — List all available plans
    GET    /billing/invoices          — List user invoices
    GET    /billing/usage             — Get usage summary
    POST   /billing/cancel            — Cancel subscription
    POST   /billing/resume            — Resume cancelled subscription
    POST   /billing/apply-coupon      — Validate and preview coupon discount
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field

from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.exceptions.errors import DomainException
from app.models.user import User, Plan, Invoice, Subscription
from app.schemas.response import StandardResponse, wrap_success_response
from app.services.billing.coupon_service import CouponService
from app.services.billing.invoice_service import InvoiceService
from app.services.billing.plan_service import PlanService
from app.services.billing.subscription_service import SubscriptionService
from app.services.billing.usage_service import UsageService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/billing", tags=["Billing & Subscriptions"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class CheckoutRequest(BaseModel):
    plan_name: str = Field(..., description="Target plan slug (free, starter, pro, business, enterprise)")
    success_url: str = Field(..., description="URL to redirect to after successful checkout")
    cancel_url: str = Field(..., description="URL to redirect to when checkout is cancelled")
    trial_days: int = Field(0, ge=0, le=90, description="Number of trial days to apply")
    coupon_code: Optional[str] = Field(None, description="Optional promotional coupon code")
    provider: Optional[str] = Field(None, description="Payment gateway slug (stripe or lemonsqueezy)")


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    provider: str


class PortalRequest(BaseModel):
    return_url: str = Field(..., description="URL to return to after closing the portal")
    provider: Optional[str] = Field(None)


class PortalResponse(BaseModel):
    portal_url: str
    provider: str


class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    price_monthly: float
    limits: dict
    features: dict
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    amount: float
    currency: str
    status: str
    billing_reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    tier: str
    status: str
    limit_reset_at: datetime
    monthly_query_count: int

    class Config:
        from_attributes = True


class CancelRequest(BaseModel):
    provider: Optional[str] = Field(None)


class ResumeRequest(BaseModel):
    provider: Optional[str] = Field(None)


class CouponRequest(BaseModel):
    code: str = Field(..., min_length=4)
    plan_name: str = Field(..., description="Plan to apply the coupon to")


class CouponResponse(BaseModel):
    code: str
    discount_percent: float
    original_price: float
    discounted_price: float
    savings: float
    valid: bool


# ---------------------------------------------------------------------------
# Endpoint handlers
# ---------------------------------------------------------------------------

@router.post(
    "/checkout",
    response_model=StandardResponse[CheckoutResponse],
    status_code=status.HTTP_200_OK,
    summary="Create checkout session",
)
async def create_checkout(
    request: Request,
    body: CheckoutRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[CheckoutResponse]:
    """Creates a hosted checkout session for purchasing a subscription plan."""
    coupon_id = None
    if body.coupon_code:
        coupon_svc = CouponService(db)
        coupon = await coupon_svc.validate(body.coupon_code)
        coupon_id = coupon.code  # Providers accept the coupon code

    svc = SubscriptionService(db)
    session = await svc.create_checkout(
        user_id=current_user.id,
        email=current_user.email,
        plan_name=body.plan_name,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        trial_days=body.trial_days,
        coupon_id=coupon_id,
        provider_slug=body.provider,
    )

    await db.commit()
    return wrap_success_response(
        CheckoutResponse(
            checkout_url=session.checkout_url,
            session_id=session.session_id,
            provider=session.provider,
        ),
        request,
        "Checkout session created successfully.",
    )


@router.post(
    "/portal",
    response_model=StandardResponse[PortalResponse],
    summary="Open customer portal",
)
async def create_portal(
    request: Request,
    body: PortalRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[PortalResponse]:
    """Generates a self-service billing portal URL for the authenticated user."""
    svc = SubscriptionService(db)
    portal = await svc.create_portal_session(
        user_id=current_user.id,
        return_url=body.return_url,
        provider_slug=body.provider,
    )
    return wrap_success_response(
        PortalResponse(portal_url=portal.portal_url, provider=portal.provider),
        request,
        "Billing portal session created.",
    )


@router.get(
    "/plans",
    response_model=StandardResponse[list[PlanResponse]],
    summary="List available plans",
)
async def list_plans(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> StandardResponse[list[PlanResponse]]:
    """Returns all publicly available subscription plans."""
    plan_svc = PlanService(db)
    plans = await plan_svc.list_plans()
    return wrap_success_response(
        [
            PlanResponse(
                id=p.id,
                name=p.name,
                price_monthly=p.price_monthly,
                limits=p.limits_json,
                features=p.features_json,
                created_at=p.created_at,
            )
            for p in plans
        ],
        request,
        f"{len(plans)} plans available.",
    )


@router.get(
    "/invoices",
    response_model=StandardResponse[list[InvoiceResponse]],
    summary="List billing invoices",
)
async def list_invoices(
    request: Request,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[list[InvoiceResponse]]:
    """Returns the billing invoice history for the authenticated user."""
    inv_svc = InvoiceService(db)
    invoices = await inv_svc.list_user_invoices(current_user.id, limit=limit)
    return wrap_success_response(
        [
            InvoiceResponse(
                id=inv.id,
                amount=inv.amount,
                currency=inv.currency,
                status=inv.status,
                billing_reason=inv.billing_reason,
                created_at=inv.created_at,
            )
            for inv in invoices
        ],
        request,
        f"{len(invoices)} invoices retrieved.",
    )


@router.get(
    "/usage",
    response_model=StandardResponse[dict],
    summary="Get usage summary",
)
async def get_usage(
    request: Request,
    workspace_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[dict]:
    """Returns the current billing period usage summary for the authenticated user."""
    # Use first workspace if none provided
    if not workspace_id:
        from app.models.workspace import Workspace
        from sqlalchemy import select
        stmt = select(Workspace).where(
            Workspace.deleted_at == None
        ).limit(1)
        ws = (await db.execute(stmt)).scalar_one_or_none()
        workspace_id = ws.id if ws else uuid.uuid4()

    usage_svc = UsageService(db)
    summary = await usage_svc.get_usage_summary(current_user.id, workspace_id)
    return wrap_success_response(summary, request, "Usage summary retrieved.")


@router.post(
    "/cancel",
    response_model=StandardResponse[dict],
    summary="Cancel subscription",
)
async def cancel_subscription(
    request: Request,
    body: CancelRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[dict]:
    """Cancels the current user's subscription at the end of the billing period."""
    svc = SubscriptionService(db)
    await svc.cancel(current_user.id, provider_slug=body.provider)
    await db.commit()
    return wrap_success_response(
        {"cancelled": True},
        request,
        "Subscription cancelled. You retain access until the end of the billing period.",
    )


@router.post(
    "/resume",
    response_model=StandardResponse[SubscriptionResponse],
    summary="Resume subscription",
)
async def resume_subscription(
    request: Request,
    body: ResumeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[SubscriptionResponse]:
    """Resumes a subscription that was scheduled for cancellation."""
    svc = SubscriptionService(db)
    sub = await svc.resume(current_user.id, provider_slug=body.provider)
    await db.commit()
    return wrap_success_response(
        SubscriptionResponse(
            id=sub.id,
            tier=sub.tier,
            status=sub.status,
            limit_reset_at=sub.limit_reset_at,
            monthly_query_count=sub.monthly_query_count,
        ),
        request,
        "Subscription resumed successfully.",
    )


@router.post(
    "/apply-coupon",
    response_model=StandardResponse[CouponResponse],
    summary="Preview coupon discount",
)
async def apply_coupon(
    request: Request,
    body: CouponRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[CouponResponse]:
    """Validates a coupon code and returns a pricing preview without applying charges."""
    plan_svc = PlanService(db)
    plan = await plan_svc.get_plan_by_name(body.plan_name)
    if not plan:
        raise DomainException(f"Plan '{body.plan_name}' not found.")

    coupon_svc = CouponService(db)
    discounted_price, savings = await coupon_svc.apply_discount(body.code, plan.price_monthly)
    coupon = await coupon_svc.get_coupon(body.code)

    return wrap_success_response(
        CouponResponse(
            code=body.code.upper(),
            discount_percent=coupon.discount_percent,
            original_price=plan.price_monthly,
            discounted_price=discounted_price,
            savings=savings,
            valid=True,
        ),
        request,
        f"Coupon '{body.code.upper()}' is valid. You save ${savings:.2f}/month.",
    )
