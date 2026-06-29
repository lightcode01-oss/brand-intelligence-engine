from app.services.validation.trademark.base import AbstractTrademarkProvider, TrademarkCheckResult
from app.services.validation.trademark.mock import MockTrademarkProvider

class IndiaTrademarkProvider(MockTrademarkProvider):
    """Adapter class wrapping IPO India API endpoints."""
    pass
