import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collaboration import Mention
from app.repositories.collaboration import SqlAlchemyMentionRepository

class MentionsService:
    """Manages queries and dispatches for user mentions inside workspace comments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SqlAlchemyMentionRepository(db)

    async def get_user_mentions(self, user_id: uuid.UUID) -> Sequence[Mention]:
        """Retrieves all mentions mapping to a specific user ID."""
        return await self.repo.list_by_user(user_id)
        
    async def create_mention_link(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> Mention:
        """Saves a direct association linking comments to mentioned users."""
        mention = Mention(comment_id=comment_id, user_id=user_id)
        mention = await self.repo.create(mention)
        await self.db.flush()
        return mention
