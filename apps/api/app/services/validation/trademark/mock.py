import datetime
from app.services.validation.trademark.base import AbstractTrademarkProvider, TrademarkCheckResult

class MockTrademarkProvider(AbstractTrademarkProvider):
    """Fallback mock trademark clearance lookup adapter."""
    
    def health(self) -> bool:
        return True
        
    async def check(self, name_string: str, jurisdiction: str) -> TrademarkCheckResult:
        normalized = self.normalize(name_string)
        # Mock status logic
        status = "CLEAR"
        serial = None
        if len(normalized) % 4 == 0:
            status = "CONFLICT"
            serial = "88990011"
        elif len(normalized) % 3 == 0:
            status = "WARNING"
            serial = "77665544"
            
        payload = {
            "status": status,
            "serial_number": serial,
            "mark": normalized.upper(),
            "filing_date": datetime.date.today().isoformat() if serial else None,
            "registration_date": None,
            "class": "009"
        }
        return self.parse(payload)
        
    def normalize(self, name: str) -> str:
        return name.strip().upper()
        
    def parse(self, raw_payload: dict) -> TrademarkCheckResult:
        return TrademarkCheckResult(
            risk_status=raw_payload["status"],
            serial_number=raw_payload.get("serial_number"),
            mark_text=raw_payload["mark"],
            filing_date=raw_payload.get("filing_date"),
            registration_date=raw_payload.get("registration_date"),
            class_code=raw_payload.get("class"),
            raw_payload=raw_payload
        )
