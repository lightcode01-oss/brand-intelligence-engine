from app.services.validation.trademark.base import AbstractTrademarkProvider, TrademarkCheckResult
from app.services.validation.trademark.mock import MockTrademarkProvider

class EuipoTrademarkProvider(MockTrademarkProvider):
    """Adapter class wrapping EUIPO API endpoints."""
    pass
