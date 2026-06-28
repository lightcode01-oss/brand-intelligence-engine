# Backend Architecture: Nomen

This document specifies the internal architecture of Nomen's backend application, built using **FastAPI (Python 3.12)** and **Celery**.

---

## 1. Directory Structure

The backend application is structured as a modular monolith to keep execution clean and scalable:

```text
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py                 <-- FastAPI application initialization
│   ├── core/
│   │   ├── config.py           <-- Pydantic BaseSettings config loading
│   │   ├── database.py         <-- SQLAlchemy AsyncSession setup
│   │   ├── security.py         <-- Password hashing and JWT generation
│   │   └── cel_app.py          <-- Celery instance config
│   ├── models/                 <-- SQLAlchemy SQL Models
│   │   ├── user.py
│   │   ├── name.py
│   │   └── checks.py
│   ├── schemas/                <-- Pydantic validation schemas
│   │   ├── user.py
│   │   ├── search.py
│   │   └── brand.py
│   ├── api/                    <-- REST API routes
│   │   ├── deps.py             <-- FastAPI dependency injection definitions
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── search.py
│   │   │   └── brands.py
│   └── workers/                <-- Celery task implementations
│       ├── tasks.py            <-- Celery entry points
│       ├── brand_gen.py        <-- AI Generator integrations
│       ├── dns_check.py        <-- dnspython checking logic
│       └── trademark_scr.py   <-- USPTO/EUIPO scraping logic
├── alembic/                    <-- DB Migrations
├── tests/                      <-- Unit & integration tests
├── Dockerfile                  <-- Backend app build script
└── requirements.txt            <-- Backend Python dependencies
```

---

## 2. Concurrency & Async Processing Model

FastAPI runs on an ASGI server (Uvicorn), allowing it to handle thousands of concurrent requests by shifting I/O operations to an asynchronous loop.

### 2.1. Async DB Operations (asyncpg)
We use `asyncpg` as the PostgreSQL database driver. All database operations use `SQLAlchemy`'s async session builder (`AsyncSession`), which releases control to the event loop during DB queries:
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

### 2.2. Heavy CPU/Network Tasks -> Celery
Endpoints that make external blocking API calls (LLMs, DNS lookups, Web Scraping) must not run on the FastAPI event loop, as they will block the entire server. These tasks are queued to Celery workers via Redis.

---

## 3. Celery Task Queue Orchestration

Celery workers process long-running tasks asynchronously. We configure Celery with two distinct queues to prevent fast tasks (like single domain checks) from getting stuck behind slow tasks (like full trademark screening portfolios):

```text
               ┌─────────────┐
               │ FastAPI API │
               └──────┬──────┘
                      │
            Enqueue   │
                      ▼
               ┌─────────────┐
               │ Redis Broker│
               └──────┬──────┘
                      │
         ┌────────────┴────────────┐
         ▼ Route                   ▼ Route
  ┌──────────────┐          ┌──────────────┐
  │  "fast-queue"│          │ "heavy-queue"│
  └──────┬───────┘          └──────┬───────┘
         │                         │
         ▼ Consume                 ▼ Consume
  ┌──────────────┐          ┌──────────────┐
  │ DNS/WHOIS    │          │ LLM Generation│
  │ Check Worker │          │ Trademark Scrapes
  └──────────────┘          └──────────────┘
```

- **`fast-queue`**: Handles instant single domain availability lookups and pronunciation index calculations. Max execution time is under 1.5 seconds.
- **`heavy-queue`**: Handles the semantic AI generation pipeline and multi-registry trademark scrapes. Max execution time is 10 seconds.

### 3.1. Task Retry & Error Policies
To ensure resilience when interacting with rate-limited public registries, tasks implement exponential backoff retry states:
```python
@cel_app.task(bind=True, max_retries=3, default_retry_delay=5)
def scrape_uspto_task(self, name: str):
    try:
        return run_uspto_scraper(name)
    except ConnectionError as exc:
        # Retry with exponential backoff: 5s, 10s, 20s
        raise self.retry(exc=exc, countdown=self.request.retries * 5 + 5)
```

---

## 4. Key Libraries & Framework Integrations

- **Pydantic v2**: Handles request parsing, static typing, and schema serialization.
- **SQLAlchemy 2.0 (Async)**: Modern ORM configuration with strict type mapping.
- **LiteLLM**: Standardizes API calls to Google Gemini, Groq, or local Ollama instances.
- **structlog**: Provides structured JSON logging that integrates with Docker and Loki.
