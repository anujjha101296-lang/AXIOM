from typing import Dict, Any, Optional
from axiom.services.billing.models import SubscriptionInfo, PlanTier, BillingState, EntitlementLimits

# In a real system, these would be loaded from a DB or config service.
TIER_LIMITS = {
    PlanTier.FREE: EntitlementLimits(max_research_runs_per_month=5, max_z3_verifications_per_month=20, max_documents=3, can_use_lean4=False, team_members_allowed=1),
    PlanTier.PRO: EntitlementLimits(max_research_runs_per_month=50, max_z3_verifications_per_month=500, max_documents=100, can_use_lean4=True, team_members_allowed=1),
    PlanTier.TEAM: EntitlementLimits(max_research_runs_per_month=500, max_z3_verifications_per_month=5000, max_documents=1000, can_use_lean4=True, team_members_allowed=5),
    PlanTier.ENTERPRISE: EntitlementLimits(max_research_runs_per_month=9999, max_z3_verifications_per_month=99999, max_documents=9999, can_use_lean4=True, team_members_allowed=99)
}

class EntitlementEngine:
    def __init__(self):
        # Memory mock for currently active subscriptions
        self._subscriptions: Dict[str, SubscriptionInfo] = {}

    def get_subscription(self, user_id: str) -> SubscriptionInfo:
        if user_id not in self._subscriptions:
            # Default to FREE trial
            self._subscriptions[user_id] = SubscriptionInfo(
                user_id=user_id,
                tier=PlanTier.FREE,
                state=BillingState.TRIALING,
                limits=TIER_LIMITS[PlanTier.FREE]
            )
        return self._subscriptions[user_id]

    def record_usage(self, user_id: str, resource: str, quantity: int = 1) -> bool:
        """
        Records usage and returns False if the action exceeds limits.
        """
        sub = self.get_subscription(user_id)
        
        # Never block data viewing (research deletion protection)
        if resource == "view_research":
            return True

        if sub.state in [BillingState.CANCELLED, BillingState.EXPIRED, BillingState.PAST_DUE]:
            # Degraded state - block creation/heavy compute, but allow viewing.
            return False

        current = sub.usage_this_period.get(resource, 0)
        
        # Check specific limits
        if resource == "research_run" and current + quantity > sub.limits.max_research_runs_per_month:
            return False
        if resource == "z3_verification" and current + quantity > sub.limits.max_z3_verifications_per_month:
            return False
        if resource == "document_upload" and current + quantity > sub.limits.max_documents:
            return False

        # Apply usage
        sub.usage_this_period[resource] = current + quantity
        return True

    def check_entitlement(self, user_id: str, feature: str) -> bool:
        sub = self.get_subscription(user_id)
        if feature == "lean4":
            return sub.limits.can_use_lean4
        if feature == "team_collaboration":
            return sub.limits.team_members_allowed > 1
        return True
