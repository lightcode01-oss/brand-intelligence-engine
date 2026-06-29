import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Sequence

T = TypeVar("T")

class AbstractRepository(ABC, Generic[T]):
    """Generic base interface for all data layer repositories."""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Saves a new entity instance to the database."""
        pass
        
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Persists modifications made to an existing entity."""
        pass
        
    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Executes a hard-delete or soft-delete on the entity matching the ID."""
        pass
        
    @abstractmethod
    async def get(self, entity_id: uuid.UUID) -> Optional[T]:
        """Retrieves a single active entity matching the ID."""
        pass
        
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """Lists a page range of active entities."""
        pass
        
    @abstractmethod
    async def exists(self, entity_id: uuid.UUID) -> bool:
        """Verifies if an active record matches the ID."""
        pass
        
    @abstractmethod
    async def count(self) -> int:
        """Calculates total count of active records."""
        pass
        
    @abstractmethod
    async def search(self, query: str) -> Sequence[T]:
        """Fuzzy matches fields using a text pattern."""
        pass
