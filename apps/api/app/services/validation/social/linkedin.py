from app.services.validation.social.mock import MockSocialProvider

class LinkedInSocialProvider(MockSocialProvider):
    """Adapter class wrapping LinkedIn profiles endpoints."""
    def __init__(self):
        super().__init__("linkedin")
