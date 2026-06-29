"""
Webhook receiver endpoint — processes payment gateway events.

Supports Stripe and Lemon Squeezy.  Each provider's signature is verified
before the payload is processed.  Idempotency is enforced in the
SubscriptionService layer.

Routes:
    POST /webhooks/stripe
    POST /webhooks/lemonsqueezy
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.dependencies.database import get_db_session
from app.services.billing.providers.registry import get_billing_registry
from app.services.billing.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

async def _handle_webhook(
    provider_slug: str,
    raw_body: bytes,
    signature_header: str,
    background_tasks: BackgroundTasks,
) -> dict:
    registry = get_billing_registry()
    try:
        provider = registry.get(provider_slug)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_slug}")

    # 1. Verify signature
    if not provider.verify_webhook_signature(raw_body, signature_header):
        logger.warning("Invalid webhook signature from provider: %s", provider_slug)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook signature verification failed.",
        )

    # 2. Parse event
    event_type, payload = provider.parse_webhook_event(raw_body)

    # 3. Extract idempotency key from payload
    idempotency_key = payload.get("id") or payload.get("data", {}).get("id", "unknown")

    # 4. Process in background to return 200 immediately (recommended by all providers)
    background_tasks.add_task(
        _process_event,
        provider_slug=provider_slug,
        event_type=event_type,
        payload=payload,
        idempotency_key=f"{provider_slug}::{event_type}::{idempotency_key}",
    )

    return {"received": True}


async def _process_event(
    provider_slug: str,
    event_type: str,
    payload: dict,
    idempotency_key: str,
) -> None:
    """Background task that processes the webhook event with a fresh DB session."""
    try:
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            async with db.begin():
                svc = SubscriptionService(db)
                await svc.handle_webhook_event(
                    provider_slug=provider_slug,
                    event_type=event_type,
                    payload=payload,
                    idempotency_key=idempotency_key,
                )
        logger.info("Webhook processed: %s / %s", provider_slug, event_type)
    except Exception as exc:
        logger.error(
            "Webhook processing failed [%s/%s]: %s",
            provider_slug,
            event_type,
            exc,
            exc_info=True,
        )


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

@router.post(
    "/stripe",
    status_code=status.HTTP_200_OK,
    summary="Stripe Webhook Receiver",
    description="Receives and processes signed webhook events from Stripe.",
)
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None, alias="stripe-signature"),
) -> dict:
    raw_body = await request.body()
    return await _handle_webhook(
        provider_slug="stripe",
        raw_body=raw_body,
        signature_header=stripe_signature or "",
        background_tasks=background_tasks,
    )


@router.post(
    "/lemonsqueezy",
    status_code=status.HTTP_200_OK,
    summary="Lemon Squeezy Webhook Receiver",
    description="Receives and processes signed webhook events from Lemon Squeezy.",
)
async def lemonsqueezy_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str = Header(None, alias="X-Signature"),
) -> dict:
    raw_body = await request.body()
    return await _handle_webhook(
        provider_slug="lemonsqueezy",
        raw_body=raw_body,
        signature_header=x_signature or "",
        background_tasks=background_tasks,
    )
