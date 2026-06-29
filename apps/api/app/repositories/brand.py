import uuid
from abc import abstractmethod
from typing import Optional, Sequence
from app.repositories.base import AbstractRepository
from app.models.brand import (
    GeneratedName, BrandScore, LogoSuggestion, DomainCheck, 
    TrademarkCheck, SocialHandleCheck, Export, GenerationJob
)

class AbstractGeneratedNameRepository(AbstractRepository[GeneratedName]):
    """Abstract interface defining candidates query contracts."""
    
    @abstractmethod
    async def list_by_project(self, project_id: uuid.UUID) -> Sequence[GeneratedName]:
        """Lists name candidates generated for a specific project context."""
        pass
        
    @abstractmethod
    async def list_saved_names(self, project_id: uuid.UUID) -> Sequence[GeneratedName]:
        """Lists saved candidates under a project."""
        pass

class AbstractBrandScoreRepository(AbstractRepository[BrandScore]):
    """Abstract interface defining BSI score card query contracts."""
    pass

class AbstractLogoSuggestionRepository(AbstractRepository[LogoSuggestion]):
    """Abstract interface defining logo configuration query contracts."""
    pass

class AbstractDomainCheckRepository(AbstractRepository[DomainCheck]):
    """Abstract interface defining domain cache query contracts."""
    
    @abstractmethod
    async def list_by_name(self, name_id: uuid.UUID) -> Sequence[DomainCheck]:
        """Retrieves cached availability results for a generated name ID."""
        pass

class AbstractTrademarkCheckRepository(AbstractRepository[TrademarkCheck]):
    """Abstract interface defining trademark cache query contracts."""
    
    @abstractmethod
    async def list_by_name(self, name_id: uuid.UUID) -> Sequence[TrademarkCheck]:
        """Retrieves cached trademark results for a generated name ID."""
        pass

class AbstractSocialHandleCheckRepository(AbstractRepository[SocialHandleCheck]):
    """Abstract interface defining handle check logs query contracts."""
    
    @abstractmethod
    async def list_by_name(self, name_id: uuid.UUID) -> Sequence[SocialHandleCheck]:
        """Retrieves cached username availability checks."""
        pass

class AbstractExportRepository(AbstractRepository[Export]):
    """Abstract interface defining compiled downloads query contracts."""
    
    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[Export]:
        """Lists historical downloads packages requested by a user."""
        pass

class AbstractGenerationJobRepository(AbstractRepository[GenerationJob]):
    """Abstract interface defining AI request jobs monitoring contracts."""
    
    @abstractmethod
    async def get_active_job(self, project_id: uuid.UUID) -> Optional[GenerationJob]:
        """Retrieves the currently running name generation task for a project."""
        pass
