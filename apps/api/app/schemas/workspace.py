import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from app.schemas.validators import WorkspaceSlug

# Workspace Schema Mappings
class WorkspaceCreate(BaseModel):
    slug: WorkspaceSlug = Field(..., description="Unique URL slug name (max 80 chars).")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display title for the workspace.")

class WorkspaceUpdate(BaseModel):
    slug: Optional[WorkspaceSlug] = Field(None)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)

class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    slug: WorkspaceSlug
    display_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# WorkspaceMember Schema Mappings
class WorkspaceMemberCreate(BaseModel):
    user_id: uuid.UUID
    role: str = Field("member", description="Role values ('owner', 'member', 'viewer').")

class WorkspaceMemberResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# Project Schema Mappings
class ProjectCreate(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500, description="Natural language search prompt.")
    target_syllables: Optional[int] = Field(None, ge=1, description="Optional target syllable count constraint.")
    selected_tlds: list[str] = Field(..., description="List of target domains extensions checked.")

class ProjectUpdate(BaseModel):
    prompt: Optional[str] = Field(None, min_length=10, max_length=500)
    target_syllables: Optional[int] = Field(None, ge=1)
    selected_tlds: Optional[list[str]] = Field(None)

class ProjectResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    prompt: str
    target_syllables: Optional[int]
    selected_tlds: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
