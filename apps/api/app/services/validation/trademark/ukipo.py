from app.services.validation.trademark.base import AbstractTrademarkProvider, TrademarkCheckResult
from app.services.validation.trademark.mock import MockTrademarkProvider

class UkipoTrademarkProvider(MockTrademarkProvider):
    """Adapter class wrapping UK-IPO API endpoints."""
    pass
