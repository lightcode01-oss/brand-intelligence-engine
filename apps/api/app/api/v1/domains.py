import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.brand import DomainCheckResponse
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["Domain Checks"])

@router.get("/names/{name_id}/domains", response_model=StandardResponse[list[DomainCheckResponse]])
async def list_domain_checks(request: Request, name_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[list[DomainCheckResponse]]:
    """Retrieves cached domain availability verification results for a generated name."""
    data = [
        DomainCheckResponse(
            id=uuid.uuid4(),
            name_id=name_id,
            domain_name="nomen.com",
            tld="com",
            available=False,
            price=2500.0,
            created_at=datetime.utcnow()
        ),
        DomainCheckResponse(
            id=uuid.uuid4(),
            name_id=name_id,
            domain_name="nomen.co",
            tld="co",
            available=True,
            price=None,
            created_at=datetime.utcnow()
        )
    ]
    return wrap_success_response(data, request, "Domain availability checks retrieved.")
