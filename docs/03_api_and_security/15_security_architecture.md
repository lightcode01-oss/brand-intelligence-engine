# Security Architecture: Nomen

This document details the security principles, data protection mechanisms, rate-limiting rules, and defense configurations implemented across Nomen's application and infrastructure layers.

---

## 1. Network & Transport Security

- **Enforced TLS 1.3**: All public network communication requires HTTPS with cipher suites restricted to modern, secure configurations (e.g., TLS_AES_256_GCM_SHA384).
- **HTTP Strict Transport Security (HSTS)**: The server issues the HSTS header to ensure browsers only request the domain over HTTPS:
  ```http
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  ```
- **Cloudflare WAF (Web Application Firewall)**: Filters out generic SQL injection payloads, cross-site scripting (XSS) vectors, and anomalous bot traffic at the edge before hitting our application servers.

---

## 2. Application Layer Protections

### 2.1. SQL Injection Prevention
We use **SQLAlchemy 2.0 ORM**. Raw queries are banned. All database interaction uses parameterized object-relational mapping, ensuring client parameters are automatically escaped by the driver (e.g., `asyncpg` bindings), rendering SQL injection attacks mathematically impossible.

### 2.2. Cross-Site Scripting (XSS) Mitigation
- **Escape-by-Default**: React 19 automatically escapes variables rendered in JSX.
- **Content Security Policy (CSP)**: We configure Next.js layout headers to enforce strict source loading rules:
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; img-src 'self' data: r2.nomen.ai; font-src 'self' fonts.gstatic.com;
  ```

### 2.3. Cross-Site Request Forgery (CSRF) Mitigation
As specified in the Authentication Design, all JWT access and refresh tokens are encapsulated in **SameSite=Strict** cookies. This prevents standard CSRF vectors as browsers refuse to attach these cookies to requests triggered from external origins.

---

## 3. Strict CORS Settings
We restrict cross-origin requests at the FastAPI layer using the `CORSMiddleware`. We explicitly whitelist the primary frontend client domain, blocking development localhost paths in production:

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nomen.ai"],  # Whitelist only our frontend domain
    allow_credentials=True,             # Allow cookies to be sent
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 4. API Rate Limiting (Redis-backed Token Bucket)

To prevent denial of service (DDoS) and AI API token exhaustion, we implement rate limiting at the FastAPI entry points using `fastapi-limiter` backed by **Redis**:

- **Search Generation (`POST /api/v1/search/generate`)**:
  - Unauthenticated (IP-based key): 3 requests / 24 hours.
  - Free Authenticated (User ID-based key): 10 requests / 24 hours.
  - Pro Authenticated: 100 requests / hour.
- **Login / Auth Endpoints (`POST /api/v1/auth/login`)**:
  - Enforces a limit of 5 login attempts / IP / 5 minutes to mitigate brute-force password cracking.

---

## 5. Passwords Hashing & Secret Management

- **Argon2id**: User passwords are encrypted before storage using `Argon2id` (via `cryptography` or `passlib`). It is highly resistant to GPU/ASIC brute-forcing.
- **Secret Isolation**: Production database credentials, JWT secret keys, and LLM API keys are **never** stored in the code repository. They are injected as environment variables at the container level by Docker Compose or orchestration configurations using secure Docker secrets.
