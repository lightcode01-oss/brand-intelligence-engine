class NomenException(Exception):
    """Base system exception for all custom Nomen errors."""
    
    def __init__(self, message: str, status_code: int = 400, errors: list[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or []

class DomainException(NomenException):
    """Exception raised on domain invariant violations (e.g. project constraints)."""
    def __init__(self, message: str, errors: list[str] = None):
        super().__init__(message, status_code=422, errors=errors)

class AuthenticationError(NomenException):
    """Exception raised on invalid authentication tokens or credentials."""
    def __init__(self, message: str = "Invalid credentials or authorization token."):
        super().__init__(message, status_code=401)

class AuthorizationError(NomenException):
    """Exception raised when access to a resource is forbidden."""
    def __init__(self, message: str = "Permission denied for this resource."):
        super().__init__(message, status_code=403)

class RateLimitError(NomenException):
    """Exception raised when a user exceeds their query limits."""
    def __init__(self, message: str = "Query quota exceeded. Please wait or upgrade your plan."):
        super().__init__(message, status_code=429)

class UnexpectedException(NomenException):
    """Exception raised on unhandled systems runtime exceptions."""
    def __init__(self, message: str = "An unexpected error occurred. Please try again."):
        super().__init__(message, status_code=500)
