import httpx
from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class SlackIntegrationAdapter(BaseIntegrationAdapter):
    """Adapter class implementing Slack Incoming Webhook interface."""
    
    def get_slug(self) -> str:
        return "slack"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        webhook_url = settings.get("webhook_url")
        if not webhook_url:
            logger.error("Slack integration missing 'webhook_url'.")
            return False
            
        title = payload.get("title", "Nomen Notification")
        message = payload.get("message", "")
        
        slack_payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title,
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{message}\n\n*Details:* {str(payload.get('data_json', {}))}"
                    }
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(webhook_url, json=slack_payload)
                return res.status_code in [200, 201]
        except Exception as exc:
            logger.error(f"Slack integration delivery failed: {exc}")
            return False
