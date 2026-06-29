import re

SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def slugify(text: str) -> str:
    """Converts a raw string into a URL-friendly slug.
    
    Examples:
        "My Workspace!" -> "my-workspace"
        "---hello---world---" -> "hello-world"
    """
    # Lowercase
    s = text.lower().strip()
    # Replace non-alphanumeric characters with dashes
    s = re.sub(r"[^a-z0-9\-]", "-", s)
    # Compress multiple dashes into a single dash
    s = re.sub(r"-+", "-", s)
    # Remove leading and trailing dashes
    return s.strip("-")

def is_valid_slug(slug: str, max_length: int = 80) -> bool:
    """Validates that a slug matches standard URL guidelines and length limits."""
    if not slug or len(slug) > max_length:
        return False
    return bool(SLUG_REGEX.match(slug))
