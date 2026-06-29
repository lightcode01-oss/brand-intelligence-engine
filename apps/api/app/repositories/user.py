import uuid
from abc import abstractmethod
from typing import Optional, Sequence
from app.repositories.base import AbstractRepository
from app.models.user import User, Subscription, FeatureFlag, AuditLog

class AbstractUserRepository(AbstractRepository[User]):
    """Abstract interface defining user-specific query contracts."""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user matching a specific email address."""
        pass

class AbstractSubscriptionRepository(AbstractRepository[Subscription]):
    """Abstract interface defining subscription query contracts."""
    
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Subscription]:
        """Retrieves active billing limits matching a specific user ID."""
        pass

class AbstractFeatureFlagRepository(AbstractRepository[FeatureFlag]):
    """Abstract interface defining feature flag query contracts."""
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[FeatureFlag]:
        """Retrieves a feature flag configuration matching a specific name."""
        pass
        
    @abstractmethod
    async def list_active_flags(self) -> Sequence[FeatureFlag]:
        """Lists all enabled feature flags currently active."""
        pass

class AbstractAuditLogRepository(AbstractRepository[AuditLog]):
    """Abstract interface defining write-only audit trail logging contracts."""
    
    @abstractmethod
    async def list_by_actor(self, actor: str) -> Sequence[AuditLog]:
        """Retrieves action records triggered by a specific actor profile."""
        pass
        
    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[AuditLog]:
        """Retrieves action records logged inside a specific workspace context."""
        pass
