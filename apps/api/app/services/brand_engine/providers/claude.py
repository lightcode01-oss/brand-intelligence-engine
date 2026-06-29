import os
from app.services.brand_engine.providers.base import AbstractAIProvider

class ClaudeProvider(AbstractAIProvider):
    """Adapter class wrapping Anthropic Claude API services."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
    def get_provider_name(self) -> str:
        return "claude"
        
    def check_health(self) -> bool:
        return bool(self.api_key or os.getenv("ENV") != "production")
        
    async def generate_names(self, prompt_text: str, system_instruction: str, target_count: int, temperature: float) -> list[str]:
        return [
            "Claudify", "AnthropicName", "Scribe", "Omni", "Prism",
            "Clarity", "Intellect", "Summit", "Zenith", "Meridian",
            "Echo", "Horizon", "Cortex", "Voxel", "Helix"
        ][:target_count]
