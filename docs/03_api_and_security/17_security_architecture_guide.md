# Security Architecture & RBAC Guide: Nomen

This document details Nomen's Authentication architecture, Workspace Role-Based Access Control (RBAC) rules, JWT rotation, session management, and threat model.

---

## 1. Authentication Lifecycle & JWT Flow

Nomen implements a stateless, token-based authentication mechanism leveraging access tokens for short-lived requests, coupled with rotated refresh tokens to manage continuous sessions.

```text
 Client (Browser)                        API Gateway (FastAPI)              PostgreSQL DB
        │                                        │                                │
        ├───────── POST /auth/login ────────────>│                                │
        │          (Email/Password)              ├───── Verify Credentials ──────>│
        │                                        │                                │
        │                                        ├───── Create Session Log ──────>│
        │                                        │                                │
        │<── Set-Cookie: access_token (15m) ─────┤                                │
        │    Set-Cookie: refresh_token (7d)      │                                │
        │                                        │                                │
        │                                        │                                │
  [Token Expiration (15m)]                       │                                │
        │                                        │                                │
        ├───────── POST /auth/refresh ──────────>│                                │
        │          (Cookies payload)             ├───── Verify Session Active ───>│
        │                                        │                                │
        │                                        ├───── Rotate Tokens in DB ─────>│
        │                                        │                                │
        │<── Set-Cookie: rotated tokens ─────────┤                                │
```

### Cookie Configuration Security
To protect tokens from Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) exploits:
- **HttpOnly**: Strict. Prevents JavaScript scripts from accessing cookie files.
- **Secure**: Strict. Restricts transmission to HTTPS channels only.
- **SameSite**: `Lax`. Restricts cookie routing on third-party links, blocking cross-origin CSRF queries.

---

## 2. Workspace RBAC Permission Matrix

Workspace actions are governed by membership role scopes.

| Permission Name | SUPER_ADMIN | OWNER | MEMBER | VIEWER | Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `workspace.read` | ✅ | ✅ | ✅ | ✅ | Access workspace details. |
| `workspace.write` | ✅ | ✅ | ❌ | ❌ | Modify workspace slug or name. |
| `workspace.delete` | ✅ | ✅ | ❌ | ❌ | Soft-delete a workspace. |
| `project.read` | ✅ | ✅ | ✅ | ✅ | List projects. |
| `project.write` | ✅ | ✅ | ✅ | ❌ | Create or edit project settings. |
| `project.delete` | ✅ | ✅ | ❌ | ❌ | Delete search projects. |
| `generation.create` | ✅ | ✅ | ✅ | ❌ | Start AI generation jobs. |
| `billing.manage` | ✅ | ✅ | ❌ | ❌ | Upgrade billing subscriptions. |
| `user.manage` | ✅ | ❌ | ❌ | ❌ | Administer global user accounts. |

---

## 3. Account Lockout & Brute-Force Throttling

To mitigate password guessing and brute-force attacks:
- **Threshold**: 5 consecutive failed login attempts.
- **Action**: Lock account for **15 minutes**.
- **Implementation**: Tracks `failed_login_count` and `locked_until` (TIMESTAMPTZ) in the `User` record. Successful logins instantly reset the counter to zero.

---

## 4. Threat Model & Security Checklist

### 4.1. Threat Matrix
- **Credential Stuffing**: Mitigated by Argon2id high-performance password hashes and brute-force lockouts.
- **Session Hijacking**: Mitigated by JTI tracking, user IP correlation logging, and fast session revocation.
- **CSRF**: Blocked by Lax SameSite cookie flags and custom header validation.

### 4.2. Security Checklist
- [ ] Are all API controllers bound to the `get_current_active_user` dependency?
- [ ] Do all auth cookies include the `HttpOnly` and `Secure` parameters?
- [ ] Are all database operations wrapped in standard SQLAlchemy transaction blocks to prevent session leaks?
