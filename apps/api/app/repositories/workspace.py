import uuid
from abc import abstractmethod
from typing import Optional, Sequence
from app.repositories.base import AbstractRepository
from app.models.workspace import Workspace, WorkspaceMember, Project

class AbstractWorkspaceRepository(AbstractRepository[Workspace]):
    """Abstract interface defining workspace collaboration query contracts."""
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        """Retrieves a workspace matching a specific URL-friendly slug."""
        pass

class AbstractWorkspaceMemberRepository(AbstractRepository[WorkspaceMember]):
    """Abstract interface defining team memberships query contracts."""
    
    @abstractmethod
    async def get_membership(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> Optional[WorkspaceMember]:
        """Retrieves a single member assignment link."""
        pass
        
    @abstractmethod
    async def list_workspace_members(self, workspace_id: uuid.UUID) -> Sequence[WorkspaceMember]:
        """Lists all team memberships grouped under a workspace."""
        pass

class AbstractProjectRepository(AbstractRepository[Project]):
    """Abstract interface defining project search workspace query contracts."""
    
    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[Project]:
        """Lists active projects registered inside a workspace."""
        pass
