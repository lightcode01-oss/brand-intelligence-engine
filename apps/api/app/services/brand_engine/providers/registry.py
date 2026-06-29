import os
import time
import asyncio
from typing import Optional, Tuple, List
from app.services.brand_engine.providers.base import AbstractAIProvider
from app.services.brand_engine.providers.gemini import GeminiProvider
from app.services.brand_engine.providers.openai import OpenAIProvider
from app.services.brand_engine.providers.claude import ClaudeProvider
from app.services.brand_engine.providers.ollama import OllamaProvider
from app.services.brand_engine.providers.circuit_breaker import CircuitBreaker
from app.core.logging import logger

PROVIDER_PRICING = {
    "openai": {"input_1k": 0.005, "output_1k": 0.015},
    "claude": {"input_1k": 0.003, "output_1k": 0.015},
    "gemini": {"input_1k": 0.00035, "output_1k": 0.00105},
    "ollama": {"input_1k": 0.0, "output_1k": 0.0},
}

class ProviderRegistry:
    """Discovers, prioritizes, and routes queries through healthy AI providers with circuit breakers."""
    
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
        """Returns list of active, non-blocked providers sorted by fallback configuration priority."""
        healthy = []
        for name in self._fallback_order:
            if name in self._providers:
                cb = CircuitBreaker(name)
                if cb.can_execute():
                    healthy.append(self._providers[name])
        return healthy

    async def execute_generation_with_fallback(
        self, prompt_text: str, system_instruction: str, target_count: int, temperature: float
    ) -> Tuple[list[str], str, dict]:
        """Executes LLM request, falling back to lower-priority models on connection failures, with retries."""
        providers = self.get_healthy_providers()
        if not providers:
            # Fallback to local offline generation rules if no APIs are active
            logger.error("No active or healthy AI providers discovered in registry.")
            raise ValueError("All configured AI providers are offline.")
            
        errors = []
        for provider in providers:
            name = provider.get_provider_name()
            cb = CircuitBreaker(name)
            
            # Retry policy: 3 attempts with exponential backoff
            max_attempts = 3
            backoff_factor = 1.5
            
            for attempt in range(1, max_attempts + 1):
                try:
                    start_time = time.perf_counter()
                    results = await provider.generate_names(prompt_text, system_instruction, target_count, temperature)
                    latency = int((time.perf_counter() - start_time) * 1000)
                    
                    cb.record_success()
                    
                    # Token usage and cost calculations
                    input_tokens = len(prompt_text + system_instruction) // 4
                    output_tokens = len(" ".join(results)) // 4
                    total_tokens = input_tokens + output_tokens
                    
                    pricing = PROVIDER_PRICING.get(name, {"input_1k": 0.0, "output_1k": 0.0})
                    cost = (input_tokens * pricing["input_1k"] + output_tokens * pricing["output_1k"]) / 1000.0
                    
                    # Record Prometheus metrics
                    try:
                        from app.api.v1.metrics import nomen_ai_requests_total, nomen_ai_cost_usd_total
                        nomen_ai_requests_total.labels(provider=name, model=name, status="success", cache_hit="miss").inc()
                        nomen_ai_cost_usd_total.labels(provider=name, model=name).inc(cost)
                    except Exception:
                        pass
                    
                    metrics = {
                        "latency_ms": latency,
                        "token_usage": {
                            "prompt_tokens": input_tokens,
                            "completion_tokens": output_tokens,
                            "total_tokens": total_tokens
                        },
                        "cost_estimate": cost,
                        "provider": name
                    }
                    
                    # Log metrics success
                    logger.info(
                        f"AI Generation resolved successfully with provider '{name}' in {latency}ms. Cost: ${cost:.6f}",
                        extra={"provider": name, "latency": latency, "status": "success", "cost": cost}
                    )
                    return results, name, metrics
                    
                except Exception as exc:
                    logger.warning(
                        f"Provider '{name}' execution failed (attempt {attempt}/{max_attempts}). Error: {str(exc)}",
                        extra={"provider": name, "status": "failure", "attempt": attempt}
                    )
                    if attempt == max_attempts:
                        cb.record_failure()
                        try:
                            from app.api.v1.metrics import nomen_ai_requests_total
                            nomen_ai_requests_total.labels(provider=name, model=name, status="failure", cache_hit="miss").inc()
                        except Exception:
                            pass
                        errors.append(f"{name}: {str(exc)}")
                    else:
                        await asyncio.sleep(backoff_factor ** attempt)
                        
        raise RuntimeError(f"All AI providers failed. Fallback details: {', '.join(errors)}")
