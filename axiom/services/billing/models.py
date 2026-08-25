from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

class PlanTier(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    TEAM = "TEAM"
    ENTERPRISE = "ENTERPRISE"

class BillingState(str, Enum):
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    PAYMENT_FAILED = "PAYMENT_FAILED"

class EntitlementLimits(BaseModel):
    max_research_runs_per_month: int = 5
    max_z3_verifications_per_month: int = 20
    max_documents: int = 3
    can_use_lean4: bool = False
    team_members_allowed: int = 1

class SubscriptionInfo(BaseModel):
    user_id: str
    org_id: Optional[str] = None
    tier: PlanTier = PlanTier.FREE
    state: BillingState = BillingState.TRIALING
    limits: EntitlementLimits = Field(default_factory=EntitlementLimits)
    usage_this_period: Dict[str, int] = Field(default_factory=dict)
