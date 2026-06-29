import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from app.schemas.validators import BrandNameStr

# GeneratedName Schema Mappings
class GeneratedNameUpdate(BaseModel):
    lifecycle_state: str = Field(..., description="Target lifecycle state ('SUGGESTED', 'SAVED', 'DEPRECATED', 'ARCHIVED').")

class GeneratedNameResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name_string: BrandNameStr
    style: str
    lifecycle_state: str
    model_name: str
    temperature: float
    prompt_tokens: int
    completion_tokens: int
    generation_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# BrandScore Schema Mappings
class BrandScoreResponse(BaseModel):
    name_id: uuid.UUID
    bsi_overall: int
    length_score: float
    pronounceability_score: float
    domain_score: float
    trademark_score: float
    semantic_score: float

    class Config:
        from_attributes = True

# LogoSuggestion Schema Mappings
class LogoSuggestionResponse(BaseModel):
    name_id: uuid.UUID
    primary_hue: int
    secondary_hue: int
    heading_font: str
    body_font: str
    layout_style: str

    class Config:
        from_attributes = True

# Check Schemas Mappings
class DomainCheckResponse(BaseModel):
    id: uuid.UUID
    name_id: uuid.UUID
    domain_name: str
    tld: str
    available: bool
    price: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class TrademarkCheckResponse(BaseModel):
    id: uuid.UUID
    name_id: uuid.UUID
    jurisdiction: str
    risk_status: str
    serial_number: Optional[str]
    mark_text: str
    filing_date: Optional[datetime]
    registration_date: Optional[datetime]
    class_code: Optional[str]
    raw_payload: dict
    created_at: datetime

    class Config:
        from_attributes = True

class SocialHandleCheckResponse(BaseModel):
    id: uuid.UUID
    name_id: uuid.UUID
    platform: str
    available: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Export Schema Mappings
class ExportCreate(BaseModel):
    name_id: uuid.UUID

class ExportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name_id: uuid.UUID
    package_url: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# GenerationJob Schema Mappings
class GenerationJobCreate(BaseModel):
    model_name: str = Field("gemini-1.5-flash", description="AI model to target.")
    temperature: float = Field(0.7, description="Generation randomness index.")

class GenerationJobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    model_name: str
    engine_version: str
    prompt_version: str
    latency_ms: int
    token_usage: dict
    cost_estimate: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
