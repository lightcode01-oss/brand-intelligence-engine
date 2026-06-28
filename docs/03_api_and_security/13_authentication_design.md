# Authentication Design: Nomen

This document details the authentication models, token schemas, session mechanisms, and third-party integrations (OAuth2) utilized by Nomen.

---

## 1. Authentication Strategy

Nomen uses a **stateless, token-based authentication system** leveraging JSON Web Tokens (JWT) for the backend APIs, coupled with cookie storage for the frontend.

```text
  Client (Next.js FE)                         Server (FastAPI BE)
        │                                             │
        │─── 1. Login Credentials (Email/Pass) ──────>│
        │                                             │ (Validate credentials)
        │<── 2. Set-Cookie: httpOnly, Secure ─────────│ (Issue JWT Access & Refresh)
        │                                             │
        │─── 3. Subsequent Request (Cookie Sent) ────>│
        │                                             │ (Validate JWT signature)
        │<── 4. Protected Resource JSON ──────────────│
```

---

## 2. JWT Configuration & Cookie Security

Tokens are divided into short-lived Access Tokens and long-lived Refresh Tokens.

### 2.1. Access Token Details
- **Expiration**: 15 minutes.
- **Algorithm**: HS256 (symmetric signature, private key stored in backend environments).
- **Payload Schema**:
  ```json
  {
    "sub": "e4b934b1-8b94-4d89-9a7c-12f5a6f87d41",
    "role": "free_user",
    "exp": 1782678300
  }
  ```

### 2.2. Refresh Token Details & Rotation (RTR)
- **Expiration**: 7 days.
- **Algorithm**: HS256.
- **Payload Schema**: Contains the user ID and a unique session token ID (`jti`) matching a hash stored in the database.
- **Rotation Policy**: Every time a client requests a new access token, a new refresh token is also issued, and the previous one is marked as revoked in Redis to protect against replay attacks.

### 2.3. Cookie Transmission Settings
Both tokens are set by the FastAPI backend using the standard `Set-Cookie` header. This prevents cross-site scripting (XSS) access:
```http
Set-Cookie: access_token=jwt_string; Path=/; Max-Age=900; HttpOnly; Secure; SameSite=Strict
Set-Cookie: refresh_token=jwt_string; Path=/api/v1/auth/refresh; Max-Age=604800; HttpOnly; Secure; SameSite=Strict
```
- **HttpOnly**: Prevents JavaScript (e.g. `document.cookie`) from reading the token.
- **Secure**: Forces cookie transmission only over HTTPS connections.
- **SameSite=Strict**: Instructs the browser to only attach the cookie on requests originating from the site's primary domain, eliminating Cross-Site Request Forgery (CSRF).
- **Path**: The refresh token is only sent to the refresh endpoint `/api/v1/auth/refresh` to minimize transit surface.

---

## 3. Third-Party OAuth2 Integrations (Google & GitHub)

To support social logins:

1. **Frontend Flow**: Next.js uses **Auth.js** (NextAuth) to redirect the user to Google or GitHub's authentication portals.
2. **Callback Handling**: Auth.js retrieves the third-party OAuth profile, extracts user data (email, name), and makes a secure server-to-server request to the FastAPI backend at `POST /api/v1/auth/oauth-callback`.
3. **Backend Validation**: FastAPI verifies the signature of the provider token, creates the user record in PostgreSQL if it is a new user, issues Nomen's secure JWT cookies, and returns user session objects back to the Next.js middleware.
4. **Session Synchronization**: The user is logged in to both Next.js edge route handlers and the FastAPI microservices.
