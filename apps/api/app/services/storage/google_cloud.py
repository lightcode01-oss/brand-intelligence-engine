from app.services.storage.base import AbstractStorageProvider

class GoogleCloudStorageProvider(AbstractStorageProvider):
    """Saves assets to Google Cloud Storage (GCS) buckets."""
    
    def __init__(self, bucket_name: str = "nomen-gcs-assets"):
        self.bucket = bucket_name
        
    async def upload(self, local_file_path: str, destination_key: str) -> str:
        return f"https://storage.googleapis.com/{self.bucket}/{destination_key}"
        
    async def download(self, destination_key: str, local_dest_path: str) -> bool:
        return False
        
    async def delete(self, destination_key: str) -> bool:
        return False
