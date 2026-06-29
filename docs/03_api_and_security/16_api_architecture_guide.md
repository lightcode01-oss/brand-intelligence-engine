# API Architecture & Contracts Guide: Nomen

This document details Nomen's core API foundation, middleware pipelines, error formats, validation rules, and dependency structures.

---

## 1. Application Layer Structure

The API is built using **FastAPI (ASGI)**, organized around a modular, clean-layered architecture:

```text
HTTP Request
     │
     ▼
┌───────────────────────────────┐
│       Middleware Pipeline     │ (RequestID, Logging, Timing, Security, GZip)
└────────────┬──────────────────┘
             │
             ▼
┌───────────────────────────────┐
│        API Controllers        │ (api/v1/ routes - serializes Pydantic contracts)
└────────────┬──────────────────┘
             │
             ▼
┌───────────────────────────────┐
│        Services (ABCs)        │ (Business logic layer - purely decoupled interfaces)
└────────────┬──────────────────┘
             │
             ▼
┌───────────────────────────────┐
│     Repositories (ABCs)       │ (Data access layer - SQLAlchemy operations)
└───────────────────────────────┘
```

---

## 2. Global Request/Response Envelope Specification

All endpoints return a standardized, type-safe envelope payload wrapper:

```json
{
  "success": true,
  "message": "Human-readable status summary.",
  "data": {},
  "meta": {
    "request_id": "uuid-correlation-string",
    "timestamp": "2026-06-28T22:54:00Z",
    "api_version": "1.0.0"
  },
  "errors": []
}
```

### Response Field Specifications
- **`success`** (Boolean): Indicates whether the transaction resolved successfully.
- **`message`** (String): Contextual details outlining success or user instructions.
- **`data`** (JSON Object/Array/Null): The response resource payload.
- **`meta`** (Object): Contains the trace `request_id`, completion `timestamp` (UTC), and target `api_version`.
- **`errors`** (List of Strings): Validation details or warning codes.

---

## 3. Global Exception & Error Code Reference

When exceptions occur, global interceptors catch and map them into standard error structures:

| HTTP Status | Exception Class | Errors Content | Rationale |
| :--- | :--- | :--- | :--- |
| **401** | `AuthenticationError` | `["UNAUTHORIZED"]` | Missing or invalid auth tokens. |
| **403** | `AuthorizationError` | `["FORBIDDEN"]` | Permission violations. |
| **409** | `IntegrityError` | `["Database conflict details"]` | Unique key or database constraint failures. |
| **422** | `RequestValidationError` | `["field: error description"]` | Pydantic validation failures. |
| **429** | `RateLimitError` | `["RATE_LIMIT_EXCEEDED"]` | Request limit hit. |
| **500** | `UnexpectedException` | `["Internal traceback details"]` | Systems runtime exceptions. |

---

## 4. REST API Endpoint Inventory (v1)

### 4.1. Health & Telemetry
- `GET /api/v1/health`: Basic container health check.
- `GET /api/v1/ready`: Readiness checker (verifies active database ping).
- `GET /api/v1/live`: Liveness checker reporting process uptime.
- `GET /api/v1/version`: Semantic version parameter indicator.
- `GET /api/v1/metrics`: Telemetry logs placeholder.

### 4.2. Workspace Collaboration
- `POST /api/v1/workspaces/`: Creates a new workspace.
- `GET /api/v1/workspaces/`: Lists user workspaces (Paginated & Filtered).
- `GET /api/v1/workspaces/{workspace_id}`: Retrieves workspace attributes.
- `PUT /api/v1/workspaces/{workspace_id}`: Renames workspace or edits URL slugs.
- `DELETE /api/v1/workspaces/{workspace_id}`: Soft-deletes a workspace.
- `POST /api/v1/workspaces/{workspace_id}/members`: Assigns user membership.

### 4.3. Naming Projects
- `POST /api/v1/projects/`: Creates a new project inside a workspace.
- `GET /api/v1/projects/`: Lists active projects (Filtered).
- `GET /api/v1/projects/{project_id}`: Retrieves project search filters.
- `PUT /api/v1/projects/{project_id}`: Updates prompt text or TLD constraints.
- `DELETE /api/v1/projects/{project_id}`: Soft-deletes a project.

### 4.4. AI Name Generation & Checks
- `POST /api/v1/projects/{project_id}/generate`: Triggers async Celery search task.
- `GET /api/v1/jobs/{job_id}`: Polls task status and usage metadata.
- `GET /api/v1/projects/{project_id}/names`: Lists generated candidates (Paginated).
- `PUT /api/v1/names/{name_id}`: Updates candidate lifecycle (`SAVED`, `ARCHIVED`).
- `DELETE /api/v1/names/{name_id}`: Hard-deletes a temporary candidate.
- `GET /api/v1/names/{name_id}/domains`: Retrieves cached TLD checks.
- `GET /api/v1/names/{name_id}/trademarks`: Retrieves cached trademark clearance logs.

### 4.5. Exports & Flags
- `POST /api/v1/exports/`: Compiles logo SVGs into a downloadable zip file.
- `GET /api/v1/exports/`: Lists user export requests.
- `GET /api/v1/feature-flags/`: Lists enabled features (for client UI rollouts).

---

## 5. Dependency Injection Diagram

FastAPI manages resource lifecycles through its dependency injection framework:

```text
                        ┌──────────────────┐
                        │   FastAPI Route  │
                        └────────┬─────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   get_db_session │    │ get_current_user │    │   get_settings   │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         ▼                       ▼                       ▼
  [SQLAlchemy Session]     [User Model]          [Pydantic Settings]
```
