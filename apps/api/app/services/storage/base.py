from abc import ABC, abstractmethod

class AbstractStorageProvider(ABC):
    """Abstract interface defining platform assets persistence operations."""
    
    @abstractmethod
    async def upload(self, local_file_path: str, destination_key: str) -> str:
        """Uploads a local file and returns the public or internal access URL."""
        pass
        
    @abstractmethod
    async def download(self, destination_key: str, local_dest_path: str) -> bool:
        """Downloads a remote file key into a local path."""
        pass
        
    @abstractmethod
    async def delete(self, destination_key: str) -> bool:
        """Deletes a file key from the storage registry."""
        pass
