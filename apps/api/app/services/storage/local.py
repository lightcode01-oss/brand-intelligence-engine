import os
import shutil
from app.services.storage.base import AbstractStorageProvider

class LocalStorageProvider(AbstractStorageProvider):
    """Saves assets directly to a local configuration folder (default for local development)."""
    
    def __init__(self, base_dir: str = "./scratch/storage"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    async def upload(self, local_file_path: str, destination_key: str) -> str:
        dest_path = os.path.join(self.base_dir, destination_key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(local_file_path, dest_path)
        return f"file://{os.path.abspath(dest_path)}"
        
    async def download(self, destination_key: str, local_dest_path: str) -> bool:
        src_path = os.path.join(self.base_dir, destination_key)
        if os.path.exists(src_path):
            shutil.copy2(src_path, local_dest_path)
            return True
        return False
        
    async def delete(self, destination_key: str) -> bool:
        path = os.path.join(self.base_dir, destination_key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
