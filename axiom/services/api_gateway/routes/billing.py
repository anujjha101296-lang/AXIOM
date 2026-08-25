from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from axiom.services.api_gateway.auth import verify_token
from axiom.services.billing.entitlement import EntitlementEngine
from axiom.services.billing.models import SubscriptionInfo

router = APIRouter(prefix="/billing", tags=["Billing"])
engine = EntitlementEngine()

class UsageEvent(BaseModel):
    resource: str
    quantity: int = 1

@router.get("/status", response_model=SubscriptionInfo)
def get_billing_status(token_data: dict = Depends(verify_token)):
    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return engine.get_subscription(user_id)

@router.post("/usage")
def report_usage(event: UsageEvent, token_data: dict = Depends(verify_token)):
    user_id = token_data.get("sub")
    allowed = engine.record_usage(user_id, event.resource, event.quantity)
    if not allowed:
        raise HTTPException(status_code=402, detail="Payment Required: Usage limits exceeded")
    return {"status": "ok", "message": "Usage recorded"}
