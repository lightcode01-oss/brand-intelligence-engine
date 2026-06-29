from app.services.validation.trademark.base import AbstractTrademarkProvider, TrademarkCheckResult
from app.services.validation.trademark.mock import MockTrademarkProvider

class UsptoTrademarkProvider(MockTrademarkProvider):
    """Adapter class wrapping USPTO TSDR API endpoints."""
    pass
