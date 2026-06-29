import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.validators import EmailStr

# User Schema Mappings
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email address for the registration credentials.")
    password: str = Field(..., min_length=8, description="Plaintext password (minimum 8 characters).")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Optional new email address.")
    password: Optional[str] = Field(None, min_length=8, description="Optional new password.")
    role: Optional[str] = Field(None, description="Optional new role mapping.")
    status: Optional[str] = Field(None, description="Optional new status mapping.")

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Subscription Schema Mappings
class SubscriptionCreate(BaseModel):
    user_id: uuid.UUID
    tier: str = Field("FREE", description="Subscription tier level.")
    status: str = Field("ACTIVE", description="Payment status state.")
    limit_reset_at: datetime

class SubscriptionUpdate(BaseModel):
    tier: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    limit_reset_at: Optional[datetime] = Field(None)
    monthly_query_count: Optional[int] = Field(None)

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tier: str
    status: str
    limit_reset_at: datetime
    monthly_query_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# FeatureFlag Schema Mappings
class FeatureFlagCreate(BaseModel):
    name: str = Field(..., description="Unique slug name of the feature flag.")
    is_enabled: bool = Field(False, description="State of rollout toggle.")
    description: Optional[str] = Field(None, description="Optional description.")

class FeatureFlagResponse(BaseModel):
    id: uuid.UUID
    name: str
    is_enabled: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    category: Optional[str]
    title: str
    message: str
    data_json: Optional[dict]
    sender_id: Optional[uuid.UUID]
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
