import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Request, Depends, status, HTTPException, BackgroundTasks
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.brand import GenerationJobCreate, GenerationJobResponse, GeneratedNameResponse, GeneratedNameUpdate
from app.schemas.pagination import PaginatedListResponse, PaginationMeta, PaginationParams
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.models.workspace import Project
from app.models.brand import GeneratedName, GenerationJob

router = APIRouter(tags=["AI Names Generation"])

async def run_generation_pipeline_bg(
    project_id: uuid.UUID, job_id: uuid.UUID, workspace_id: uuid.UUID,
    industry: str, context: str, target_count: int, temperature: float, style: str
):
    """FastAPI BackgroundTask runner executing name generation orchestrations."""
    from app.core.database import async_session_maker
    from app.services.brand_engine.pipeline.orchestrator import BrandPipelineOrchestrator
    
    async with async_session_maker() as db:
        orchestrator = BrandPipelineOrchestrator()
        try:
            results, meta = await orchestrator.run_pipeline(
                industry=industry,
                context=context,
                target_count=target_count,
                temperature=temperature,
                style=style,
                db=db,
                job_id=job_id,
                workspace_id=workspace_id
            )
            
            # Persist all generated name candidates
            for r in results:
                name_entity = GeneratedName(
                    project_id=project_id,
                    name_string=r.get("name_string", "SuggestedName"),
                    style=style,
                    model_name=r.get("model_name", "gemini-1.5-flash"),
                    temperature=temperature,
                    prompt_tokens=100,      # placeholder
                    completion_tokens=50,   # placeholder
                    generation_version=1
                )
                db.add(name_entity)
            await db.commit()
            
            # Save activity event
            from app.services.collaboration.activity import ActivityService
            activity = ActivityService(db)
            await activity.log_activity(
                workspace_id=workspace_id,
                user_id=uuid.UUID(int=0), # system user placeholder
                action_type="names_generated",
                description=f"Generated {len(results)} new brand name concepts for industry '{industry}'",
                metadata_json={"project_id": str(project_id), "count": len(results)}
            )
            await db.commit()
        except Exception as e:
            # Stage updated to FAILED inside orchestrator
            pass

@router.post("/projects/{project_id}/generate", response_model=StandardResponse[GenerationJobResponse], status_code=status.HTTP_202_ACCEPTED)
async def generate_names(
    request: Request, project_id: uuid.UUID, payload: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[GenerationJobResponse]:
    """Triggers an asynchronous name generation job for a project."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    job = GenerationJob(
        project_id=project_id,
        status="PENDING",
        current_stage="Queued",
        model_name=payload.model_name,
        engine_version="v1.0.0",
        prompt_version="v1.0",
        latency_ms=0,
        token_usage={},
        cost_estimate=0.0
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Run the orchestrator in a background task
    background_tasks.add_task(
        run_generation_pipeline_bg,
        project_id=project_id,
        job_id=job.id,
        workspace_id=project.workspace_id,
        industry="Technology",  # Default industry context
        context=project.prompt,
        target_count=10,
        temperature=payload.temperature,
        style="Compound"
    )
    
    return wrap_success_response(job, request, "Generation job triggered successfully.")

@router.get("/jobs/{job_id}", response_model=StandardResponse[GenerationJobResponse])
async def get_job_status(
    request: Request, job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[GenerationJobResponse]:
    """Retrieves current processing state of a generation job."""
    job = await db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return wrap_success_response(job, request, "Job status retrieved.")

@router.get("/projects/{project_id}/names", response_model=StandardResponse[PaginatedListResponse[GeneratedNameResponse]])
async def list_generated_names(
    request: Request, project_id: uuid.UUID, page_params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[PaginatedListResponse[GeneratedNameResponse]]:
    """Lists name candidates generated under a specific project."""
    stmt = select(GeneratedName).where(
        GeneratedName.project_id == project_id,
        GeneratedName.deleted_at == None
    ).order_by(GeneratedName.created_at)
    
    # Calculate totals
    from sqlalchemy import func
    count_stmt = select(func.count(GeneratedName.id)).where(
        GeneratedName.project_id == project_id,
        GeneratedName.deleted_at == None
    )
    total = (await db.execute(count_stmt)).scalar() or 0
    
    # Paginate
    stmt = stmt.offset((page_params.page - 1) * page_params.page_size).limit(page_params.page_size)
    items = (await db.execute(stmt)).scalars().all()
    
    total_pages = (total + page_params.page_size - 1) // page_params.page_size
    meta = PaginationMeta(
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
        total_pages=total_pages,
        has_next=page_params.page < total_pages,
        has_previous=page_params.page > 1
    )
    payload = PaginatedListResponse(items=items, pagination=meta)
    return wrap_success_response(payload, request, "Generated names retrieved.")

@router.put("/names/{name_id}", response_model=StandardResponse[GeneratedNameResponse])
async def update_name_state(
    request: Request, name_id: uuid.UUID, payload: GeneratedNameUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[GeneratedNameResponse]:
    """Updates candidate state (e.g. saves or archives a name)."""
    name_item = await db.get(GeneratedName, name_id)
    if not name_item:
        raise HTTPException(status_code=404, detail="Name candidate not found")
        
    name_item.lifecycle_state = payload.lifecycle_state
    name_item.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(name_item)
    return wrap_success_response(name_item, request, "Name state updated successfully.")

@router.delete("/names/{name_id}", response_model=StandardResponse[dict])
async def delete_name(
    request: Request, name_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Soft-deletes a candidate name."""
    name_item = await db.get(GeneratedName, name_id)
    if not name_item:
        raise HTTPException(status_code=404, detail="Name candidate not found")
        
    name_item.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return wrap_success_response({"id": name_id, "deleted": True}, request, "Temporary name deleted successfully.")
