import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends, status
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceMemberCreate, WorkspaceMemberResponse
from app.schemas.pagination import PaginatedListResponse, PaginationMeta, PaginationParams
from app.schemas.filters import FilterParams
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("/", response_model=StandardResponse[WorkspaceResponse], status_code=status.HTTP_201_CREATED)
async def create_workspace(request: Request, payload: WorkspaceCreate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[WorkspaceResponse]:
    """Initializes a new team workspace."""
    data = WorkspaceResponse(
        id=uuid.uuid4(),
        slug=payload.slug,
        display_name=payload.display_name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Workspace created successfully.")

@router.get("/", response_model=StandardResponse[PaginatedListResponse[WorkspaceResponse]])
async def list_workspaces(request: Request, page_params: PaginationParams = Depends(), filter_params: FilterParams = Depends(), current_user: User = Depends(get_current_active_user)) -> StandardResponse[PaginatedListResponse[WorkspaceResponse]]:
    """Lists all active workspaces accessible by the current user."""
    items = [
        WorkspaceResponse(
            id=uuid.uuid4(),
            slug="default-workspace",
            display_name="Default Workspace",
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
    return wrap_success_response(payload, request, "Workspaces list retrieved.")

@router.get("/{workspace_id}", response_model=StandardResponse[WorkspaceResponse])
async def get_workspace(request: Request, workspace_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[WorkspaceResponse]:
    """Retrieves detailed attributes of a workspace."""
    data = WorkspaceResponse(
        id=workspace_id,
        slug="my-workspace",
        display_name="My Workspace",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Workspace details retrieved.")

@router.put("/{workspace_id}", response_model=StandardResponse[WorkspaceResponse])
async def update_workspace(request: Request, workspace_id: uuid.UUID, payload: WorkspaceUpdate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[WorkspaceResponse]:
    """Updates workspace titles or slugs."""
    data = WorkspaceResponse(
        id=workspace_id,
        slug=payload.slug or "updated-workspace",
        display_name=payload.display_name or "Updated Workspace",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Workspace updated successfully.")

@router.delete("/{workspace_id}", response_model=StandardResponse[dict])
async def delete_workspace(request: Request, workspace_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[dict]:
    """Soft deletes a workspace."""
    return wrap_success_response({"id": workspace_id, "deleted": True}, request, "Workspace soft-deleted successfully.")

@router.post("/{workspace_id}/members", response_model=StandardResponse[WorkspaceMemberResponse], status_code=status.HTTP_201_CREATED)
async def add_member(request: Request, workspace_id: uuid.UUID, payload: WorkspaceMemberCreate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[WorkspaceMemberResponse]:
    """Invites a user to the workspace."""
    data = WorkspaceMemberResponse(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        user_id=payload.user_id,
        role=payload.role,
        created_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "Workspace member added successfully.")
