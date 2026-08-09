"""Human review gates (FRCE §11)."""

from __future__ import annotations

from axiom.campaign.models import ContributionLevel, FrontierCampaign, HumanGateRequest, _new_id, _utc_now


GATE_TRIGGERS = {
    "novel_claim": "A novel scientific claim appeared",
    "evidence_conflict": "Evidence conflicts detected",
    "direction_change": "Major research direction change proposed",
    "formal_proof_success": "Formal proof compilation succeeded",
    "counterexample_found": "Computational counterexample found",
    "potential_contribution": "Potential scientific contribution detected",
    "resource_threshold": "Resource consumption exceeded threshold",
    "external_publication": "AXIOM wants to publish externally",
}


def should_trigger_gate(
    campaign: FrontierCampaign,
    *,
    trigger: str,
    details: dict | None = None,
) -> HumanGateRequest | None:
    """Determine if human review is required."""
    always_gate = {
        "formal_proof_success",
        "counterexample_found",
        "external_publication",
        "novel_claim",
    }
    threshold_gate = {"resource_threshold"}

    if trigger in always_gate:
        return _create_gate(campaign, trigger, details)

    if trigger in threshold_gate:
        consumed = campaign.budget.consumed.get("compute_units", 0)
        if consumed > campaign.budget.compute_units * 0.8:
            return _create_gate(campaign, trigger, details)

    if trigger == "potential_contribution":
        level = campaign.contribution_level
        if level in (
            ContributionLevel.VERIFIED_LEMMA,
            ContributionLevel.PARTIAL_THEOREM,
            ContributionLevel.MAJOR_BREAKTHROUGH,
            ContributionLevel.POTENTIAL_COMPLETE_SOLUTION,
        ):
            return _create_gate(campaign, trigger, details)

    return None


def _create_gate(
    campaign: FrontierCampaign,
    trigger: str,
    details: dict | None,
) -> HumanGateRequest:
    gate = HumanGateRequest(
        gate_id=_new_id("gate"),
        reason=GATE_TRIGGERS.get(trigger, trigger),
        trigger=trigger,
        details=details or {},
    )
    campaign.human_gates.append(gate)
    return gate


def resolve_gate(
    campaign: FrontierCampaign,
    gate_id: str,
    *,
    approved: bool,
    notes: str = "",
) -> HumanGateRequest | None:
    for gate in campaign.human_gates:
        if gate.gate_id != gate_id:
            continue
        gate.status = "approved" if approved else "rejected"
        gate.resolved_at = _utc_now()
        gate.details["resolution_notes"] = notes
        return gate
    return None


def pending_gates(campaign: FrontierCampaign) -> list[HumanGateRequest]:
    return [g for g in campaign.human_gates if g.status == "pending"]
