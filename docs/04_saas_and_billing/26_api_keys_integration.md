# Developer API Keys Guide: Nomen

This guide details how developers configure Nomen's API keys, authenticate requests, and authorize custom scopes.

---

## 1. Key Format & Hashing Security

- **Format**: API keys are generated using cryptographically secure random bytes with a standard prefix: `nm_live_[32-byte-hex]`.
- **Database Safety**: Raw keys are shown to developers only once upon creation. Nomen only stores a **SHA-256 hash** of the key in the database:
  
  $$\text{hashed\_key} = \text{SHA-256}(\text{raw\_key})$$

---

## 2. API Key Request Authorization Flow

Developers authenticate requests by passing the raw key in the HTTP `Authorization` header:

```http
Authorization: Bearer nm_live_8e945c711209bcae710adcf112a1ef82
```

The application's `require_api_key` dependency interceptor:
1. Extracts the raw token and hashes it.
2. Performs a lookup in the `api_keys` table.
3. Checks if the key has been revoked (`revoked_at != None`) or has expired (`expires_at < now`).
4. Verifies that the assigned key scopes match the requested scopes.
5. Populates `request.state.user_id` to establish the authenticated user context.

---

## 3. Key Rotation & Revocation

- **Rotation**: To rotate a key, developers generate a new key and delete the old key entry.
- **Revocation**: Admins or developers can immediately revoke a key by setting `revoked_at = now`. Revoked keys fail authentication immediately.
