import uuid
from typing import Optional, Sequence, Any, TypeVar
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import AbstractRepository
from app.repositories.user import AbstractUserRepository, AbstractSubscriptionRepository, AbstractFeatureFlagRepository, AbstractAuditLogRepository
from app.models.user import User, Subscription, FeatureFlag, AuditLog, Session, VerificationToken, PasswordResetToken, Role, Permission

T = TypeVar("T")

class SqlAlchemyRepository(AbstractRepository[T]):
    """Common implementation base executing standard SQLAlchemy queries."""
    
    def __init__(self, db: AsyncSession, model_class: type):
        self.db = db
        self.model_class = model_class
        
    async def create(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.flush()
        return entity
        
    async def update(self, entity: T) -> T:
        await self.db.flush()
        return entity
        
    async def delete(self, entity_id: uuid.UUID) -> bool:
        entity = await self.get(entity_id)
        if entity:
            if hasattr(entity, "soft_delete"):
                entity.soft_delete()
            else:
                await self.db.delete(entity)
            await self.db.flush()
            return True
        return False
        
    async def get(self, entity_id: uuid.UUID) -> Optional[T]:
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at == None)
        return (await self.db.execute(stmt)).scalar()
        
    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = select(self.model_class).offset(skip).limit(limit)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at == None)
        return (await self.db.execute(stmt)).scalars().all()
        
    async def exists(self, entity_id: uuid.UUID) -> bool:
        stmt = select(func.count(self.model_class.id)).where(self.model_class.id == entity_id)
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at == None)
        count = (await self.db.execute(stmt)).scalar() or 0
        return count > 0
        
    async def count(self) -> int:
        stmt = select(func.count(self.model_class.id))
        if hasattr(self.model_class, "deleted_at"):
            stmt = stmt.where(self.model_class.deleted_at == None)
        return (await self.db.execute(stmt)).scalar() or 0
        
    async def search(self, query: str) -> Sequence[T]:
        # Simple placeholder fallback
        return await self.list()

# Concrete Repositories
class SqlAlchemyUserRepository(SqlAlchemyRepository, AbstractUserRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
        
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.strip().lower(), User.deleted_at == None)
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemySubscriptionRepository(SqlAlchemyRepository, AbstractSubscriptionRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Subscription)
        
    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id, Subscription.deleted_at == None)
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemyFeatureFlagRepository(SqlAlchemyRepository, AbstractFeatureFlagRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, FeatureFlag)
        
    async def get_by_name(self, name: str) -> Optional[FeatureFlag]:
        stmt = select(FeatureFlag).where(FeatureFlag.name == name, FeatureFlag.deleted_at == None)
        return (await self.db.execute(stmt)).scalar()
        
    async def list_active_flags(self) -> Sequence[FeatureFlag]:
        stmt = select(FeatureFlag).where(FeatureFlag.is_enabled == True, FeatureFlag.deleted_at == None)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemyAuditLogRepository(SqlAlchemyRepository, AbstractAuditLogRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditLog)
        
    async def list_by_actor(self, actor: str) -> Sequence[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.actor == actor).order_by(AuditLog.created_at.desc())
        return (await self.db.execute(stmt)).scalars().all()
        
    async def list_by_workspace(self, workspace_id: uuid.UUID) -> Sequence[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.workspace_id == workspace_id).order_by(AuditLog.created_at.desc())
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemySessionRepository(SqlAlchemyRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Session)
        
    async def get_active_sessions(self, user_id: uuid.UUID) -> Sequence[Session]:
        stmt = select(Session).where(Session.user_id == user_id, Session.revoked == False, Session.deleted_at == None)
        return (await self.db.execute(stmt)).scalars().all()

class SqlAlchemyVerificationTokenRepository(SqlAlchemyRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, VerificationToken)
        
    async def get_by_token_hash(self, token_hash: str) -> Optional[VerificationToken]:
        stmt = select(VerificationToken).where(VerificationToken.token_hash == token_hash, VerificationToken.used_at == None)
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemyPasswordResetTokenRepository(SqlAlchemyRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, PasswordResetToken)
        
    async def get_by_token_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        stmt = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash, PasswordResetToken.used_at == None)
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemyRoleRepository(SqlAlchemyRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)
        
    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        return (await self.db.execute(stmt)).scalar()

class SqlAlchemyPermissionRepository(SqlAlchemyRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Permission)
        
    async def get_by_name(self, name: str) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.name == name)
        return (await self.db.execute(stmt)).scalar()
from typing import Any
