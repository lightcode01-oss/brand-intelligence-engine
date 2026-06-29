import asyncio
from datetime import datetime, timezone
from sqlalchemy import update, select
from app.workers.celery_app import celery_app
from app.core.database import async_session_maker
from app.models.user import Subscription, CreditTransaction
from app.core.logging import logger

@celery_app.task
def reset_monthly_usage_limits() -> dict:
    """Scheduled task resetting monthly generation counts on the 1st of every month."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    async def reset():
        async with async_session_maker() as db:
            # Update all query counts back to 0
            stmt = update(Subscription).where(
                Subscription.deleted_at == None
            ).values(monthly_query_count=0)
            
            res = await db.execute(stmt)
            await db.commit()
            return res.rowcount
            
    try:
        updated = loop.run_until_complete(reset())
        logger.info(f"Monthly reset scheduler completed. Reset query counts for {updated} subscriptions.")
        return {"status": "SUCCESS", "reset_count": updated}
    except Exception as exc:
        logger.error(f"Monthly reset scheduler failed: {str(exc)}")
        return {"status": "FAILURE", "error": str(exc)}

@celery_app.task
def expire_outdated_credits() -> dict:
    """Scheduled task finding and marking expired credit transactions as used/expired."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    async def expire():
        async with async_session_maker() as db:
            now = datetime.now(timezone.utc)
            # Find credits that are past expiration and not yet marked used
            stmt = update(CreditTransaction).where(
                CreditTransaction.type == "CREDIT",
                CreditTransaction.expires_at != None,
                CreditTransaction.expires_at < now,
                CreditTransaction.used_at == None,
                CreditTransaction.deleted_at == None
            ).values(used_at=now)
            
            res = await db.execute(stmt)
            await db.commit()
            return res.rowcount
            
    try:
        expired = loop.run_until_complete(expire())
        logger.info(f"Credit expiration scheduler completed. Expired {expired} credit transactions.")
        return {"status": "SUCCESS", "expired_count": expired}
    except Exception as exc:
        logger.error(f"Credit expiration scheduler failed: {str(exc)}")
        return {"status": "FAILURE", "error": str(exc)}
