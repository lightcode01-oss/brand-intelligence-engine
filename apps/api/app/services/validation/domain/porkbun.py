from app.services.validation.domain.base import AbstractDomainProvider, DomainCheckResult
from app.services.validation.domain.mock import MockDomainProvider

class PorkbunDomainProvider(MockDomainProvider):
    """Adapter class wrapping Porkbun API endpoints."""
    pass
