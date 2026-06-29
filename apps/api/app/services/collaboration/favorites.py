import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collaboration import Favorite
from app.repositories.collaboration import SqlAlchemyFavoriteRepository

class FavoritesService:
    """Manages workspace brand candidate star markers and listings."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SqlAlchemyFavoriteRepository(db)

    async def toggle_favorite(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID, name_id: uuid.UUID
    ) -> bool:
        """Stars or unstars a name. Returns True if starred, False if unstarred."""
        fav = await self.repo.get_by_user_and_name(user_id, name_id)
        if fav:
            await self.repo.delete(fav.id)
            await self.db.flush()
            return False
        else:
            fav = Favorite(
                user_id=user_id,
                workspace_id=workspace_id,
                name_id=name_id
            )
            await self.repo.create(fav)
            await self.db.flush()
            return True

    async def list_workspace_favorites(
        self, workspace_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> Sequence[Favorite]:
        """Lists starred names inside a workspace, optionally filtered by user ID."""
        return await self.repo.list_by_workspace(workspace_id, user_id=user_id)
        
    async def is_favorite(self, user_id: uuid.UUID, name_id: uuid.UUID) -> bool:
        """Checks if a user has favorited a specific name candidate."""
        fav = await self.repo.get_by_user_and_name(user_id, name_id)
        return fav is not None
