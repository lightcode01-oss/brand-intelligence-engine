import re
from typing import Any
from pydantic import AfterValidator
from typing_extensions import Annotated

# Regex specifications
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_REGEX = re.compile(r"^[a-zA-Z0-9\-']+$")

def validate_email(value: str) -> str:
    v = value.strip().lower()
    if not EMAIL_REGEX.match(v):
        raise ValueError("Invalid email address format.")
    return v

def validate_slug(value: str) -> str:
    v = value.strip().lower()
    if not SLUG_REGEX.match(v):
        raise ValueError("Slug must be lowercase alphanumeric characters separated by single dashes.")
    if len(v) > 80:
        raise ValueError("Slug cannot exceed 80 characters.")
    return v

def validate_name_string(value: str) -> str:
    v = value.strip()
    if len(v) < 2 or len(v) > 18:
        raise ValueError("Name string must be between 2 and 18 characters.")
    if not NAME_REGEX.match(v):
        raise ValueError("Name string contains invalid characters.")
    return v

def validate_pagination_page(value: int) -> int:
    if value < 1:
        raise ValueError("Page index must be greater than or equal to 1.")
    return value

def validate_pagination_size(value: int) -> int:
    if value < 1 or value > 100:
        raise ValueError("Page size must be between 1 and 100.")
    return value

# Reusable Pydantic types annotations
EmailStr = Annotated[str, AfterValidator(validate_email)]
WorkspaceSlug = Annotated[str, AfterValidator(validate_slug)]
BrandNameStr = Annotated[str, AfterValidator(validate_name_string)]
PageInt = Annotated[int, AfterValidator(validate_pagination_page)]
PageSizeInt = Annotated[int, AfterValidator(validate_pagination_size)]
