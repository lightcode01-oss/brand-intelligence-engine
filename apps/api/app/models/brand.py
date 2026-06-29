import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Enum, ForeignKey, Boolean, Integer, DateTime, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, StandardBase, ImmutableBase

# Postgres native Enum definitions
name_lifecycle_enum = Enum(
    "SUGGESTED", "SAVED", "DEPRECATED", "ARCHIVED", 
    name="name_lifecycle"
)
trademark_risk_enum = Enum(
    "CLEAR", "WARNING", "CONFLICT", 
    name="trademark_risk"
)
job_status_enum = Enum(
    "PENDING", "RUNNING", "SUCCESS", "FAILED",
    name="job_status"
)

class GeneratedName(StandardBase):
    __tablename__ = "generated_names"
    
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), 
        nullable=False
    )
    name_string: Mapped[str] = mapped_column(String(18), nullable=False)
    style: Mapped[str] = mapped_column(String(50), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(name_lifecycle_enum, default="SUGGESTED", nullable=False)
    
    # Generation Metadata & Versioning
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    generation_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

class BrandScore(Base):
    """BSI Metrics scorecard. Cascade replaced with RESTRICT."""
    __tablename__ = "brand_scores"
    
    name_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generated_names.id", ondelete="RESTRICT"), 
        primary_key=True
    )
    bsi_overall: Mapped[int] = mapped_column(Integer, nullable=False)
    length_score: Mapped[float] = mapped_column(Float, nullable=False)
    pronounceability_score: Mapped[float] = mapped_column(Float, nullable=False)
    domain_score: Mapped[float] = mapped_column(Float, nullable=False)
    trademark_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_score: Mapped[float] = mapped_column(Float, nullable=False)

class LogoSuggestion(Base):
    """Logo vector configuration. Cascade replaced with RESTRICT."""
    __tablename__ = "logo_suggestions"
    
    name_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generated_names.id", ondelete="RESTRICT"), 
        primary_key=True
    )
    primary_hue: Mapped[int] = mapped_column(Integer, nullable=False)
    secondary_hue: Mapped[int] = mapped_column(Integer, nullable=False)
    heading_font: Mapped[str] = mapped_column(String(50), nullable=False)
    body_font: Mapped[str] = mapped_column(String(50), nullable=False)
    layout_style: Mapped[str] = mapped_column(String(50), nullable=False)

class DomainCheck(ImmutableBase):
    __tablename__ = "domain_checks"
    
    name_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generated_names.id", ondelete="RESTRICT"), 
        nullable=False
    )
    domain_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tld: Mapped[str] = mapped_column(String(20), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

class TrademarkCheck(ImmutableBase):
    __tablename__ = "trademark_checks"
    
    name_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generated_names.id", ondelete="RESTRICT"), 
        nullable=False
    )
    jurisdiction: Mapped[str] = mapped_column(String(10), nullable=False) # 'US', 'UK', 'EU'
    risk_status: Mapped[str] = mapped_column(trademark_risk_enum, nullable=False)
    
    # Structured columns for quick indexing
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mark_text: Mapped[str] = mapped_column(String(255), nullable=False)
    filing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    registration_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    class_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Unstructured JSON payload
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

class SocialHandleCheck(ImmutableBase):
    __tablename__ = "social_handle_checks"
    
    name_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generated_names.id", ondelete="RESTRICT"), 
        nullable=False
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)

class Export(ImmutableBase):
    __tablename__ = "exports"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), 
        nullable=False
    )
    name_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generated_names.id", ondelete="RESTRICT"), 
        nullable=False
    )
    package_url: Mapped[str] = mapped_column(String(500), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class GenerationJob(StandardBase):
    """Records AI query metadata and token costs."""
    __tablename__ = "generation_jobs"
    
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(job_status_enum, default="PENDING", nullable=False)
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), default="Queued", nullable=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    token_usage: Mapped[dict] = mapped_column(JSONB, nullable=False) # e.g. {"prompt_tokens": 100, "completion_tokens": 50}
    cost_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
