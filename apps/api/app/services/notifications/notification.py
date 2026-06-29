import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Notification, User
from app.services.notifications.email import AbstractEmailProvider, MockEmailProvider

class NotificationEngine:
    """Dispatches in-app alerts and email notifications to users."""
    
    def __init__(self, db: AsyncSession, email_provider: AbstractEmailProvider = None):
        self.db = db
        self.email = email_provider or MockEmailProvider()
        
    async def send_in_app_notification(self, user_id: uuid.UUID, title: str, message: str) -> Notification:
        """Saves a notification to the database for retrieval inside the web dashboard."""
        alert = Notification(
            user_id=user_id,
            type="IN_APP",
            title=title,
            message=message
        )
        self.db.add(alert)
        await self.db.flush()
        return alert
        
    async def send_email_alert(self, user_id: uuid.UUID, email_address: str, title: str, message: str) -> bool:
        """Triggers an email notification via the configured email provider and registers a notification log."""
        # 1. Dispatch email
        sent = await self.email.send_email(email_address, title, message)
        
        # 2. Log database event
        alert = Notification(
            user_id=user_id,
            type="EMAIL",
            title=title,
            message=message
        )
        self.db.add(alert)
        await self.db.flush()
        return sent
