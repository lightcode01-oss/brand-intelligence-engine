import uuid
from abc import abstractmethod
from typing import Optional, Sequence
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import AbstractRepository
from app.repositories.auth import SqlAlchemyRepository
from app.models.collaboration import (
    CommentThread, Comment, Favorite, Collection,
    CollectionItem, ActivityEvent, Mention, SearchHistory
)

# ---------------------------------------------------------------------------
# Abstract Repository Definitions
# ---------------------------------------------------------------------------

class AbstractCommentThreadRepository(AbstractRepository[CommentThread]):
    @abstractmethod
    async def get_by_name(self, name_id: uuid.UUID) -> Optional[CommentThread]:
        pass

class AbstractCommentRepository(AbstractRepository[Comment]):
    @abstractmethod
    async def list_by_thread(self, thread_id: uuid.UUID) -> Sequence[Comment]:
        pass

class AbstractFavoriteRepository(AbstractRepository[Favorite]):
    @abstractmethod
    async def get_by_user_and_name(self, user_id: uuid.UUID, name_id: uuid.UUID) -> Optional[Favorite]:
        pass
    
    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> Sequence[Favorite]:
        pass

class AbstractCollectionRepository(AbstractRepository[Collection]):
    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[Collection]:
        pass

class AbstractCollectionItemRepository(AbstractRepository[CollectionItem]):
    @abstractmethod
    async def list_by_collection(self, collection_id: uuid.UUID) -> Sequence[CollectionItem]:
        pass
    
    @abstractmethod
    async def get_item(self, collection_id: uuid.UUID, name_id: uuid.UUID) -> Optional[CollectionItem]:
        pass

class AbstractActivityEventRepository(AbstractRepository[ActivityEvent]):
    @abstractmethod
    async def list_by_workspace(self, workspace_id: uuid.UUID, limit: int = 50) -> Sequence[ActivityEvent]:
        pass

class AbstractMentionRepository(AbstractRepository[Mention]):
    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[Mention]:
        pass

class AbstractSearchHistoryRepository(AbstractRepository[SearchHistory]):
    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID, workspace_id: uuid.UUID, limit: int = 10) -> Sequence[SearchHistory]:
        pass

# ---------------------------------------------------------------------------
# Concrete SQLAlchemy Implementations
# ---------------------------------------------------------------------------

class SqlAlchemyCommentThreadRepository(SqlAlchemyRepository, AbstractCommentThreadRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CommentThread)

    async def get_by_name(self, name_id: uuid.UUID) -> Optional[CommentThread]:
        stmt = select(CommentThread).where(CommentThread.name_id == name_id, CommentThread.deleted_at == None)
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemyCommentRepository(SqlAlchemyRepository, AbstractCommentRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Comment)

    async def list_by_thread(self, thread_id: uuid.UUID) -> Sequence[Comment]:
        stmt = select(Comment).where(Comment.thread_id == thread_id, Comment.deleted_at == None).order_by(Comment.created_at)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemyFavoriteRepository(SqlAlchemyRepository, AbstractFavoriteRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Favorite)

    async def get_by_user_and_name(self, user_id: uuid.UUID, name_id: uuid.UUID) -> Optional[Favorite]:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.name_id == name_id,
            Favorite.deleted_at == None
        )
        return (await self.db.execute(stmt)).scalar()

    async def list_by_workspace(self, workspace_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> Sequence[Favorite]:
        stmt = select(Favorite).where(Favorite.workspace_id == workspace_id, Favorite.deleted_at == None)
        if user_id:
            stmt = stmt.where(Favorite.user_id == user_id)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemyCollectionRepository(SqlAlchemyRepository, AbstractCollectionRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Collection)

    async def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[Collection]:
        stmt = select(Collection).where(Collection.workspace_id == workspace_id, Collection.deleted_at == None)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemyCollectionItemRepository(SqlAlchemyRepository, AbstractCollectionItemRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CollectionItem)

    async def list_by_collection(self, collection_id: uuid.UUID) -> Sequence[CollectionItem]:
        stmt = select(CollectionItem).where(CollectionItem.collection_id == collection_id, CollectionItem.deleted_at == None)
        return (await self.db.execute(stmt)).scalars().all()

    async def get_item(self, collection_id: uuid.UUID, name_id: uuid.UUID) -> Optional[CollectionItem]:
        stmt = select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.name_id == name_id,
            CollectionItem.deleted_at == None
        )
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemyActivityEventRepository(SqlAlchemyRepository, AbstractActivityEventRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ActivityEvent)

    async def list_by_workspace(self, workspace_id: uuid.UUID, limit: int = 50) -> Sequence[ActivityEvent]:
        stmt = select(ActivityEvent).where(ActivityEvent.workspace_id == workspace_id).order_by(desc(ActivityEvent.created_at)).limit(limit)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemyMentionRepository(SqlAlchemyRepository, AbstractMentionRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Mention)

    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[Mention]:
        stmt = select(Mention).where(Mention.user_id == user_id)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemySearchHistoryRepository(SqlAlchemyRepository, AbstractSearchHistoryRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SearchHistory)

    async def list_by_user(self, user_id: uuid.UUID, workspace_id: uuid.UUID, limit: int = 10) -> Sequence[SearchHistory]:
        stmt = select(SearchHistory).where(
            SearchHistory.user_id == user_id,
            SearchHistory.workspace_id == workspace_id
        ).order_by(desc(SearchHistory.created_at)).limit(limit)
        return (await self.db.execute(stmt)).scalars().all()
