import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class WorkspaceIntegrationCreate(BaseModel):
    provider_slug: str
    settings_json: Dict[str, Any]
    is_active: bool = True

class WorkspaceIntegrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    workspace_id: uuid.UUID
    provider_slug: str
    settings_json: Dict[str, Any]
    is_active: bool
    
class WorkspaceWebhookCreate(BaseModel):
    url: str
    secret_key: str
    events_json: List[str]
    is_active: bool = True

class WorkspaceWebhookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    workspace_id: uuid.UUID
    url: str
    secret_key: str
    events_json: List[str]
    is_active: bool
