import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

class FilterParams(BaseModel):
    """Reusable query parameters for sorting, matching, and boundary filtering."""
    
    search: Optional[str] = Field(None, description="Fuzzy search text pattern.")
    sort_by: Optional[str] = Field(None, description="Column name target for sorting.")
    sort_order: Literal["asc", "desc"] = Field("desc", description="Sorting direction constraint.")
    
    created_before: Optional[datetime] = Field(None, description="Upper timestamp creation boundary.")
    created_after: Optional[datetime] = Field(None, description="Lower timestamp creation boundary.")
    updated_before: Optional[datetime] = Field(None, description="Upper timestamp update boundary.")
    updated_after: Optional[datetime] = Field(None, description="Lower timestamp update boundary.")
    
    status: Optional[str] = Field(None, description="Lifecycle or authentication state indicator.")
    workspace_id: Optional[uuid.UUID] = Field(None, description="Target workspace uuid context.")
