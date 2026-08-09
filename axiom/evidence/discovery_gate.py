"""Discovery gate — prevent unauthorized claim status upgrades (E&R §15)."""

from __future__ import annotations

from dataclasses import dataclass

from axiom.evidence.models import (
    DISCOVERY_LABELS,
    ClaimStatus,
    EvidenceObject,
    EvidenceType,
    ScientificClaim,
    status_rank,
)


@dataclass
class GateResult:
    allowed: bool
    reason: str = ""

    def to_dict(self) -> dict[str, str | bool]:
        return {"allowed": self.allowed, "reason": self.reason}


def validate_status_upgrade(
    claim: ScientificClaim,
    new_status: ClaimStatus,
    evidence: list[EvidenceObject],
    *,
    reviewer: str | None = None,
) -> GateResult:
    """Validate whether a claim may transition to new_status."""
    old = claim.status
    if new_status == old:
        return GateResult(True)

    # Downgrades to rejected/disproved always allowed with evidence of contradiction
    if new_status in (ClaimStatus.REJECTED, ClaimStatus.DISPROVED):
        return GateResult(True)

    if status_rank(new_status) < status_rank(old):
        return GateResult(True, "downgrade permitted")

    supporting = [e for e in evidence if e.evidence_id in claim.supporting_evidence_ids]

    if new_status == ClaimStatus.SUPPORTED and not supporting:
        return GateResult(False, "SUPPORTED requires at least one supporting evidence object")

    if new_status == ClaimStatus.VERIFIED:
        if not supporting:
            return GateResult(False, "VERIFIED requires supporting evidence")
        if all(e.evidence_type == EvidenceType.SIMULATION for e in supporting):
            return GateResult(
                False,
                "VERIFIED cannot be granted from simulation-only evidence",
            )

    if new_status == ClaimStatus.FORMALLY_VERIFIED:
        formal = [
            e
            for e in supporting
            if e.evidence_type == EvidenceType.FORMAL_PROOF and e.formally_verified
        ]
        if not formal:
            return GateResult(
                False,
                "FORMALLY_VERIFIED requires formal_proof evidence from an actual verifier",
            )
        if not formal[0].verifier:
            return GateResult(False, "FORMALLY_VERIFIED requires verifier identity")

    if status_rank(new_status) > status_rank(old) + 2 and not reviewer:
        return GateResult(
            False,
            "Skipping more than one status level requires human reviewer",
        )

    return GateResult(True)


def validate_discovery_label(
    claim: ScientificClaim,
    label: str,
    evidence: list[EvidenceObject],
    *,
    reproduction_passed: bool = False,
    independent_verification: bool = False,
    human_review: bool = False,
) -> GateResult:
    """Block major discovery labels without verification requirements."""
    if label not in DISCOVERY_LABELS:
        return GateResult(True, "not a discovery label")

    if claim.status not in (
        ClaimStatus.VERIFIED,
        ClaimStatus.FORMALLY_VERIFIED,
    ):
        return GateResult(
            False,
            f"Discovery label '{label}' requires VERIFIED or FORMALLY_VERIFIED status",
        )

    if not reproduction_passed:
        return GateResult(False, "Discovery labels require successful reproduction")

    if not independent_verification:
        return GateResult(False, "Discovery labels require independent verification")

    if not human_review:
        return GateResult(False, "Discovery labels require human expert review")

    formal_required = label in ("NEW_THEOREM", "PROOF_OF_OPEN_PROBLEM")
    if formal_required and claim.status != ClaimStatus.FORMALLY_VERIFIED:
        return GateResult(
            False,
            f"Label '{label}' requires FORMALLY_VERIFIED status",
        )

    if not claim.supporting_evidence_ids:
        return GateResult(False, "Discovery labels require documented evidence")

    return GateResult(True)
