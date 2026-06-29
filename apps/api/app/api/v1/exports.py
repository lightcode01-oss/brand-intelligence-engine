import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends, status
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.brand import ExportCreate, ExportResponse
from app.schemas.pagination import PaginatedListResponse, PaginationMeta, PaginationParams
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/exports", tags=["Asset Exports"])

@router.post("/", response_model=StandardResponse[ExportResponse], status_code=status.HTTP_201_CREATED)
async def request_export(request: Request, payload: ExportCreate, current_user: User = Depends(get_current_active_user)) -> StandardResponse[ExportResponse]:
    """Compiles name logo vectors and summaries into a zipped package download."""
    data = ExportResponse(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name_id=payload.name_id,
        package_url="https://r2.nomen.ai/exports/mocked_file_package.zip",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        created_at=datetime.utcnow()
    )
    return wrap_success_response(data, request, "ZIP asset export compiled successfully.")

@router.get("/", response_model=StandardResponse[PaginatedListResponse[ExportResponse]])
async def list_exports(request: Request, page_params: PaginationParams = Depends(), current_user: User = Depends(get_current_active_user)) -> StandardResponse[PaginatedListResponse[ExportResponse]]:
    """Lists historical exports requested by the current user."""
    items = [
        ExportResponse(
            id=uuid.uuid4(),
            user_id=current_user.id,
            name_id=uuid.uuid4(),
            package_url="https://r2.nomen.ai/exports/mocked_file_package.zip",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            created_at=datetime.utcnow()
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
    return wrap_success_response(payload, request, "Exports logs list retrieved.")
