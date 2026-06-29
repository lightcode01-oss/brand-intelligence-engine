import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.compiler import compiles

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"

class Base(DeclarativeBase):
    """ Declarative Base for database mapping."""
    pass

class StandardBase(Base):
    """Abstract model mapping UUID keys, soft deletes, and optimistic locking version identifiers."""
    __abstract__ = True
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        default=None
    )
    
    # Optimistic locking integer
    version_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    __mapper_args__ = {
        "version_id_col": version_id
    }
    
    def soft_delete(self) -> None:
        """Helper to mark deleted status inside transaction blocks."""
        self.deleted_at = datetime.now(timezone.utc)

class ImmutableBase(Base):
    """Abstract model mapping append-only static logs and cache tables."""
    __abstract__ = True
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
