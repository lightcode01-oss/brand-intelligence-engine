from app.services.validation.domain.base import AbstractDomainProvider, DomainCheckResult

class MockDomainProvider(AbstractDomainProvider):
    """Fallback mock domain checker simulating registrar check responses."""
    
    def health(self) -> bool:
        return True
        
    async def check(self, domain_name: str, tld: str) -> DomainCheckResult:
        normalized = self.normalize(domain_name)
        # Determinisitc check: even length is available
        available = len(normalized) % 2 == 0
        price = 12.99 if available else None
        
        payload = {
            "status": "success",
            "domain": f"{normalized}.{tld}",
            "availability": "AVAILABLE" if available else "REGISTERED",
            "price": price
        }
        return self.parse(payload)
        
    def normalize(self, name: str) -> str:
        return name.strip().lower().replace(" ", "")
        
    def parse(self, raw_payload: dict) -> DomainCheckResult:
        available = raw_payload["availability"] == "AVAILABLE"
        return DomainCheckResult(
            available=available,
            price=raw_payload.get("price"),
            raw_payload=raw_payload
        )
