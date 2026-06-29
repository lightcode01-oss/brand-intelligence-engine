import os
from app.services.validation.domain.base import AbstractDomainProvider
from app.services.validation.domain.mock import MockDomainProvider
from app.services.validation.domain.cloudflare import CloudflareDomainProvider
from app.services.validation.domain.godaddy import GoDaddyDomainProvider
from app.services.validation.domain.namecheap import NamecheapDomainProvider
from app.services.validation.domain.porkbun import PorkbunDomainProvider

class DomainProviderRegistry:
    """Discovers and resolves the active domain registrar checking adapter."""
    
    def __init__(self):
        self._providers = {
            "mock": MockDomainProvider(),
            "cloudflare": CloudflareDomainProvider(),
            "godaddy": GoDaddyDomainProvider(),
            "namecheap": NamecheapDomainProvider(),
            "porkbun": PorkbunDomainProvider()
        }
        
    def get_provider(self, name: str = None) -> AbstractDomainProvider:
        """Retrieves active provider matching name key, falling back to 'mock' if missing."""
        provider_name = name or os.getenv("DOMAIN_PROVIDER", "mock")
        return self._providers.get(provider_name.lower(), self._providers["mock"])
