from app.services.validation.social.mock import MockSocialProvider

class XSocialProvider(MockSocialProvider):
    """Adapter class wrapping X platform endpoints."""
    def __init__(self):
        super().__init__("x")
