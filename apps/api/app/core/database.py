import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://nomen_user:secure_dev_password_change_me@localhost:5432/nomen_db"
)

# Async engine creation
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    pool_size=20,
    max_overflow=10
)

# Session factory creation
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency session factory helper for FastAPI endpoints."""
    async with async_session_maker() as session:
        yield session
