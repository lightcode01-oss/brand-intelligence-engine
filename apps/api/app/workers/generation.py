import asyncio
from app.workers.celery_app import celery_app
from app.services.brand_engine.pipeline.orchestrator import BrandPipelineOrchestrator

@celery_app.task(bind=True, max_retries=3)
def async_generate_names_task(self, industry: str, context: str, target_count: int, temperature: float, style: str) -> dict:
    """Celery background task orchestrating the multi-stage brand name generation pipeline."""
    # Run async orchestrator inside Celery sync thread
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    orchestrator = BrandPipelineOrchestrator()
    try:
        results, meta = loop.run_until_complete(
            orchestrator.run_pipeline(
                industry=industry,
                context=context,
                target_count=target_count,
                temperature=temperature,
                style=style
            )
        )
        return {"status": "SUCCESS", "results": results, "metadata": meta}
    except Exception as exc:
        # Retry with exponential backoff on transient errors
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
