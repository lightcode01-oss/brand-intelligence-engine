from abc import ABC, abstractmethod
from pydantic import BaseModel

class SocialCheckResult(BaseModel):
    available: bool
    raw_payload: dict

class AbstractSocialProvider(ABC):
    """Abstract interface defining social profile handles availability checking adapters."""
    
    @abstractmethod
    def health(self) -> bool:
        """Verifies active token credentials and connectivity status."""
        pass
        
    @abstractmethod
    async def check(self, handle: str) -> SocialCheckResult:
        """Queries platform API to check profile username availability."""
        pass
        
    @abstractmethod
    def normalize(self, name: str) -> str:
        """Standardizes username handles strings (removes spaces and special chars)."""
        pass
        
    @abstractmethod
    def parse(self, raw_payload: dict) -> SocialCheckResult:
        """Parses API response payloads into a common checking result object."""
        pass
        
    @abstractmethod
    def get_platform_name(self) -> str:
        """Returns the unique platform identifier (e.g. 'github')."""
        pass
        
class AbstractSocialProviderRegistry(ABC):
    @abstractmethod
    def get_provider(self, platform: str) -> AbstractSocialProvider:
        pass
