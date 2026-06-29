from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider supplying a scoped transactional async database session."""
    async with async_session_maker() as session:
        yield session
