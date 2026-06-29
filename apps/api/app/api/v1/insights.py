import uuid
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.services.insights.engine import InsightsEngine

router = APIRouter(prefix="/insights", tags=["AI Insights"])

@router.get("/", response_model=StandardResponse[dict])
async def get_insights(
    request: Request,
    workspace_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[dict]:
    """Retrieves AI-generated workspace naming trends, comparison distributions, and metrics recommendations."""
    engine = InsightsEngine(db)
    
    trends = await engine.get_naming_trends(workspace_id)
    prompts = await engine.get_prompt_performance(workspace_id)
    stats = await engine.get_industry_stats(workspace_id)
    
    data = {
        "naming_trends": trends,
        "best_performing_prompts": prompts,
        "industry_statistics": stats,
        "recommendations": stats["insights_recommendations"]
    }
    return wrap_success_response(data, request, "AI Insights engine metrics calculated.")
