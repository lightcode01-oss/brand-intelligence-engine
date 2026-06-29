from app.services.validation.domain.base import AbstractDomainProvider, DomainCheckResult
from app.services.validation.domain.mock import MockDomainProvider

class CloudflareDomainProvider(MockDomainProvider):
    """Adapter class wrapping Cloudflare Registrar API endpoints."""
    # Extends Mock for now, ready to override methods with actual HTTP requests
    pass
