from abc import ABC, abstractmethod
from typing import Optional, Any
import uuid

class AbstractBillingService(ABC):
    """Abstract interface defining standard operations for external payment gateways."""
    
    @abstractmethod
    async def create_customer(self, user_id: uuid.UUID, email: str) -> str:
        """Registers a customer with the provider and returns their gateway ID."""
        pass
        
    @abstractmethod
    async def create_checkout_session(self, user_id: uuid.UUID, plan_name: str, cancel_url: str, success_url: str) -> str:
        """Generates a secure checkout URL for purchasing a tier subscription."""
        pass
        
    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancels a customer tier subscription at the end of the billing period."""
        pass
        
    @abstractmethod
    async def process_webhook_payload(self, event_type: str, payload: dict) -> None:
        """Processes raw events payload sent from the gateway provider."""
        pass
