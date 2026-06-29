import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Role, WorkspaceRole, Permission
from app.models.workspace import WorkspaceMember

class PermissionService:
    """RBAC validation logic for workspace roles and user-level authorizations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def check_global_permission(self, user_id: uuid.UUID, permission_name: str) -> bool:
        """Verifies if a user holds a global permission via active system roles."""
        stmt = select(User).where(User.id == user_id, User.deleted_at == None)
        user = (await self.db.execute(stmt)).scalar()
        if not user:
            return False
            
        # SUPER_ADMIN bypass check
        if user.role == "SUPER_ADMIN":
            return True
            
        # Check permissions in user's assigned roles
        for role in user.roles:
            for perm in role.permissions:
                if perm.name == permission_name:
                    return True
        return False
        
    async def check_workspace_permission(self, workspace_id: uuid.UUID, user_id: uuid.UUID, permission_name: str) -> bool:
        """Verifies if a user carries a workspace permission via memberships."""
        # 1. Bypass check if user is a global SUPER_ADMIN
        stmt = select(User).where(User.id == user_id, User.deleted_at == None)
        user = (await self.db.execute(stmt)).scalar()
        if user and user.role == "SUPER_ADMIN":
            return True
            
        # 2. Check if user is a member of the workspace
        member_stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.deleted_at == None
        )
        membership = (await self.db.execute(member_stmt)).scalar()
        if not membership:
            return False
            
        # 3. Check workspace role-based permissions
        ws_role_stmt = select(WorkspaceRole).where(
            WorkspaceRole.workspace_id == workspace_id,
            WorkspaceRole.user_id == user_id,
            WorkspaceRole.deleted_at == None
        )
        ws_role_assignment = (await self.db.execute(ws_role_stmt)).scalar()
        if not ws_role_assignment:
            # If no custom workspace role matches, default permissions based on member role string
            role_mapping = {
                "owner": ["workspace.read", "workspace.write", "workspace.delete", "project.read", "project.write", "project.delete", "generation.create", "billing.manage"],
                "member": ["workspace.read", "project.read", "project.write", "generation.create"],
                "viewer": ["workspace.read", "project.read"]
            }
            user_perms = role_mapping.get(membership.role, [])
            return permission_name in user_perms
            
        # Check explicit role-based permissions loaded from DB
        for perm in ws_role_assignment.role.permissions:
            if perm.name == permission_name:
                return True
                
        return False
