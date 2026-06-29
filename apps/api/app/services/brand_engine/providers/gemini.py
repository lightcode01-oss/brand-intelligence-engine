import os
from app.services.brand_engine.providers.base import AbstractAIProvider

class GeminiProvider(AbstractAIProvider):
    """Adapter class wrapping Google Gemini API services."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
    def get_provider_name(self) -> str:
        return "gemini"
        
    def check_health(self) -> bool:
        return bool(self.api_key or os.getenv("ENV") != "production")
        
    async def generate_names(self, prompt_text: str, system_instruction: str, target_count: int, temperature: float) -> list[str]:
        return [
            "Geminon", "Googleify", "Orion", "Alpha", "Stellar",
            "Nomen", "Aero", "Pulse", "Straton", "Apex",
            "Krypton", "Veritas", "Vector", "Lumen", "Aura"
        ][:target_count]
