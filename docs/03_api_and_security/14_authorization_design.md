# Authorization Design: Nomen

This document details the Role-Based Access Control (RBAC) schemas, permission definitions, and route-guard middleware setups of Nomen.

---

## 1. Role Definitions & Permissions Matrix

Nomen supports four user roles, which are verified on every API request:

| Feature / Resource | Guest (Anon) | Free User | Pro User | Admin |
| :--- | :--- | :--- | :--- | :--- |
| **Search Queries** | Limit: 3 / day | Limit: 10 / day | Unlimited | Unlimited |
| **Trademark Summaries**| Basic match count | Basic match count | Full Record details | Full Record details |
| **Save Portfolios** | None (Disabled) | Max 2 folders | Unlimited | Unlimited |
| **Asset Bundle Export** | Client-side only (Low-res) | Custom styles preview | Full Vector ZIP packages | Full Vector ZIP packages |
| **Access Admin Console**| Denied | Denied | Denied | Approved |

---

## 2. FastAPI Middleware & Dependency Enforcement

In FastAPI, authorization is enforced at the router path level using **Dependencies** (`Depends`). This patterns checks the validated user object returned by the authentication dependency.

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import User

def require_role(allowed_roles: list[str]):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return dependency
```

### 2.1. Usage Example: Premium Export Endpoint
```python
# app/api/v1/export.py
from fastapi import APIRouter, Depends
from app.api.deps import require_role
from app.models.user import User

router = APIRouter()

@router.post("/bundle")
async def export_brand_bundle(
    payload: ExportPayload,
    current_user: User = Depends(require_role(["pro_user", "admin"]))
):
    # Only Pro Users or Admins can hit this path
    task = queue_zip_generation(payload, current_user.id)
    return {"task_id": task.id}
```

---

## 3. Next.js Routing guards (Frontend Middleware)

To prevent guests from seeing blank dashboards or dashboard layouts shifting on mount, a global Next.js `middleware.ts` guards route paths on the Edge:

```typescript
// frontend/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/request';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const { pathname } = request.nextUrl;

  // Protect /dashboard routes
  if (pathname.startsWith('/dashboard')) {
    if (!token) {
      // Redirect to login page, saving the target path in query params
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('callbackUrl', pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```
This edge-level verification runs within milliseconds inside Cloudflare workers, ensuring unauthenticated clients are redirected instantly before any dashboard scripts load.
