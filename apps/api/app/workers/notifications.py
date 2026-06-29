import asyncio
from app.workers.celery_app import celery_app
from app.services.notifications.email import MockEmailProvider
from app.core.logging import logger

@celery_app.task(bind=True, max_retries=3)
def async_send_mention_notification_task(
    self, email_address: str, mentioner_name: str, comment_preview: str
) -> bool:
    """Dispatches email notification alerts asynchronously when a user is mentioned."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    email = MockEmailProvider()
    subject = f"You were mentioned by {mentioner_name} on Nomen"
    message = (
        f"Hi,\n\n"
        f"{mentioner_name} mentioned you in a comment:\n\n"
        f"\"{comment_preview}\"\n\n"
        f"Log in to Nomen to view and reply.\n\n"
        f"Best,\n"
        f"Nomen Team"
    )

    try:
        sent = loop.run_until_complete(
            email.send_email(
                recipient=email_address,
                subject=subject,
                body=message
            )
        )
        logger.info(f"Asynchronous email mention alert dispatched to {email_address}. Success: {sent}")
        return sent
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
