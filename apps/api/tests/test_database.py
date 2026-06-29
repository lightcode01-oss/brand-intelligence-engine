import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.future import select
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Subscription
from app.models.workspace import Workspace, Project
from app.models.brand import GeneratedName, GenerationJob
from app.core.slugs import slugify, is_valid_slug

@pytest.mark.asyncio
async def test_slug_logic() -> None:
    # 1. Test slugify transformations
    assert slugify("My Startup Name!!!") == "my-startup-name"
    assert slugify("---Hello---World---") == "hello-world"
    
    # 2. Test slug validation
    assert is_valid_slug("my-workspace") is True
    assert is_valid_slug("my_workspace") is False # Underscores invalid
    assert is_valid_slug("-my-workspace") is False # Leading dash invalid
    assert is_valid_slug("a" * 81) is False # Length check

@pytest.mark.asyncio
async def test_user_soft_delete(db_session: AsyncSession) -> None:
    # 1. Create a user
    user = User(
        email="test@nomen.ai",
        password_hash="hashed_password",
        role="FREE_USER",
        status="ACTIVE"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.deleted_at is None
    
    # 2. Soft delete the user
    user.soft_delete()
    await db_session.commit()
    
    # Re-fetch user
    stmt = select(User).where(User.id == user.id)
    refetched = (await db_session.execute(stmt)).scalar()
    assert refetched is not None
    assert refetched.deleted_at is not None
    assert isinstance(refetched.deleted_at, datetime)

@pytest.mark.asyncio
async def test_optimistic_locking_collision(db_session: AsyncSession) -> None:
    # 1. Create a workspace
    ws = Workspace(slug="lock-test", display_name="Lock Test Workspace")
    db_session.add(ws)
    await db_session.commit()
    await db_session.refresh(ws)
    
    original_version = ws.version_id
    assert original_version == 1
    
    # 2. Simulate concurrent updates using direct SQL update on the connection
    from sqlalchemy import update
    conn = await db_session.connection()
    await conn.execute(
        update(Workspace)
        .where(Workspace.id == ws.id)
        .values(display_name="First Update Winner", version_id=2)
    )
    
    # ws in our db_session still has version_id=1 in its internal state.
    # Attempting to modify and commit it will result in StaleDataError.
    ws.display_name = "Stale Update Loser"
    
    with pytest.raises(StaleDataError):
        await db_session.commit()

@pytest.mark.asyncio
async def test_generation_job_metadata(db_session: AsyncSession) -> None:
    # 1. Create Workspace & Project parent nodes
    ws = Workspace(slug="metadata-test", display_name="Meta Test")
    db_session.add(ws)
    await db_session.commit()
    await db_session.refresh(ws)
    
    proj = Project(
        workspace_id=ws.id,
        prompt="Testing metadata logs",
        selected_tlds=[".com", ".io"]
    )
    db_session.add(proj)
    await db_session.commit()
    await db_session.refresh(proj)
    
    # 2. Add Generation Job
    job = GenerationJob(
        project_id=proj.id,
        status="SUCCESS",
        model_name="gemini-1.5-flash",
        engine_version="v1.0.0",
        prompt_version="v1.2",
        latency_ms=1250,
        token_usage={"prompt_tokens": 150, "completion_tokens": 80},
        cost_estimate=0.00034
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    assert job.id is not None
    assert job.token_usage["prompt_tokens"] == 150
    assert job.cost_estimate == 0.00034
