import pytest
import uuid
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Notification
from app.models.workspace import Workspace, Project
from app.models.brand import GeneratedName, GenerationJob
from app.models.collaboration import (
    CommentThread, Comment, Favorite, Collection,
    CollectionItem, ActivityEvent, Mention, SearchHistory
)
from app.services.collaboration.comments import CommentsService
from app.services.collaboration.favorites import FavoritesService
from app.services.collaboration.collections import CollectionsService
from app.services.collaboration.notifications import NotificationsService
from app.services.collaboration.activity import ActivityService
from app.services.collaboration.search import SearchService

@pytest.mark.asyncio
async def test_comments_flow(db_session: AsyncSession) -> None:
    # 1. Setup workspace, project, name, and user
    user = User(email="collab-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="collab-test", display_name="Collaboration Test Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    project = Project(workspace_id=ws.id, prompt="Naming campaign", selected_tlds=[".com"])
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    gname = GeneratedName(
        project_id=project.id,
        name_string="TestBrand",
        style="Abstract",
        model_name="gemini-1.5-flash",
        temperature=0.7,
        prompt_tokens=100,
        completion_tokens=50,
        generation_version=1
    )
    db_session.add(gname)
    await db_session.commit()
    await db_session.refresh(gname)

    comments_service = CommentsService(db_session)
    
    # 2. Get or create thread
    thread = await comments_service.get_or_create_thread(ws.id, project.id, gname.id)
    assert thread is not None
    assert thread.name_id == gname.id
    assert thread.is_resolved is False

    # 3. Add comment
    comment1 = await comments_service.add_comment(thread.id, user.id, "This brand sounds awesome! @collab-user")
    assert comment1 is not None
    assert comment1.content == "This brand sounds awesome! @collab-user"
    assert comment1.is_pinned is False

    # 4. Resolve thread
    resolved_thread = await comments_service.resolve_thread(thread.id, user.id)
    assert resolved_thread.is_resolved is True
    assert resolved_thread.resolved_by == user.id

    # 5. List comments
    all_comments = await comments_service.list_comments_by_name(gname.id)
    assert len(all_comments) == 1
    assert all_comments[0].content == comment1.content

@pytest.mark.asyncio
async def test_favorites_flow(db_session: AsyncSession) -> None:
    user = User(email="fav-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="fav-test", display_name="Favorite Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    project = Project(workspace_id=ws.id, prompt="Favorites campaign", selected_tlds=[".com"])
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    gname = GeneratedName(
        project_id=project.id,
        name_string="FavBrand",
        style="Abstract",
        model_name="gemini-1.5-flash",
        temperature=0.7,
        prompt_tokens=100,
        completion_tokens=50,
        generation_version=1
    )
    db_session.add(gname)
    await db_session.commit()
    await db_session.refresh(gname)

    fav_service = FavoritesService(db_session)

    # 1. Star the name
    starred = await fav_service.toggle_favorite(user.id, ws.id, gname.id)
    assert starred is True
    
    is_fav = await fav_service.is_favorite(user.id, gname.id)
    assert is_fav is True

    # 2. List favorites
    favs = await fav_service.list_workspace_favorites(ws.id, user.id)
    assert len(favs) == 1
    assert favs[0].name_id == gname.id

    # 3. Unstar the name
    starred = await fav_service.toggle_favorite(user.id, ws.id, gname.id)
    assert starred is False
    
    is_fav = await fav_service.is_favorite(user.id, gname.id)
    assert is_fav is False

@pytest.mark.asyncio
async def test_collections_flow(db_session: AsyncSession) -> None:
    user = User(email="col-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="col-test", display_name="Collection Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    project = Project(workspace_id=ws.id, prompt="Collections campaign", selected_tlds=[".com"])
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    gname = GeneratedName(
        project_id=project.id,
        name_string="ColBrand",
        style="Abstract",
        model_name="gemini-1.5-flash",
        temperature=0.7,
        prompt_tokens=100,
        completion_tokens=50,
        generation_version=1
    )
    db_session.add(gname)
    await db_session.commit()
    await db_session.refresh(gname)

    col_service = CollectionsService(db_session)

    # 1. Create collection
    col = await col_service.create_collection(ws.id, user.id, "Tech Names", "Best tech branding options")
    assert col is not None
    assert col.name == "Tech Names"
    assert col.description == "Best tech branding options"

    # 2. Add name to collection
    item = await col_service.add_name_to_collection(col.id, gname.id)
    assert item is not None
    assert item.collection_id == col.id
    assert item.name_id == gname.id

    # 3. List collection items
    items = await col_service.list_items_by_collection(col.id)
    assert len(items) == 1

    # 4. Remove item
    removed = await col_service.remove_name_from_collection(col.id, gname.id)
    assert removed is True

@pytest.mark.asyncio
async def test_activity_events(db_session: AsyncSession) -> None:
    user = User(email="act-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="act-test", display_name="Activity Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    act_service = ActivityService(db_session)
    event = await act_service.log_activity(
        workspace_id=ws.id,
        user_id=user.id,
        action_type="project_created",
        description="Created a brand research campaign folder."
    )
    assert event is not None
    assert event.action_type == "project_created"

    activities = await act_service.list_workspace_activity(ws.id)
    assert len(activities) == 1
    assert activities[0].description == "Created a brand research campaign folder."

@pytest.mark.asyncio
async def test_search_service(db_session: AsyncSession) -> None:
    user = User(email="search-user@nomen.ai", password_hash="hash", role="FREE_USER", status="ACTIVE")
    ws = Workspace(slug="search-test", display_name="Search Workspace")
    db_session.add_all([user, ws])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(ws)

    project = Project(workspace_id=ws.id, prompt="AI brand names", selected_tlds=[".com"])
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    search_service = SearchService(db_session)
    
    # Search history logging
    await search_service.add_to_history(user.id, ws.id, "AI branding")
    recents = await search_service.get_recent_searches(user.id, ws.id)
    assert "AI branding" in recents

    # Search results
    results = await search_service.search_all(user.id, ws.id, "brand")
    assert "projects" in results
    assert len(results["projects"]) == 1
    assert results["projects"][0]["prompt"] == "AI brand names"
