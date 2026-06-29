from typing import Dict, Optional
from app.services.integrations.base import BaseIntegrationAdapter
from app.services.integrations.slack import SlackIntegrationAdapter
from app.services.integrations.discord import DiscordIntegrationAdapter
from app.services.integrations.teams import TeamsIntegrationAdapter
from app.services.integrations.zapier import ZapierIntegrationAdapter
from app.services.integrations.webhook import GenericWebhookAdapter
from app.services.integrations.github import GitHubActionsIntegrationAdapter
from app.services.integrations.email import EmailAutomationIntegrationAdapter
from app.core.logging import logger

class IntegrationRegistry:
    """Discovers and dispatches events through active integration adapters."""
    
    def __init__(self):
        self._adapters: Dict[str, BaseIntegrationAdapter] = {}
        self._register_adapters()
        
    def _register_adapters(self) -> None:
        adapters = [
            SlackIntegrationAdapter(),
            DiscordIntegrationAdapter(),
            TeamsIntegrationAdapter(),
            ZapierIntegrationAdapter(),
            GenericWebhookAdapter(),
            GitHubActionsIntegrationAdapter(),
            EmailAutomationIntegrationAdapter()
        ]
        for adapter in adapters:
            self._adapters[adapter.get_slug()] = adapter
            
    def get_adapter(self, slug: str) -> Optional[BaseIntegrationAdapter]:
        return self._adapters.get(slug)
        
    async def dispatch(self, adapter_slug: str, payload: dict, settings: dict) -> bool:
        adapter = self.get_adapter(adapter_slug)
        if not adapter:
            logger.error(f"Integration adapter '{adapter_slug}' not found in registry.")
            return False
            
        logger.info(f"Dispatching notification via integration '{adapter_slug}'...")
        success = await adapter.send_notification(payload, settings)
        if success:
            logger.info(f"Notification delivered successfully via '{adapter_slug}'.")
        else:
            logger.error(f"Notification delivery failed via '{adapter_slug}'.")
        return success

# Global instance
integration_registry = IntegrationRegistry()
