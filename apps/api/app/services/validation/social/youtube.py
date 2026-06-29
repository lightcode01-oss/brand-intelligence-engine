from app.services.validation.social.mock import MockSocialProvider

class YouTubeSocialProvider(MockSocialProvider):
    """Adapter class wrapping YouTube channels endpoints."""
    def __init__(self):
        super().__init__("youtube")
