from app.services.validation.domain.base import AbstractDomainProvider, DomainCheckResult
from app.services.validation.domain.mock import MockDomainProvider

class GoDaddyDomainProvider(MockDomainProvider):
    """Adapter class wrapping GoDaddy Developer API endpoints."""
    pass
