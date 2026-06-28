# API Design: Nomen

This document details the REST API specifications for Nomen v1.0. All endpoints run under prefix `/api/v1` and communicate using JSON.

---

## 1. Authentication Endpoints

### 1.1. User Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Description**: Registers a new user account.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Responses**:
  - `201 Created`: User created successfully.
    ```json
    {
      "id": "e4b934b1-8b94-4d89-9a7c-12f5a6f87d41",
      "email": "user@example.com",
      "role": "free_user",
      "created_at": "2026-06-28T20:24:00Z"
    }
    ```
  - `400 Bad Request`: Email already registered.

### 1.2. User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: Authenticates user credentials. Returns JWT in HttpOnly cookie.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Responses**:
  - `200 OK`: Cookie set. Returns user metadata:
    ```json
    {
      "user": {
        "id": "e4b934b1-8b94-4d89-9a7c-12f5a6f87d41",
        "email": "user@example.com",
        "role": "free_user"
      }
    }
    ```
  - `401 Unauthorized`: Invalid credentials.

---

## 2. Search & Generation Endpoints

### 2.1. Trigger Name Generation (Async Task)
- **Endpoint**: `POST /api/v1/search/generate`
- **Description**: Enqueues a search query task to Celery.
- **Request Body**:
  ```json
  {
    "prompt": "AI-powered brand intelligence software",
    "style": "compound",
    "tlds": [".com", ".io"],
    "max_length": 12
  }
  ```
- **Responses**:
  - `202 Accepted`: Job enqueued successfully.
    ```json
    {
      "task_id": "job_a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "status": "PENDING"
    }
    ```
  - `429 Too Many Requests`: Rate limit exceeded.

### 2.2. Poll Generation Task Status
- **Endpoint**: `GET /api/v1/search/status/{task_id}`
- **Description**: Fetches job status and payload if complete.
- **Responses**:
  - `200 OK (In Progress)`:
    ```json
    {
      "task_id": "job_a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "status": "PROCESSING",
      "progress": 0.45
    }
    ```
  - `200 OK (Completed)`:
    ```json
    {
      "task_id": "job_a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "status": "SUCCESS",
      "results": [
        {
          "name": "Nomen",
          "style": "abstract",
          "brand_score": 94,
          "syllables": 2,
          "pronunciation_index": 0.95,
          "domains": [
            { "tld": ".com", "available": true, "price": null },
            { "tld": ".io", "available": false, "price": 4500.00 }
          ],
          "trademark_summary": {
            "status": "clear",
            "matches_count": 0
          }
        }
      ]
    }
    ```

---

## 3. Brand Detail & Validation Endpoints

### 3.1. Fetch Detailed Brand Information
- **Endpoint**: `GET /api/v1/brands/{name}/details`
- **Description**: Fetches deeper data (phonetics, full trademark records, embeddings, semantic collision checks).
- **Responses**:
  - `200 OK`:
    ```json
    {
      "name": "Nomen",
      "pronunciation": {
        "ipa": "/ˈnoʊ.mən/",
        "syllables": ["no", "men"],
        "pronounceability_score": 9.5
      },
      "trademarks": [
        {
          "jurisdiction": "US",
          "status": "clear",
          "conflicts": []
        }
      ],
      "semantic_similarity": [
        { "name": "Nomenlix", "similarity": 0.74, "vertical": "Naming tools" }
      ]
    }
    ```

---

## 4. Portfolios & Collections Endpoints (Authenticated)

### 4.1. Get User Portfolios
- **Endpoint**: `GET /api/v1/portfolios`
- **Headers**: `Authorization: Bearer <token>` (or cookies)
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "portfolio_id": "c1f7a2db-6543-4bcd-8ef0-5712e624fcd8",
        "name": "My Tech Startup Names",
        "items_count": 4,
        "created_at": "2026-06-28T20:25:00Z"
      }
    ]
    ```

### 4.2. Add Name to Portfolio
- **Endpoint**: `POST /api/v1/portfolios/{portfolio_id}/names`
- **Request Body**:
  ```json
  {
    "name": "Nomen",
    "style": "abstract",
    "brand_score": 94
  }
  ```
- **Responses**:
  - `201 Created`: Added successfully.

---

## 5. Export Endpoint (Authenticated)

### 5.1. Request Brand Asset ZIP Compile
- **Endpoint**: `POST /api/v1/export/bundle`
- **Request Body**:
  ```json
  {
    "name": "Nomen",
    "palette": {
      "primary": "#3b82f6",
      "secondary": "#1e3a8a",
      "background": "#ffffff"
    },
    "typography": {
      "heading": "Inter",
      "body": "Outfit"
    }
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "export_id": "exp_7f6e5d4c-3b2a-1c0d-e9f8-a7b6c5d4e3f2",
      "download_url": "https://r2.nomen.ai/exports/exp_7f6e5d4c.zip?token=presigned_token"
    }
    ```
