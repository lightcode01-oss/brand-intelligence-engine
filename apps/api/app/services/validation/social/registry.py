from app.services.validation.social.base import AbstractSocialProvider, AbstractSocialProviderRegistry
from app.services.validation.social.mock import MockSocialProvider
from app.services.validation.social.github import GitHubSocialProvider
from app.services.validation.social.x import XSocialProvider
from app.services.validation.social.linkedin import LinkedInSocialProvider
from app.services.validation.social.instagram import InstagramSocialProvider
from app.services.validation.social.youtube import YouTubeSocialProvider

class SocialProviderRegistry(AbstractSocialProviderRegistry):
    """Discovers and routes handles checks to platform-specific adapters."""
    
    def __init__(self):
        self._providers = {
            "github": GitHubSocialProvider(),
            "x": XSocialProvider(),
            "linkedin": LinkedInSocialProvider(),
            "instagram": InstagramSocialProvider(),
            "youtube": YouTubeSocialProvider()
        }
        self.mock_fallback = MockSocialProvider("fallback")
        
    def get_provider(self, platform: str) -> AbstractSocialProvider:
        """Retrieves active provider matching target platform name."""
        return self._providers.get(platform.lower(), self.mock_fallback)
