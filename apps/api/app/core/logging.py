import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """Custom logging formatter that outputs logs as structured JSON lines."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": settings.ENV,
        }
        
        # Inject standard contextual parameters if defined
        for key in ["request_id", "correlation_id", "user_id", "workspace_id", "latency", "response_status", "endpoint"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
                
        # Include exception trace info if exists
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging() -> None:
    """Configures system-wide log handlers to output JSON to stdout."""
    root_logger = logging.getLogger()
    
    # Clean up existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO if not settings.is_testing else logging.WARNING)

# Get application logger
logger = logging.getLogger("nomen")
