from app.services.validation.domain.base import AbstractDomainProvider, DomainCheckResult
from app.services.validation.domain.mock import MockDomainProvider

class NamecheapDomainProvider(MockDomainProvider):
    """Adapter class wrapping Namecheap API endpoints."""
    pass
