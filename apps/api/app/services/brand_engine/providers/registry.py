import os
from typing import Optional
from app.services.brand_engine.providers.base import AbstractAIProvider
from app.services.brand_engine.providers.gemini import GeminiProvider
from app.services.brand_engine.providers.openai import OpenAIProvider
from app.services.brand_engine.providers.claude import ClaudeProvider
from app.services.brand_engine.providers.ollama import OllamaProvider
from app.core.logging import logger

class ProviderRegistry:
    """Discovers, prioritizes, and routes queries through healthy AI providers."""
    
    def __init__(self):
        self._providers: dict[str, AbstractAIProvider] = {}
        self._fallback_order: list[str] = []
        self._initialize_providers()
        
    def _initialize_providers(self) -> None:
        # Load concrete provider adapters
        gemini = GeminiProvider()
        openai = OpenAIProvider()
        claude = ClaudeProvider()
        ollama = OllamaProvider()
        
        # Register if healthy / configured
        for provider in [gemini, openai, claude, ollama]:
            if provider.check_health():
                self._providers[provider.get_provider_name()] = provider
                
        # Load fallback priority order from config
        fallback_str = os.getenv("PROVIDER_FALLBACK_ORDER", "gemini,openai,claude,ollama")
        self._fallback_order = [p.strip().lower() for p in fallback_str.split(",") if p.strip().lower() in self._providers]
        
    def get_healthy_providers(self) -> list[AbstractAIProvider]:
        """Returns list of active providers sorted by fallback configuration priority."""
        return [self._providers[name] for name in self._fallback_order if name in self._providers]

    async def execute_generation_with_fallback(
        self, prompt_text: str, system_instruction: str, target_count: int, temperature: float
    ) -> Tuple[list[str], str]:
        """Executes LLM request, falling back to lower-priority models on connection failures."""
        providers = self.get_healthy_providers()
        if not providers:
            # Fallback to local offline generation rules if no APIs are active
            logger.error("No active or healthy AI providers discovered in registry.")
            raise ValueError("All configured AI providers are offline.")
            
        errors = []
        for provider in providers:
            name = provider.get_provider_name()
            try:
                start_time = time.perf_counter()
                results = await provider.generate_names(prompt_text, system_instruction, target_count, temperature)
                latency = int((time.perf_counter() - start_time) * 1000)
                
                # Log metrics success
                logger.info(
                    f"AI Generation resolved successfully with provider '{name}' in {latency}ms.",
                    extra={"provider": name, "latency": latency, "status": "success"}
                )
                return results, name
            except Exception as exc:
                logger.warning(
                    f"Provider '{name}' execution failed. Attempting next fallback. Error: {str(exc)}",
                    extra={"provider": name, "status": "failure"}
                )
                errors.append(f"{name}: {str(exc)}")
                
        raise RuntimeError(f"All AI providers failed. Fallback details: {', '.join(errors)}")
import time
from typing import Tuple
