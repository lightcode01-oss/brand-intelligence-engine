from abc import ABC, abstractmethod

class AbstractAIProvider(ABC):
    """Abstract interface defining AI candidate name generation contracts."""
    
    @abstractmethod
    async def generate_names(self, prompt_text: str, system_instruction: str, target_count: int, temperature: float) -> list[str]:
        """Queries the provider LLM to generate list of candidate brand names."""
        pass
        
    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the unique slug name of the provider."""
        pass
        
    @abstractmethod
    def check_health(self) -> bool:
        """Verifies active API keys and connectivity."""
        pass
