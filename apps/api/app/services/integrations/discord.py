import httpx
from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class DiscordIntegrationAdapter(BaseIntegrationAdapter):
    """Adapter class implementing Discord Webhook interfaces."""
    
    def get_slug(self) -> str:
        return "discord"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        webhook_url = settings.get("webhook_url")
        if not webhook_url:
            logger.error("Discord integration missing 'webhook_url'.")
            return False
            
        title = payload.get("title", "Nomen Notification")
        message = payload.get("message", "")
        
        discord_payload = {
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": 0x4f46e5,  # Indigo primary theme
                    "fields": [
                        {
                            "name": "Data Payload",
                            "value": f"```{str(payload.get('data_json', {}))[:1000]}```"
                        }
                    ]
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(webhook_url, json=discord_payload)
                return res.status_code in [200, 204]
        except Exception as exc:
            logger.error(f"Discord integration delivery failed: {exc}")
            return False
