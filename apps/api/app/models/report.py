import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import StandardBase

class SavedReport(StandardBase):
    """Stores generated brand intelligence, enterprise statistics, and custom audit reports."""
    __tablename__ = "saved_reports"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="RESTRICT"), 
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), 
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "analytics", "insights", "team", "audit"
    format: Mapped[str] = mapped_column(String(20), nullable=False) # "pdf", "markdown", "json", "csv"
    data_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
