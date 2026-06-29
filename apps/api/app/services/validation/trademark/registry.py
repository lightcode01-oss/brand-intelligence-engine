import os
from app.services.validation.trademark.base import AbstractTrademarkProvider
from app.services.validation.trademark.mock import MockTrademarkProvider
from app.services.validation.trademark.uspto import UsptoTrademarkProvider
from app.services.validation.trademark.euipo import EuipoTrademarkProvider
from app.services.validation.trademark.ukipo import UkipoTrademarkProvider
from app.services.validation.trademark.india import IndiaTrademarkProvider

class TrademarkProviderRegistry:
    """Discovers and resolves the active trademark checking adapter based on target jurisdiction."""
    
    def __init__(self):
        self._providers = {
            "mock": MockTrademarkProvider(),
            "us": UsptoTrademarkProvider(),
            "eu": EuipoTrademarkProvider(),
            "uk": UkipoTrademarkProvider(),
            "in": IndiaTrademarkProvider()
        }
        
    def get_provider(self, name: str = None) -> AbstractTrademarkProvider:
        """Retrieves active provider matching name key, falling back to 'mock' if missing."""
        provider_name = name or os.getenv("TRADEMARK_PROVIDER", "mock")
        return self._providers.get(provider_name.lower(), self._providers["mock"])
