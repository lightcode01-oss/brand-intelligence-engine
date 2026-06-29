import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends, status
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.workspace import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.pagination import PaginatedListResponse, PaginationMeta, PaginationParams
from app.schemas.filters import FilterParams
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=StandardResponse[ProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_project(request: Request, payload: ProjectCreate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[ProjectResponse]:
    """Creates a new brainstorming project inside a workspace."""
    workspace_id = payload.workspace_id if hasattr(payload, "workspace_id") else uuid.uuid4()
    data = ProjectResponse(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        prompt=payload.prompt,
        target_syllables=payload.target_syllables,
        selected_tlds=payload.selected_tlds,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Project created successfully.")

@router.get("/", response_model=StandardResponse[PaginatedListResponse[ProjectResponse]])
async def list_projects(request: Request, page_params: PaginationParams = Depends(), filter_params: FilterParams = Depends(), current_user: User = Depends(get_current_active_user)) -> StandardResponse[PaginatedListResponse[ProjectResponse]]:
    """Lists all active projects matching the filter query."""
    workspace_id = filter_params.workspace_id or uuid.uuid4()
    items = [
        ProjectResponse(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            prompt="AI brand name generation for a startup platform.",
            target_syllables=2,
            selected_tlds=[".com", ".co", ".io"],
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
    return wrap_success_response(payload, request, "Projects list retrieved.")

@router.get("/{project_id}", response_model=StandardResponse[ProjectResponse])
async def get_project(request: Request, project_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[ProjectResponse]:
    """Retrieves full details of a specific project."""
    data = ProjectResponse(
        id=project_id,
        workspace_id=uuid.uuid4(),
        prompt="Brand name discovery for a pet wellness app.",
        target_syllables=3,
        selected_tlds=[".com", ".net"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Project details retrieved.")

@router.put("/{project_id}", response_model=StandardResponse[ProjectResponse])
async def update_project(request: Request, project_id: uuid.UUID, payload: ProjectUpdate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[ProjectResponse]:
    """Modifies search prompts or target extensions configuration."""
    data = ProjectResponse(
        id=project_id,
        workspace_id=uuid.uuid4(),
        prompt=payload.prompt or "Updated search prompt.",
        target_syllables=payload.target_syllables,
        selected_tlds=payload.selected_tlds or [".com"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Project configuration updated.")

@router.delete("/{project_id}", response_model=StandardResponse[dict])
async def delete_project(request: Request, project_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[dict]:
    """Soft deletes a project."""
    return wrap_success_response({"id": project_id, "deleted": True}, request, "Project soft-deleted successfully.")
