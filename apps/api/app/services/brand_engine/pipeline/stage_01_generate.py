import uuid
from typing import Optional, Tuple
from app.services.brand_engine.providers.registry import ProviderRegistry
from app.services.brand_engine.prompts import PromptEngine
from app.core.cache.semantic import SemanticCache

class Stage1Generate:
    """Stage 1: Generates a list of raw candidate names using versioned templates and LLM providers with semantic caching."""
    
    def __init__(self, registry: Optional[ProviderRegistry] = None):
        self.registry = registry or ProviderRegistry()
        self.prompts = PromptEngine()
        
    async def execute(
        self, industry: str, context: str, target_count: int, 
        temperature: float = 0.7, syllable_limit: Optional[int] = None,
        workspace_id: Optional[uuid.UUID] = None
    ) -> Tuple[list[str], dict]:
        """Runs the generation call returning candidate name strings and generation metadata, checking semantic cache first."""
        # 1. Compile versioned template prompt
        template = self.prompts.compile_prompt(industry, context, target_count, syllable_limit)
        
        ws_str = str(workspace_id) if workspace_id else "global"
        cache = SemanticCache()
        
        # Check semantic cache
        cached_result = cache.lookup(ws_str, template.user_prompt)
        if cached_result:
            results, hit_type = cached_result
            try:
                from app.api.v1.metrics import nomen_ai_requests_total
                nomen_ai_requests_total.labels(provider="cache", model="cache", status="success", cache_hit=hit_type).inc()
            except Exception:
                pass
            metadata = {
                "prompt_id": template.prompt_id,
                "prompt_version": template.version,
                "provider": "cache",
                "temperature": temperature,
                "system_prompt": template.system_prompt,
                "user_prompt": template.user_prompt,
                "latency_ms": 0,
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "cost_estimate": 0.0,
                "cache_hit": hit_type
            }
            return results, metadata
        
        # 2. Query registry providers with fallback
        results, provider_name, metrics = await self.registry.execute_generation_with_fallback(
            prompt_text=template.user_prompt,
            system_instruction=template.system_prompt,
            target_count=target_count,
            temperature=temperature
        )
        
        # Save to semantic cache
        cache.save(ws_str, template.user_prompt, results)
        
        metadata = {
            "prompt_id": template.prompt_id,
            "prompt_version": template.version,
            "provider": provider_name,
            "temperature": temperature,
            "system_prompt": template.system_prompt,
            "user_prompt": template.user_prompt,
            "latency_ms": metrics.get("latency_ms", 0),
            "token_usage": metrics.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0}),
            "cost_estimate": metrics.get("cost_estimate", 0.0),
            "cache_hit": None
        }
        
        return results, metadata
