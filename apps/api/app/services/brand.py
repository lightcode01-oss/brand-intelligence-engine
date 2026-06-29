import uuid
from abc import abstractmethod
from typing import Sequence
from app.services.base import AbstractService
from app.models.brand import GeneratedName, GenerationJob, DomainCheck, TrademarkCheck, SocialHandleCheck, Export

class AbstractNameGenerationService(AbstractService):
    """Abstract interface defining candidate name generation engine triggers."""
    
    @abstractmethod
    async def trigger_generation_job(self, project_id: uuid.UUID, model_name: str, temperature: float) -> GenerationJob:
        """Starts an async name generation job via Celery worker queues."""
        pass
        
    @abstractmethod
    async def get_job_status(self, job_id: uuid.UUID) -> GenerationJob:
        """Retrieves current processing state of a generation job."""
        pass

class AbstractBrandValidationService(AbstractService):
    """Abstract interface defining candidate verification workflows."""
    
    @abstractmethod
    async def check_domain_availability(self, name_id: uuid.UUID) -> Sequence[DomainCheck]:
        """Polls registration states of selected TLD checks."""
        pass
        
    @abstractmethod
    async def check_trademark_collisions(self, name_id: uuid.UUID) -> Sequence[TrademarkCheck]:
        """Polls official registries for trademark conflicts."""
        pass
        
    @abstractmethod
    async def check_social_handles(self, name_id: uuid.UUID) -> Sequence[SocialHandleCheck]:
        """Polls social platform handles availability."""
        pass

class AbstractExportService(AbstractService):
    """Abstract interface defining zipped asset downloads compilation."""
    
    @abstractmethod
    async def compile_name_assets(self, user_id: uuid.UUID, name_id: uuid.UUID) -> Export:
        """Assembles logo SVG vectors and details into a zip archive stored in R2."""
        pass
