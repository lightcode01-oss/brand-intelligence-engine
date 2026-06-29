import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Comment body markdown content.")
    parent_id: Optional[uuid.UUID] = Field(None, description="Optional parent comment ID for replies.")

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, description="Edited comment body markdown content.")

class UserProfileShort(BaseModel):
    id: uuid.UUID
    email: str
    role: str

    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    is_edited: bool
    is_pinned: bool
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    author: Optional[UserProfileShort] = None

    class Config:
        from_attributes = True

class CommentThreadResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    project_id: uuid.UUID
    name_id: uuid.UUID
    is_resolved: bool
    resolved_by: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FavoriteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    workspace_id: uuid.UUID
    name_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Collection name.")
    description: Optional[str] = Field(None, max_length=255, description="Collection folder description.")

class CollectionResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: Optional[str]
    created_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CollectionItemResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    name_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
