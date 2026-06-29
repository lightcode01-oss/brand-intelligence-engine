import json
import hmac
import hashlib
import httpx
from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class GenericWebhookAdapter(BaseIntegrationAdapter):
    """Adapter class implementing signed generic outbound webhooks."""
    
    def get_slug(self) -> str:
        return "webhook"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        webhook_url = settings.get("webhook_url")
        secret_key = settings.get("secret_key", "nomen_default_secret")
        if not webhook_url:
            logger.error("Generic Webhook integration missing 'webhook_url'.")
            return False
            
        serialized = json.dumps(payload)
        signature = hmac.new(
            secret_key.encode("utf-8"),
            serialized.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "X-Nomen-Signature": signature
        }
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(webhook_url, content=serialized, headers=headers)
                return res.status_code in [200, 201, 202, 204]
        except Exception as exc:
            logger.error(f"Generic Webhook delivery failed: {exc}")
            return False
