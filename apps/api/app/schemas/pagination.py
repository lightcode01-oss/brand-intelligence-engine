from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel, Field
from app.schemas.validators import PageInt, PageSizeInt

T = TypeVar("T")

class PaginationParams(BaseModel):
    """Query parameters to control API page requests."""
    page: PageInt = Field(1, description="Target page index (1-based).")
    page_size: PageSizeInt = Field(20, description="Number of items returned per page (max 100).")

class PaginationMeta(BaseModel):
    """Pagination details included in the meta section of paginated responses."""
    page: int = Field(..., description="Current page index.")
    page_size: int = Field(..., description="Target page size limit.")
    total: int = Field(..., description="Total count of active database records matching filters.")
    total_pages: int = Field(..., description="Total pages count calculated from size.")
    has_next: bool = Field(..., description="True if a next page exists.")
    has_previous: bool = Field(..., description="True if a previous page exists.")

class PaginatedListResponse(BaseModel, Generic[T]):
    """Generic payload containing paginated lists and pagination metadata."""
    items: Sequence[T] = Field(..., description="List of items returned for the current page.")
    pagination: PaginationMeta = Field(..., description="Pagination metadata parameters.")
