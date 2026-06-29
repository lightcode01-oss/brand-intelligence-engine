import uuid
from abc import abstractmethod
from typing import Optional, Sequence
from app.services.base import AbstractService
from app.models.workspace import Workspace, WorkspaceMember, Project

class AbstractWorkspaceService(AbstractService):
    """Abstract interface defining team workspace collaboration workflows."""
    
    @abstractmethod
    async def create_workspace(self, owner_id: uuid.UUID, slug: str, display_name: str) -> Workspace:
        """Initializes a new workspace and registers the owner membership."""
        pass
        
    @abstractmethod
    async def add_workspace_member(self, workspace_id: uuid.UUID, user_id: uuid.UUID, role: str) -> WorkspaceMember:
        """Adds a member link to the workspace collaboration pool."""
        pass
        
    @abstractmethod
    async def get_workspace_details(self, workspace_id: uuid.UUID) -> Workspace:
        """Retrieves details of a workspace."""
        pass

class AbstractProjectService(AbstractService):
    """Abstract interface defining project folders management workflows."""
    
    @abstractmethod
    async def create_project(self, workspace_id: uuid.UUID, prompt: str, target_syllables: Optional[int], selected_tlds: list[str]) -> Project:
        """Creates a new project session to host name discoveries."""
        pass
        
    @abstractmethod
    async def list_workspace_projects(self, workspace_id: uuid.UUID) -> Sequence[Project]:
        """Lists all projects registered under a workspace."""
        pass
