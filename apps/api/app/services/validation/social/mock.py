from app.services.validation.social.base import AbstractSocialProvider, SocialCheckResult

class MockSocialProvider(AbstractSocialProvider):
    """Fallback mock social username lookup adapter."""
    
    def __init__(self, platform: str = "mock"):
        self.platform = platform
        
    def get_platform_name(self) -> str:
        return self.platform
        
    def health(self) -> bool:
        return True
        
    async def check(self, handle: str) -> SocialCheckResult:
        normalized = self.normalize(handle)
        # Mock logic: handles with odd length are available
        available = len(normalized) % 2 != 0
        payload = {
            "status": "success",
            "handle": normalized,
            "platform": self.platform,
            "availability": "AVAILABLE" if available else "TAKEN"
        }
        return self.parse(payload)
        
    def normalize(self, name: str) -> str:
        return name.strip().lower().replace(" ", "")
        
    def parse(self, raw_payload: dict) -> SocialCheckResult:
        return SocialCheckResult(
            available=raw_payload["availability"] == "AVAILABLE",
            raw_payload=raw_payload
        )
