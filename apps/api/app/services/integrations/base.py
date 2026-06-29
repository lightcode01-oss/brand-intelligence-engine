from abc import ABC, abstractmethod

class BaseIntegrationAdapter(ABC):
    """Abstract interface defining the dispatch contract for outbound marketing/notifications platforms."""
    
    @abstractmethod
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        """Sends payload message to configured webhook / endpoint."""
        pass
        
    @abstractmethod
    def get_slug(self) -> str:
        """Returns the unique identifier of the integration."""
        pass
