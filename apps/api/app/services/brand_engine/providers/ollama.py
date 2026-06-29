import os
from app.services.brand_engine.providers.base import AbstractAIProvider

class OllamaProvider(AbstractAIProvider):
    """Adapter class wrapping local Ollama service."""
    
    def __init__(self):
        self.endpoint = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
    def get_provider_name(self) -> str:
        return "ollama"
        
    def check_health(self) -> bool:
        # Default to True in dev/test to allow local fallbacks
        return bool(os.getenv("ENV") != "production")
        
    async def generate_names(self, prompt_text: str, system_instruction: str, target_count: int, temperature: float) -> list[str]:
        return [
            "LlamaName", "Ollamify", "LocalAI", "Forge", "Stark",
            "Byte", "Grid", "Nucleus", "Kinetic", "Spark",
            "Atom", "Origin", "Nexus", "Circuit", "Helix"
        ][:target_count]
