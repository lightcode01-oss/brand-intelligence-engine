import httpx
from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class TeamsIntegrationAdapter(BaseIntegrationAdapter):
    """Adapter class implementing Microsoft Teams Office 365 Connector cards."""
    
    def get_slug(self) -> str:
        return "teams"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        webhook_url = settings.get("webhook_url")
        if not webhook_url:
            logger.error("MS Teams integration missing 'webhook_url'.")
            return False
            
        title = payload.get("title", "Nomen Notification")
        message = payload.get("message", "")
        
        teams_payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "4f46e5",
            "summary": title,
            "sections": [
                {
                    "activityTitle": title,
                    "activitySubtitle": message,
                    "facts": [
                        {"name": "Payload", "value": str(payload.get("data_json", {}))}
                    ]
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(webhook_url, json=teams_payload)
                return res.status_code in [200, 201]
        except Exception as exc:
            logger.error(f"MS Teams integration delivery failed: {exc}")
            return False
