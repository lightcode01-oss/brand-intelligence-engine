from app.services.validation.social.mock import MockSocialProvider

class GitHubSocialProvider(MockSocialProvider):
    """Adapter class wrapping GitHub accounts endpoints."""
    def __init__(self):
        super().__init__("github")
