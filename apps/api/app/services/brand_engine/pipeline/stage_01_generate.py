from typing import Optional, Tuple
from app.services.brand_engine.providers.registry import ProviderRegistry
from app.services.brand_engine.prompts import PromptEngine

class Stage1Generate:
    """Stage 1: Generates a list of raw candidate names using versioned templates and LLM providers."""
    
    def __init__(self, registry: Optional[ProviderRegistry] = None):
        self.registry = registry or ProviderRegistry()
        self.prompts = PromptEngine()
        
    async def execute(self, industry: str, context: str, target_count: int, temperature: float = 0.7, syllable_limit: Optional[int] = None) -> Tuple[list[str], dict]:
        """Runs the generation call returning candidate name strings and generation metadata."""
        # 1. Compile versioned template prompt
        template = self.prompts.compile_prompt(industry, context, target_count, syllable_limit)
        
        # 2. Query registry providers with fallback
        results, provider_name = await self.registry.execute_generation_with_fallback(
            prompt_text=template.user_prompt,
            system_instruction=template.system_prompt,
            target_count=target_count,
            temperature=temperature
        )
        
        metadata = {
            "prompt_id": template.prompt_id,
            "prompt_version": template.version,
            "provider": provider_name,
            "temperature": temperature,
            "system_prompt": template.system_prompt,
            "user_prompt": template.user_prompt
        }
        
        return results, metadata
