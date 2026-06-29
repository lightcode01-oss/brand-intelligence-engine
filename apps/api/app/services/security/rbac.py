"""RBAC service: workspace role and permission management."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.workspace import WorkspaceMember

# Role hierarchy: higher index = more permissions
_ROLE_HIERARCHY = ["VIEWER", "COMMENTER", "MEMBER", "ADMIN", "OWNER"]

# Permission matrix per workspace role
_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "VIEWER": [
        "projects.read",
        "generations.read",
        "workspace.read",
    ],
    "COMMENTER": [
        "projects.read",
        "generations.read",
        "workspace.read",
        "comments.create",
        "comments.read",
    ],
    "MEMBER": [
        "projects.read",
        "projects.create",
        "generations.read",
        "generations.create",
        "workspace.read",
        "comments.create",
        "comments.read",
        "collections.manage",
        "favorites.manage",
        "exports.create",
    ],
    "ADMIN": [
        "projects.read",
        "projects.create",
        "projects.update",
        "projects.delete",
        "generations.read",
        "generations.create",
        "workspace.read",
        "workspace.update",
        "workspace.invite",
        "workspace.remove_member",
        "comments.create",
        "comments.read",
        "comments.delete",
        "collections.manage",
        "favorites.manage",
        "exports.create",
        "analytics.read",
        "security.read",
        "billing.read",
        "roles.assign",
    ],
    "OWNER": [
        "projects.read",
        "projects.create",
        "projects.update",
        "projects.delete",
        "generations.read",
        "generations.create",
        "workspace.read",
        "workspace.update",
        "workspace.delete",
        "workspace.invite",
        "workspace.remove_member",
        "comments.create",
        "comments.read",
        "comments.delete",
        "collections.manage",
        "favorites.manage",
        "exports.create",
        "analytics.read",
        "analytics.export",
        "security.read",
        "security.configure",
        "billing.read",
        "billing.manage",
        "roles.assign",
        "sso.configure",
        "gdpr.manage",
    ],
}


class RBACService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_workspace_role(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> Optional[str]:
        """Retrieve the workspace role for a user."""
        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        return member.role if member else None

    async def has_permission(self, workspace_id: uuid.UUID, user_id: uuid.UUID, permission: str) -> bool:
        """Check whether a user holds a specific permission in the workspace."""
        role = await self.get_workspace_role(workspace_id, user_id)
        if not role:
            return False
        allowed = _ROLE_PERMISSIONS.get(role, [])
        return permission in allowed

    async def assign_role(
        self,
        workspace_id: uuid.UUID,
        target_user_id: uuid.UUID,
        new_role: str,
        assigning_user_id: uuid.UUID,
    ) -> dict:
        """Assign a new workspace role. Assigning user must be OWNER or ADMIN with roles.assign permission."""
        can_assign = await self.has_permission(workspace_id, assigning_user_id, "roles.assign")
        if not can_assign:
            return {"success": False, "error": "Insufficient permissions to assign roles."}

        if new_role not in _ROLE_HIERARCHY:
            return {"success": False, "error": f"Unknown role: {new_role}"}

        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == target_user_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return {"success": False, "error": "Target user is not a member of this workspace."}

        old_role = member.role
        member.role = new_role
        await self.db.flush()
        return {"success": True, "old_role": old_role, "new_role": new_role}

    async def list_members_with_roles(self, workspace_id: uuid.UUID) -> list[dict]:
        """List all workspace members with their roles and permissions summary."""
        result = await self.db.execute(
            select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
        )
        members = result.scalars().all()
        return [
            {
                "user_id": str(m.user_id),
                "role": m.role,
                "permissions": _ROLE_PERMISSIONS.get(m.role, []),
                "joined_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in members
        ]

    def get_role_permissions(self, role: str) -> list[str]:
        """Return the list of permissions for a given role."""
        return _ROLE_PERMISSIONS.get(role, [])

    def get_all_roles(self) -> list[dict]:
        """Return all available roles with their permission sets."""
        return [
            {"role": role, "permissions": perms}
            for role, perms in _ROLE_PERMISSIONS.items()
        ]
