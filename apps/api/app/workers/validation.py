import asyncio
from app.workers.celery_app import celery_app
from app.services.validation.domain.registry import DomainProviderRegistry
from app.services.validation.trademark.registry import TrademarkProviderRegistry
from app.services.validation.social.registry import SocialProviderRegistry

@celery_app.task
def async_validate_candidate_task(name: str, domain_tld: str = "com") -> dict:
    """Runs domain, trademark, and social checkers asynchronously for a candidate name."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    async def run_checks():
        # Load registries
        dom_registry = DomainProviderRegistry()
        tm_registry = TrademarkProviderRegistry()
        soc_registry = SocialProviderRegistry()
        
        # Resolve providers
        dom_provider = dom_registry.get_provider()
        tm_provider = tm_registry.get_provider()
        github_provider = soc_registry.get_provider("github")
        
        # Execute checks concurrently
        dom_fut = dom_provider.check(name, domain_tld)
        tm_fut = tm_provider.check(name, "us")
        github_fut = github_provider.check(name)
        
        dom_res, tm_res, gh_res = await asyncio.gather(dom_fut, tm_fut, github_fut)
        
        return {
            "domain": dom_res.model_dump(),
            "trademark": tm_res.model_dump(),
            "social": gh_res.model_dump()
        }
        
    try:
        results = loop.run_until_complete(run_checks())
        return {"status": "SUCCESS", "name": name, "results": results}
    except Exception as exc:
        return {"status": "FAILURE", "name": name, "error": str(exc)}
