import uuid
from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db_session
from app.dependencies.security import get_current_active_user
from app.models.user import User
from app.schemas.response import StandardResponse, wrap_success_response
from app.schemas.analytics import RecommendationResponse
from app.services.recommendations import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])

@router.get("/", response_model=StandardResponse[RecommendationResponse])
async def get_naming_recommendations(
    request: Request,
    project_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> StandardResponse[RecommendationResponse]:
    """Generates logo colors, slogan iterations, typography guidelines, and alternative domains based on project profile."""
    engine = RecommendationEngine(db)
    recs = await engine.generate_recommendations(project_id)
    
    data = RecommendationResponse(
        stronger_prompts=recs["stronger_prompts"],
        better_industries=recs["better_industries"],
        logo_colors=recs["logo_colors"],
        typography=recs["typography"],
        slogan_suggestions=recs["slogan_suggestions"],
        domain_alternatives=recs["domain_alternatives"],
        similar_successful_brands=recs["similar_successful_brands"]
    )
    return wrap_success_response(data, request, "AI recommendations calculated.")
