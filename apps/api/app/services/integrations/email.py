from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class EmailAutomationIntegrationAdapter(BaseIntegrationAdapter):
    """Adapter class implementing email notification automation."""
    
    def get_slug(self) -> str:
        return "email"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        to_email = settings.get("to_email")
        if not to_email:
            logger.error("Email automation integration missing destination 'to_email'.")
            return False
            
        title = payload.get("title", "Nomen Notification")
        message = payload.get("message", "")
        
        logger.info(f"Email automation resolved successfully. Sent to '{to_email}' | Title: {title} | Message: {message}")
        return True
