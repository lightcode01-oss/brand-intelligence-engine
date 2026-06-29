import os
from app.services.brand_engine.providers.base import AbstractAIProvider

class OpenAIProvider(AbstractAIProvider):
    """Adapter class wrapping OpenAI API services."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    def get_provider_name(self) -> str:
        return "openai"
        
    def check_health(self) -> bool:
        # Healthy if API key configured (mocked connection check)
        return bool(self.api_key or os.getenv("ENV") != "production")
        
    async def generate_names(self, prompt_text: str, system_instruction: str, target_count: int, temperature: float) -> list[str]:
        # Conforming dummy names list generation
        return [
            "OpenAIify", "GPTName", "Promptly", "Aegis", "Vanguard",
            "Synthetix", "Cognitive", "Apex", "Nova", "Flux",
            "Zeta", "Vertex", "Catalyst", "Oracle", "Quill"
        ][:target_count]
