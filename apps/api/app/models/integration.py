import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, StandardBase

class WorkspaceIntegration(StandardBase):
    """Configuration settings for third-party notification adapters (Slack, Discord, MS Teams, Zapier)."""
    __tablename__ = "workspace_integrations"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    provider_slug: Mapped[str] = mapped_column(String(50), nullable=False)  # slack, discord, teams, zapier, github, email
    settings_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class WorkspaceWebhook(StandardBase):
    """Custom outbound signed webhook subscriptions per workspace."""
    __tablename__ = "workspace_webhooks"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    events_json: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)  # ['generation.success', 'comment.created']
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
