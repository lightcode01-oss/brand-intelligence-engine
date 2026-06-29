import uuid
from abc import abstractmethod
from typing import Optional
from app.services.base import AbstractService
from app.models.user import User, Subscription

class AbstractUserService(AbstractService):
    """Abstract interface defining user management capabilities."""
    
    @abstractmethod
    async def register_user(self, email: str, password_raw: str) -> User:
        """Signs up a new user account."""
        pass
        
    @abstractmethod
    async def authenticate_user(self, email: str, password_raw: str) -> User:
        """Verifies email credentials and returns the active user profile."""
        pass
        
    @abstractmethod
    async def get_user_profile(self, user_id: uuid.UUID) -> User:
        """Retrieves profile records for a user ID."""
        pass

class AbstractBillingService(AbstractService):
    """Abstract interface defining subscription management and quota checks."""
    
    @abstractmethod
    async def get_subscription(self, user_id: uuid.UUID) -> Subscription:
        """Retrieves subscription details for a user ID."""
        pass
        
    @abstractmethod
    async def upgrade_subscription_tier(self, user_id: uuid.UUID, tier: str) -> Subscription:
        """Upgrades limits capabilities, decoupled from payment vendor logic."""
        pass
        
    @abstractmethod
    async def verify_search_quota(self, user_id: uuid.UUID) -> bool:
        """Checks if a user is within their monthly search limits."""
        pass
