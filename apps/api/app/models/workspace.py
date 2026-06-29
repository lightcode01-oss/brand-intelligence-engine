import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import StandardBase

class Workspace(StandardBase):
    __tablename__ = "workspaces"
    
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)

class WorkspaceMember(StandardBase):
    __tablename__ = "workspace_members"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="RESTRICT"), 
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), 
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)

class Project(StandardBase):
    __tablename__ = "projects"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="RESTRICT"), 
        nullable=False
    )
    prompt: Mapped[str] = mapped_column(String(500), nullable=False)
    target_syllables: Mapped[Optional[int]] = mapped_column(nullable=True)
    selected_tlds: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
