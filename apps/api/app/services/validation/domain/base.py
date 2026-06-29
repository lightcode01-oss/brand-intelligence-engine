from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel

class DomainCheckResult(BaseModel):
    available: bool
    price: Optional[float]
    raw_payload: dict

class AbstractDomainProvider(ABC):
    """Abstract interface defining domain registration checks adapters."""
    
    @abstractmethod
    def health(self) -> bool:
        """Verifies API key credentials and connectivity status."""
        pass
        
    @abstractmethod
    async def check(self, domain_name: str, tld: str) -> DomainCheckResult:
        """Queries registrar API to inspect domain registration status."""
        pass
        
    @abstractmethod
    def normalize(self, name: str) -> str:
        """Cleans and standardizes input domain strings."""
        pass
        
    @abstractmethod
    def parse(self, raw_payload: dict) -> DomainCheckResult:
        """Parses raw provider response payloads into standard result envelopes."""
        pass
