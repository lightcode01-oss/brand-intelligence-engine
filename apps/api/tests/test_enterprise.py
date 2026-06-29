import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, CreditTransaction, AuditLog
from app.models.workspace import Workspace, Project
from app.models.brand import GeneratedName, BrandScore, Export, GenerationJob
from app.models.report import SavedReport
from app.services.insights.engine import InsightsEngine
from app.services.recommendations import RecommendationEngine
from app.services.reports import ReportsManager
from app.core.config import settings

@pytest.mark.asyncio
async def test_insights_engine(db_session: AsyncSession) -> None:
    # 1. Setup entities
    user = User(email="insights-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="insights-test", display_name="Insights Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    project = Project(workspace_id=ws.id, prompt="crypto wallet app", selected_tlds=[".com"])
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Add duplicate candidates
    name1 = GeneratedName(
        project_id=project.id, name_string="BitSafe", style="Abstract",
        model_name="gemini-1.5-flash", temperature=0.7, prompt_tokens=10, completion_tokens=5, generation_version=1
    )
    name2 = GeneratedName(
        project_id=project.id, name_string="BitSafe", style="Abstract",
        model_name="gemini-1.5-flash", temperature=0.7, prompt_tokens=10, completion_tokens=5, generation_version=1
    )
    db_session.add_all([name1, name2])
    await db_session.commit()
    await db_session.refresh(name1)

    score = BrandScore(
        name_id=name1.id, bsi_overall=85, length_score=9.0, pronounceability_score=8.0,
        domain_score=8.5, trademark_score=9.0, semantic_score=8.0
    )
    db_session.add(score)
    
    job = GenerationJob(
        project_id=project.id, status="SUCCESS", current_stage="Finished",
        model_name="gemini-1.5-flash", engine_version="v1", prompt_version="v1",
        latency_ms=1200, token_usage={"prompt_tokens": 10, "completion_tokens": 5},
        cost_estimate=0.01
    )
    db_session.add(job)
    await db_session.commit()

    engine = InsightsEngine(db_session)
    trends = await engine.get_naming_trends(ws.id)
    assert trends["total_candidates"] == 2
    assert trends["duplicate_ratio"] == 0.5 # 1 duplicate item / 2 total candidates

    prompts = await engine.get_prompt_performance(ws.id)
    assert len(prompts) == 1
    assert prompts[0]["prompt"] == "crypto wallet app"
    assert prompts[0]["average_brand_score"] == 85.0

    stats = await engine.get_industry_stats(ws.id)
    assert len(stats["providers_comparison"]) == 1
    assert stats["providers_comparison"][0]["model"] == "gemini-1.5-flash"
    assert len(stats["insights_recommendations"]) > 0

@pytest.mark.asyncio
async def test_recommendation_engine(db_session: AsyncSession) -> None:
    # Set up
    project_id = uuid.uuid4() # Mock non-existent project uses fallback recommendations
    engine = RecommendationEngine(db_session)
    recs = await engine.generate_recommendations(project_id)
    
    assert "stronger_prompts" in recs
    assert len(recs["logo_colors"]) > 0
    assert len(recs["typography"]) > 0

@pytest.mark.asyncio
async def test_reports_manager(db_session: AsyncSession) -> None:
    user = User(email="reports-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="reports-test", display_name="Reports Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    manager = ReportsManager(db_session)
    report_data = {"avg_bsi": 82.4, "total_names": 150}
    
    # 1. Create Report
    report = await manager.create_report(
        workspace_id=ws.id,
        user_id=user.id,
        name="Quarterly Brand Audit",
        report_type="analytics",
        fmt="json",
        data=report_data
    )
    assert report is not None
    assert report.version == 1
    assert report.format == "json"

    # Create next version
    report2 = await manager.create_report(
        workspace_id=ws.id,
        user_id=user.id,
        name="Quarterly Brand Audit",
        report_type="analytics",
        fmt="csv",
        data=report_data
    )
    assert report2.version == 2

    # 2. List Reports
    reports = await manager.list_reports(ws.id)
    assert len(reports) == 2

    # 3. Compile Streams
    content, media_type = manager.compile_export_stream(report)
    assert media_type == "application/json"
    assert "avg_bsi" in content

    content_csv, media_csv = manager.compile_export_stream(report2)
    assert media_csv == "text/csv"
    assert "Metric,Value" in content_csv

@pytest.mark.asyncio
async def test_maintenance_toggle() -> None:
    # Verify memory mutation toggle works
    assert settings.MAINTENANCE_MODE is False
    settings.MAINTENANCE_MODE = True
    assert settings.MAINTENANCE_MODE is True
    # Reset
    settings.MAINTENANCE_MODE = False
