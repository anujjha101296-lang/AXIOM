"""Research pivot mechanism (FRCE §9)."""

from __future__ import annotations

from axiom.campaign.models import (
    CampaignPhase,
    ContributionLevel,
    CycleRecord,
    FrontierCampaign,
    PivotDecision,
)


def evaluate_cycle(campaign: FrontierCampaign, cycle: CycleRecord) -> PivotDecision:
    """
    After every research cycle, decide whether to continue, pivot, or escalate.

    Detects: repeated failure, diminishing returns, contradictory evidence,
    new promising directions, unexpected discoveries.
    """
    learned_count = len(cycle.learned)
    failed_count = len(cycle.failed_approaches)

    # Contradictory evidence or counterexample → pivot or disprove
    if cycle.contribution_level == ContributionLevel.COUNTEREXAMPLE:
        campaign.phase = CampaignPhase.DISPROVED
        return PivotDecision.PIVOT

    # Major progress → continue or escalate
    if cycle.contribution_level in (
        ContributionLevel.VERIFIED_LEMMA,
        ContributionLevel.PARTIAL_THEOREM,
        ContributionLevel.NEW_METHOD,
        ContributionLevel.MAJOR_BREAKTHROUGH,
    ):
        return PivotDecision.ESCALATE

    if cycle.contribution_level in (
        ContributionLevel.NEW_LEMMA,
        ContributionLevel.NEW_CONJECTURE,
        ContributionLevel.USEFUL_OBSERVATION,
    ):
        return PivotDecision.CONTINUE

    # Repeated failure without learning
    recent_failures = campaign.failed_approaches[-5:]
    if failed_count >= 3 and learned_count == 0:
        if len(set(recent_failures)) < len(recent_failures):
            campaign.phase = CampaignPhase.EXHAUSTED
            return PivotDecision.ABANDON

    # No progress but approaches not exhausted
    if learned_count == 0 and failed_count > 0:
        active_strategies = [s for s in campaign.strategies if s.status == "active"]
        if len(active_strategies) > 1:
            return PivotDecision.PIVOT
        return PivotDecision.CONTINUE

    # Budget exceeded
    if campaign.budget.budget_exceeded():
        campaign.phase = CampaignPhase.BLOCKED
        return PivotDecision.PAUSE

    return PivotDecision.CONTINUE


def apply_pivot(campaign: FrontierCampaign, decision: PivotDecision) -> FrontierCampaign:
    """Apply pivot decision to campaign state."""
    campaign.decisions.append({
        "decision": decision.value,
        "phase_before": campaign.phase.value,
    })

    if decision == PivotDecision.CONTINUE:
        campaign.phase = CampaignPhase.RESEARCHING
    elif decision == PivotDecision.PIVOT:
        # Mark current top strategy exhausted, activate next
        active = [s for s in campaign.strategies if s.status == "active"]
        if active:
            active[0].status = "exhausted"
            campaign.failed_approaches.append(active[0].name)
        remaining = [s for s in campaign.strategies if s.status == "active"]
        if remaining:
            remaining[0].status = "selected"
        else:
            campaign.phase = CampaignPhase.EXHAUSTED
        campaign.phase = CampaignPhase.RESEARCHING
    elif decision == PivotDecision.ESCALATE:
        campaign.phase = CampaignPhase.VERIFICATION
    elif decision == PivotDecision.PAUSE:
        campaign.phase = CampaignPhase.PAUSED
    elif decision == PivotDecision.ABANDON:
        campaign.phase = CampaignPhase.ABANDONED

    return campaign
