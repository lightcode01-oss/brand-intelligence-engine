import time
from typing import Optional

class CircuitBreaker:
    """In-memory Circuit Breaker to track and isolate failing AI provider adapters."""
    
    _instances: dict[str, 'CircuitBreaker'] = {}
    
    def __new__(cls, provider_name: str, threshold: int = 3, cooldown: float = 60.0):
        if provider_name not in cls._instances:
            instance = super().__new__(cls)
            instance._init_cb(provider_name, threshold, cooldown)
            cls._instances[provider_name] = instance
        return cls._instances[provider_name]
        
    def _init_cb(self, provider_name: str, threshold: int, cooldown: float):
        self.provider_name = provider_name
        self.threshold = threshold
        self.cooldown = cooldown
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failures = 0
        self.last_state_change = time.time()
        
    def can_execute(self) -> bool:
        now = time.time()
        if self.state == "OPEN":
            # Check if cooldown has elapsed
            if now - self.last_state_change >= self.cooldown:
                self.state = "HALF_OPEN"
                self.last_state_change = now
                return True
            return False
        return True
        
    def record_success(self) -> None:
        self.failures = 0
        self.state = "CLOSED"
        self.last_state_change = time.time()
        
    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            
    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "state": self.state,
            "failures": self.failures,
            "last_state_change": self.last_state_change,
            "cooldown_remaining": max(0.0, self.cooldown - (time.time() - self.last_state_change)) if self.state == "OPEN" else 0.0
        }
