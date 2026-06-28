# Testing Strategy: Nomen

This document details the testing architecture, database transaction isolation models, external API mock strategies, and coverage goals for Nomen.

---

## 1. The Testing Pyramid

To ensure platform reliability without slowing down development cycles, Nomen enforces three layers of testing:

```text
                  ▲
                 / \
                /   \     E2E: Playwright (Core user flow validation)
               / E2E \    ~10% of test suite
              /───────\
             /         \  Integration: Pytest client requests & DB writes
            /  INTEG.  \  ~30% of test suite
           /────────────\
          /              \ Unit: Math algorithms (BSI, IPA, G2P mappings)
         /      UNIT      \ ~60% of test suite
        /__________________\
```

---

## 2. Backend Testing Specifications (pytest)

All Python unit and integration tests run under **pytest**.

### 2.1. Test Database Isolation (Transaction Rollback Pattern)
Integration tests must write to a separate test database (`nomen_test_db`) and roll back changes after every single test. This prevents state contamination and eliminates the need to wipe/re-create schemas between tests.

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.api.deps import get_db

TEST_DATABASE_URL = "postgresql+asyncpg://nomen_user:test_pass@postgres:5432/nomen_test_db"
engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    # Set up tables in test database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after session finishes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncSession:
    # Use nested transactions (SAVEPOINT) to rollback writes
    connection = await engine.connect()
    transaction = await connection.begin_nested()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    await session.close()
    await transaction.rollback()
    await connection.close()
```

### 2.2. Mocking External Gateways
We mock expensive network dependencies using `unittest.mock` or `pytest-mock` decorators:
- **LLM Generators**: Return a pre-configured static JSON candidate array.
- **DNS / WHOIS Checkers**: Mock DNS sockets to return instant positive/negative resolutions.
- **Scrapers**: Return cached HTML blocks.

---

## 3. Frontend Testing Specifications (Vitest & Playwright)

### 3.1. Unit and Component Tests (Vitest + React Testing Library)
- Test client-side formatting functions (syllable calculations, class name mergers).
- Component state validation: Verifying that components (e.g. `BrandScoreCircle`, filter slide drawer) mount and toggle states correctly based on properties.

### 3.2. End-to-End (E2E) Browser Tests (Playwright)
Playwright spins up headless browser instances (Chromium, Firefox, WebKit) and mimics real users executing the critical search flow:
- Enter prompt in home search, click submit.
- Assert that loading state shows.
- Wait for polled results to render.
- Click card, open brand drawer, verify that mockups render correctly.
- Click "Save Name" and verify redirection to login.

---

## 4. Coverage Metrics Target

- **Core Code Target**: **80% coverage** threshold across Python backend and Next.js frontend codebases.
- **BSI & Phonetic Scorer**: Enforces **100% test coverage** for the calculation algorithms (`18_brand_scoring_engine.md` and `19_pronunciation_engine.md`) to guarantee that score cards never return undefined values or crash.
- **CI Enforcement**: Pipelines automatically fail if coverage metrics fall below target benchmarks.
