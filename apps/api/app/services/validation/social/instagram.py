from app.services.validation.social.mock import MockSocialProvider

class InstagramSocialProvider(MockSocialProvider):
    """Adapter class wrapping Instagram accounts endpoints."""
    def __init__(self):
        super().__init__("instagram")
