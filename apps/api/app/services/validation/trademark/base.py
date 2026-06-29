from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel

class TrademarkCheckResult(BaseModel):
    risk_status: str # 'CLEAR', 'WARNING', 'CONFLICT'
    serial_number: Optional[str]
    mark_text: str
    filing_date: Optional[str]
    registration_date: Optional[str]
    class_code: Optional[str]
    raw_payload: dict

class AbstractTrademarkProvider(ABC):
    """Abstract interface defining official trademark registry check adapters."""
    
    @abstractmethod
    def health(self) -> bool:
        """Verifies connection and credentials to registry portals API."""
        pass
        
    @abstractmethod
    async def check(self, name_string: str, jurisdiction: str) -> TrademarkCheckResult:
        """Checks for spelling and phonetics collisions in target registries."""
        pass
        
    @abstractmethod
    def normalize(self, name: str) -> str:
        """Standardizes strings for search criteria."""
        pass
        
    @abstractmethod
    def parse(self, raw_payload: dict) -> TrademarkCheckResult:
        """Translates raw JSON responses into unified check result objects."""
        pass
