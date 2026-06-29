import httpx
from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class ZapierIntegrationAdapter(BaseIntegrationAdapter):
    """Adapter class implementing Zapier webhook triggers."""
    
    def get_slug(self) -> str:
        return "zapier"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        webhook_url = settings.get("webhook_url")
        if not webhook_url:
            logger.error("Zapier integration missing 'webhook_url'.")
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(webhook_url, json=payload)
                return res.status_code in [200, 201]
        except Exception as exc:
            logger.error(f"Zapier integration delivery failed: {exc}")
            return False
