import uuid
from typing import Optional, Sequence, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collaboration import Collection, CollectionItem
from app.repositories.collaboration import SqlAlchemyCollectionRepository, SqlAlchemyCollectionItemRepository

class CollectionsService:
    """Manages workspace brand folders, member permissions, and items assignments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.collection_repo = SqlAlchemyCollectionRepository(db)
        self.item_repo = SqlAlchemyCollectionItemRepository(db)

    async def create_collection(
        self, workspace_id: uuid.UUID, created_by: uuid.UUID, name: str, description: Optional[str] = None
    ) -> Collection:
        """Creates a brand candidate collection folder inside a workspace."""
        col = Collection(
            workspace_id=workspace_id,
            name=name,
            description=description,
            created_by=created_by
        )
        col = await self.collection_repo.create(col)
        await self.db.flush()
        return col

    async def update_collection(
        self, collection_id: uuid.UUID, name: str, description: Optional[str] = None
    ) -> Optional[Collection]:
        """Updates collection metadata folder name/description."""
        col = await self.collection_repo.get(collection_id)
        if not col:
            return None
        col.name = name
        col.description = description
        col = await self.collection_repo.update(col)
        await self.db.flush()
        return col

    async def delete_collection(self, collection_id: uuid.UUID) -> bool:
        """Deletes a collection folder and cascades items mapping deletions."""
        # 1. Clean up items maps first
        stmt = delete(CollectionItem).where(CollectionItem.collection_id == collection_id)
        await self.db.execute(stmt)
        # 2. Delete parent
        success = await self.collection_repo.delete(collection_id)
        await self.db.flush()
        return success

    async def list_workspace_collections(self, workspace_id: uuid.UUID) -> Sequence[Collection]:
        """Lists folders visible within a workspace."""
        return await self.collection_repo.list_by_workspace(workspace_id)

    async def add_name_to_collection(self, collection_id: uuid.UUID, name_id: uuid.UUID) -> CollectionItem:
        """Associates a name candidate to a collection folder."""
        item = await self.item_repo.get_item(collection_id, name_id)
        if not item:
            item = CollectionItem(
                collection_id=collection_id,
                name_id=name_id
            )
            item = await self.item_repo.create(item)
            await self.db.flush()
        return item

    async def remove_name_from_collection(self, collection_id: uuid.UUID, name_id: uuid.UUID) -> bool:
        """Removes a name candidate reference mapping from a collection folder."""
        item = await self.item_repo.get_item(collection_id, name_id)
        if item:
            await self.item_repo.delete(item.id)
            await self.db.flush()
            return True
        return False

    async def move_name(self, source_collection_id: uuid.UUID, dest_collection_id: uuid.UUID, name_id: uuid.UUID) -> bool:
        """Moves a candidate name reference between folder collections."""
        # 1. Remove from source
        removed = await self.remove_name_from_collection(source_collection_id, name_id)
        # 2. Add to destination
        if removed:
            await self.add_name_to_collection(dest_collection_id, name_id)
            return True
        return False

    async def list_items_by_collection(self, collection_id: uuid.UUID) -> Sequence[CollectionItem]:
        """Retrieves items grouped inside a collection."""
        return await self.item_repo.list_by_collection(collection_id)
