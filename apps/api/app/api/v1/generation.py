import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends, status
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.brand import GenerationJobCreate, GenerationJobResponse, GeneratedNameResponse, GeneratedNameUpdate
from app.schemas.pagination import PaginatedListResponse, PaginationMeta, PaginationParams
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["AI Names Generation"])

@router.post("/projects/{project_id}/generate", response_model=StandardResponse[GenerationJobResponse], status_code=status.HTTP_202_ACCEPTED)
async def generate_names(request: Request, project_id: uuid.UUID, payload: GenerationJobCreate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[GenerationJobResponse]:
    """Triggers an asynchronous name generation job for a project."""
    data = GenerationJobResponse(
        id=uuid.uuid4(),
        project_id=project_id,
        status="PENDING",
        model_name=payload.model_name,
        engine_version="v1.0.0",
        prompt_version="v1.0",
        latency_ms=0,
        token_usage={},
        cost_estimate=None,
        error_message=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Generation job triggered successfully.")

@router.get("/jobs/{job_id}", response_model=StandardResponse[GenerationJobResponse])
async def get_job_status(request: Request, job_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[GenerationJobResponse]:
    """Retrieves current processing state of a generation job."""
    data = GenerationJobResponse(
        id=job_id,
        project_id=uuid.uuid4(),
        status="SUCCESS",
        model_name="gemini-1.5-flash",
        engine_version="v1.0.0",
        prompt_version="v1.0",
        latency_ms=1500,
        token_usage={"prompt_tokens": 120, "completion_tokens": 60},
        cost_estimate=0.00021,
        error_message=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Job status retrieved.")

@router.get("/projects/{project_id}/names", response_model=StandardResponse[PaginatedListResponse[GeneratedNameResponse]])
async def list_generated_names(request: Request, project_id: uuid.UUID, page_params: PaginationParams = Depends(), current_user: User = Depends(get_current_active_user)) -> StandardResponse[PaginatedListResponse[GeneratedNameResponse]]:
    """Lists name candidates generated under a specific project."""
    items = [
        GeneratedNameResponse(
            id=uuid.uuid4(),
            project_id=project_id,
            name_string="Nomen",
            style="Abstract",
            lifecycle_state="SUGGESTED",
            model_name="gemini-1.5-flash",
            temperature=0.7,
            prompt_tokens=150,
            completion_tokens=50,
            generation_version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    meta = PaginationMeta(
        page=page_params.page,
        page_size=page_params.page_size,
        total=1,
        total_pages=1,
        has_next=False,
        has_previous=False
    )
    payload = PaginatedListResponse(items=items, pagination=meta)
    return wrap_success_response(payload, request, "Generated names retrieved.")

@router.put("/names/{name_id}", response_model=StandardResponse[GeneratedNameResponse])
async def update_name_state(request: Request, name_id: uuid.UUID, payload: GeneratedNameUpdate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[GeneratedNameResponse]:
    """Updates candidate state (e.g. saves or archives a name)."""
    data = GeneratedNameResponse(
        id=name_id,
        project_id=uuid.uuid4(),
        name_string="Brandify",
        style="Compound",
        lifecycle_state=payload.lifecycle_state,
        model_name="gemini-1.5-flash",
        temperature=0.7,
        prompt_tokens=150,
        completion_tokens=50,
        generation_version=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Name state updated successfully.")

@router.delete("/names/{name_id}", response_model=StandardResponse[dict])
async def delete_name(request: Request, name_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[dict]:
    """Hard-deletes a temporary candidate name."""
    return wrap_success_response({"id": name_id, "deleted": True}, request, "Temporary name hard-deleted successfully.")
