from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BillingProvider(ABC):
    @abstractmethod
    def create_customer(self, email: str, name: str) -> str:
        pass
        
    @abstractmethod
    def create_subscription(self, customer_id: str, plan_id: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        pass
        
    @abstractmethod
    def get_subscription_status(self, subscription_id: str) -> str:
        pass

    @abstractmethod
    def handle_webhook(self, payload: bytes, signature: str) -> bool:
        """Process idempotently signed webhooks from provider"""
        pass

class MockBillingProvider(BillingProvider):
    """
    Used for local testing until Stripe/Paddle is integrated.
    Never processes real card data.
    """
    def __init__(self):
        self.customers = {}
        self.subscriptions = {}

    def create_customer(self, email: str, name: str) -> str:
        cid = f"cus_{hash(email)}"
        self.customers[cid] = {"email": email, "name": name}
        return cid

    def create_subscription(self, customer_id: str, plan_id: str) -> Dict[str, Any]:
        sub_id = f"sub_{hash(customer_id + plan_id)}"
        self.subscriptions[sub_id] = {"customer": customer_id, "plan": plan_id, "status": "ACTIVE"}
        return self.subscriptions[sub_id]

    def cancel_subscription(self, subscription_id: str) -> bool:
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]["status"] = "CANCELLED"
            return True
        return False

    def get_subscription_status(self, subscription_id: str) -> str:
        return self.subscriptions.get(subscription_id, {}).get("status", "NOT_FOUND")

    def handle_webhook(self, payload: bytes, signature: str) -> bool:
        return True
