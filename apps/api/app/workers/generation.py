import asyncio
import uuid
from app.workers.celery_app import celery_app
from app.api.v1.generation import run_generation_pipeline_bg

@celery_app.task(bind=True, max_retries=3)
def async_generate_names_task(
    self, project_id_str: str, job_id_str: str, workspace_id_str: str,
    industry: str, context: str, target_count: int, temperature: float, style: str
) -> dict:
    """Celery background task orchestrating the brand pipeline generation."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        loop.run_until_complete(
            run_generation_pipeline_bg(
                project_id=uuid.UUID(project_id_str),
                job_id=uuid.UUID(job_id_str),
                workspace_id=uuid.UUID(workspace_id_str),
                industry=industry,
                context=context,
                target_count=target_count,
                temperature=temperature,
                style=style
            )
        )
        return {"status": "SUCCESS"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
