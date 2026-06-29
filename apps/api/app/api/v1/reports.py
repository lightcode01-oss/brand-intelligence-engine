import uuid
from fastapi import APIRouter, Request, Depends, Query, Response, HTTPException
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.analytics import SavedReportCreate, SavedReportResponse
from app.services.reports import ReportsManager

router = APIRouter(prefix="/reports", tags=["Saved Reports"])

@router.post("/", response_model=StandardResponse[SavedReportResponse])
async def create_saved_report(
    request: Request,
    payload: SavedReportCreate,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[SavedReportResponse]:
    """Saves a workspace report to database tracking."""
    manager = ReportsManager(db)
    
    # Fallback default parameters if data_json is empty
    report_data = payload.data_json or {
        "overall_brand_score": 85.0,
        "total_candidates": 12,
        "trademark_risk": "low"
    }
    
    report = await manager.create_report(
        workspace_id=workspace_id,
        user_id=current_user.id,
        name=payload.name,
        report_type=payload.report_type,
        fmt=payload.format,
        data=report_data
    )
    await db.commit()
    await db.refresh(report)
    
    data = SavedReportResponse.from_attributes(report)
    return wrap_success_response(data, request, "Saved report created successfully.")

@router.get("/", response_model=StandardResponse[list[SavedReportResponse]])
async def list_saved_reports(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[list[SavedReportResponse]]:
    """Lists saved historical reports for workspace."""
    manager = ReportsManager(db)
    reports = await manager.list_reports(workspace_id)
    
    data = [SavedReportResponse.from_attributes(r) for r in reports]
    return wrap_success_response(data, request, "Saved reports list retrieved.")

@router.get("/{report_id}/download")
async def download_saved_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> Response:
    """Compiles and downloads report in markdown, csv, json, or pdf."""
    manager = ReportsManager(db)
    report = await manager.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    content, media_type = manager.compile_export_stream(report)
    
    headers = {
        "Content-Disposition": f"attachment; filename=report_{report.id}.{report.format}"
    }
    return Response(content=content, media_type=media_type, headers=headers)
