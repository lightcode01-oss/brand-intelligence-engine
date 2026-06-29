import uuid
from typing import Optional, Sequence, List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace, Project
from app.models.brand import GeneratedName
from app.models.collaboration import Favorite, Collection, SearchHistory

class SearchService:
    """Provides query parameters matching workspaces, projects, names, and collections."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_to_history(self, user_id: uuid.UUID, workspace_id: uuid.UUID, query: str):
        """Saves a search query string to user histories registry."""
        if not query.strip():
            return
        history = SearchHistory(
            user_id=user_id,
            workspace_id=workspace_id,
            query=query.strip()
        )
        self.db.add(history)
        await self.db.flush()

    async def get_recent_searches(self, user_id: uuid.UUID, workspace_id: uuid.UUID, limit: int = 5) -> List[str]:
        """Retrieves list of recent unique queries searched by user."""
        stmt = select(SearchHistory.query).where(
            SearchHistory.user_id == user_id,
            SearchHistory.workspace_id == workspace_id
        ).order_by(desc(SearchHistory.created_at)).limit(limit * 2) # Fetch extra to filter duplicates
        
        results = (await self.db.execute(stmt)).scalars().all()
        
        unique = []
        for q in results:
            if q not in unique:
                unique.append(q)
            if len(unique) >= limit:
                break
        return unique

    async def search_all(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID, query: str,
        skip: int = 0, limit: int = 50
    ) -> Dict[str, Any]:
        """Searches across projects, names, favorites, and collections inside a workspace context."""
        query_pattern = f"%{query.strip().lower()}%"
        
        # 1. Search Projects prompt
        proj_stmt = select(Project).where(
            Project.workspace_id == workspace_id,
            Project.prompt.ilike(query_pattern),
            Project.deleted_at == None
        ).offset(skip).limit(limit)
        projects = (await self.db.execute(proj_stmt)).scalars().all()
        
        # 2. Search GeneratedNames matching project list
        name_stmt = select(GeneratedName).join(Project).where(
            Project.workspace_id == workspace_id,
            GeneratedName.name_string.ilike(query_pattern),
            GeneratedName.deleted_at == None
        ).offset(skip).limit(limit)
        names = (await self.db.execute(name_stmt)).scalars().all()
        
        # 3. Search Collections
        col_stmt = select(Collection).where(
            Collection.workspace_id == workspace_id,
            Collection.name.ilike(query_pattern),
            Collection.deleted_at == None
        ).offset(skip).limit(limit)
        collections = (await self.db.execute(col_stmt)).scalars().all()
        
        # 4. Search Favorites (joins generated names)
        fav_stmt = select(Favorite).join(GeneratedName).where(
            Favorite.workspace_id == workspace_id,
            GeneratedName.name_string.ilike(query_pattern),
            Favorite.deleted_at == None
        ).offset(skip).limit(limit)
        favorites = (await self.db.execute(fav_stmt)).scalars().all()
        
        # Save query to history
        await self.add_to_history(user_id, workspace_id, query)
        
        return {
            "projects": [
                {"id": str(p.id), "prompt": p.prompt, "created_at": p.created_at.isoformat()} for p in projects
            ],
            "names": [
                {"id": str(n.id), "name_string": n.name_string, "style": n.style} for n in names
            ],
            "collections": [
                {"id": str(c.id), "name": c.name, "description": c.description} for c in collections
            ],
            "favorites": [
                {"id": str(f.id), "name_id": str(f.name_id), "name_string": f.name_ref.name_string} for f in favorites
            ]
        }
