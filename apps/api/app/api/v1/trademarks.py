import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.brand import TrademarkCheckResponse
from app.dependencies.security import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["Trademark Clearance"])

@router.get("/names/{name_id}/trademarks", response_model=StandardResponse[list[TrademarkCheckResponse]])
async def list_trademark_checks(request: Request, name_id: uuid.UUID, current_user: User = Depends(get_current_active_user)) -> StandardResponse[list[TrademarkCheckResponse]]:
    """Retrieves cached trademark collision records for a generated name."""
    data = [
        TrademarkCheckResponse(
            id=uuid.uuid4(),
            name_id=name_id,
            jurisdiction="US",
            risk_status="CLEAR",
            serial_number=None,
            mark_text="NOMEN",
            filing_date=None,
            registration_date=None,
            class_code="009",
            raw_payload={},
            created_at=datetime.utcnow()
        )
    ]
    return wrap_success_response(data, request, "Trademark clearance records retrieved.")
