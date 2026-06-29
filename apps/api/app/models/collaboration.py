import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, StandardBase, ImmutableBase

class CommentThread(StandardBase):
    """Groups comment threads per candidate name inside a project."""
    __tablename__ = "comment_threads"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False)
    name_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generated_names.id", ondelete="RESTRICT"), nullable=False)
    
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="thread",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Comment.created_at"
    )

class Comment(StandardBase):
    """Individual comments and replies inside a comment thread."""
    __tablename__ = "comments"
    
    thread_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("comment_threads.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    thread: Mapped[CommentThread] = relationship("CommentThread", back_populates="comments")
    author: Mapped["User"] = relationship("User", lazy="selectin")
    replies: Mapped[List["Comment"]] = relationship("Comment", cascade="all, delete-orphan")

class Favorite(StandardBase):
    """Workspace-level user starred name candidates."""
    __tablename__ = "favorites"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    name_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generated_names.id", ondelete="RESTRICT"), nullable=False)
    
    name_ref: Mapped["GeneratedName"] = relationship("GeneratedName", lazy="selectin")

class Collection(StandardBase):
    """Named workspaces folders storing groups of candidates."""
    __tablename__ = "collections"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    items: Mapped[List["CollectionItem"]] = relationship(
        "CollectionItem",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class CollectionItem(StandardBase):
    """Mapping table linking candidates to collections."""
    __tablename__ = "collection_items"
    
    collection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    name_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generated_names.id", ondelete="RESTRICT"), nullable=False)
    
    collection: Mapped[Collection] = relationship("Collection", back_populates="items")
    name_ref: Mapped["GeneratedName"] = relationship("GeneratedName", lazy="selectin")

class ActivityEvent(ImmutableBase):
    """Workspace events logs feed."""
    __tablename__ = "activity_events"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "project_created"
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    user: Mapped["User"] = relationship("User", lazy="selectin")

class Mention(ImmutableBase):
    """Mentions maps linking comments to target users."""
    __tablename__ = "mentions"
    
    comment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

class SearchHistory(ImmutableBase):
    """Saves recent user searches queries per workspace context."""
    __tablename__ = "search_histories"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False)
    query: Mapped[str] = mapped_column(String(255), nullable=False)
