import os
import pytest
from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.base import Base

# Detect database configuration, fallback to SQLite in-memory for zero-dependency tests
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# Async engine creation
engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _is_sqlite(connection):
    """Returns True when running against SQLite (skips JSONB/UUID-incompatible DDL)."""
    return connection.dialect.name == "sqlite"


@pytest.fixture(scope="session", autouse=True)
async def prepare_database(request) -> AsyncGenerator[None, None]:
    """Sets up the schema in the test database once per session.
    
    Skips DDL for pure unit-test modules (billing, saas) that only use mocks.
    """
    skip_ddl_modules = {"test_billing", "test_saas"}
    # Check if all collected items are from mock-only modules
    all_mock = all(
        item.module.__name__.split(".")[-1] in skip_ddl_modules
        for item in request.session.items
        if hasattr(item, "module")
    )
    if not all_mock:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception:
            pass  # Skip if DB not available (pure unit test environment)
    yield
    if not all_mock:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            pass


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Session fixture utilizing nested transactions to roll back changes after every test."""
    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            async with TestingSessionLocal(bind=connection) as session:
                yield session
                # Rollback automatically cancels all database modifications made during the test
                await transaction.rollback()
