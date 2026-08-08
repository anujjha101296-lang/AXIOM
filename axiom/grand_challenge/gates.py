"""Readiness gates — capability thresholds before tier advancement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from axiom.evaluation.frameworks.capability import CapabilityDimension
from axiom.grand_challenge.models import Campaign, ChallengeTier


@dataclass
class GateRequirement:
    tier_from: ChallengeTier
    tier_to: ChallengeTier
    description: str
    min_composite_score: float | None
    min_dimension_scores: dict[str, float]
    min_challenges_completed: int
    min_experiments_run: int
    min_evidence_records: int
    min_checkpoints: int
    require_human_approval: bool
    notes: str = ""


@dataclass
class GateEvaluation:
    gate_id: str
    passed: bool
    tier_from: int
    tier_to: int
    checks: list[dict[str, Any]]
    blockers: list[str]
    warnings: list[str]


# Honest thresholds based on SCEP capability framework — not inflated
GATE_REQUIREMENTS: list[GateRequirement] = [
    GateRequirement(
        tier_from=ChallengeTier.TIER_0_TOY,
        tier_to=ChallengeTier.TIER_1_KNOWN_ANSWER,
        description="Complete Tier 0 toy challenges with measured evidence",
        min_composite_score=None,
        min_dimension_scores={"mathematical_reasoning": 0.4},
        min_challenges_completed=2,
        min_experiments_run=2,
        min_evidence_records=2,
        min_checkpoints=1,
        require_human_approval=False,
        notes="Tier 0 validates pipeline; Tier 1 requires basic math reasoning.",
    ),
    GateRequirement(
        tier_from=ChallengeTier.TIER_1_KNOWN_ANSWER,
        tier_to=ChallengeTier.TIER_2_PAPER_REPRODUCTION,
        description="Demonstrate known-answer competence before paper reproduction",
        min_composite_score=0.35,
        min_dimension_scores={
            "mathematical_reasoning": 0.5,
            "proof_verification": 0.3,
        },
        min_challenges_completed=3,
        min_experiments_run=5,
        min_evidence_records=5,
        min_checkpoints=2,
        require_human_approval=True,
        notes="Proof verification may be simulated; evidence tier must be honest.",
    ),
    GateRequirement(
        tier_from=ChallengeTier.TIER_2_PAPER_REPRODUCTION,
        tier_to=ChallengeTier.TIER_3_SMALL_OPEN,
        description="Reproduce methodology before attempting open questions",
        min_composite_score=0.45,
        min_dimension_scores={
            "research_planning": 0.3,
            "literature_synthesis": 0.3,
        },
        min_challenges_completed=2,
        min_experiments_run=8,
        min_evidence_records=8,
        min_checkpoints=3,
        require_human_approval=True,
    ),
    GateRequirement(
        tier_from=ChallengeTier.TIER_3_SMALL_OPEN,
        tier_to=ChallengeTier.TIER_4_DOMAIN_GRAND,
        description="Bounded open research before multi-year grand campaigns",
        min_composite_score=0.55,
        min_dimension_scores={
            "conjecture_generation": 0.2,
            "research_planning": 0.4,
        },
        min_challenges_completed=2,
        min_experiments_run=15,
        min_evidence_records=15,
        min_checkpoints=5,
        require_human_approval=True,
        notes="Conjecture generation threshold is intentionally low — heuristic scoring.",
    ),
    GateRequirement(
        tier_from=ChallengeTier.TIER_4_DOMAIN_GRAND,
        tier_to=ChallengeTier.TIER_5_FRONTIER,
        description="Organizational maturity before frontier capability tests",
        min_composite_score=0.60,
        min_dimension_scores={
            "mathematical_reasoning": 0.6,
            "proof_verification": 0.5,
            "knowledge_quality": 0.4,
        },
        min_challenges_completed=2,
        min_experiments_run=30,
        min_evidence_records=30,
        min_checkpoints=10,
        require_human_approval=True,
        notes="Tier 5 assesses readiness; does NOT authorize prize solution attempts.",
    ),
]


def get_gate(from_tier: ChallengeTier, to_tier: ChallengeTier) -> GateRequirement | None:
    for gate in GATE_REQUIREMENTS:
        if gate.tier_from == from_tier and gate.tier_to == to_tier:
            return gate
    return None


def evaluate_gate(
    campaign: Campaign,
    capability_snapshot: dict[str, Any] | None = None,
) -> GateEvaluation:
    """Evaluate whether a campaign may advance to the next tier."""
    from_tier = campaign.current_tier
    to_tier = ChallengeTier(min(int(from_tier) + 1, 5))
    gate = get_gate(from_tier, to_tier)

    if gate is None:
        return GateEvaluation(
            gate_id=f"gate_{int(from_tier)}_to_{int(to_tier)}",
            passed=False,
            tier_from=int(from_tier),
            tier_to=int(to_tier),
            checks=[],
            blockers=[f"No gate defined for tier {int(from_tier)} → {int(to_tier)}"],
            warnings=[],
        )

    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    # Challenge completion
    tier_challenges = [c for c in campaign.challenge_ids if c.startswith(f"t{int(from_tier)}_")]
    completed_in_tier = [c for c in campaign.challenges_completed if c in tier_challenges]
    challenge_ok = len(completed_in_tier) >= gate.min_challenges_completed
    checks.append({
        "check": "challenges_completed",
        "required": gate.min_challenges_completed,
        "actual": len(completed_in_tier),
        "passed": challenge_ok,
    })
    if not challenge_ok:
        blockers.append(
            f"Need {gate.min_challenges_completed} Tier {int(from_tier)} challenges completed; "
            f"have {len(completed_in_tier)}"
        )

    # Experiments
    exp_count = len([e for e in campaign.experiments if e.status.value == "completed"])
    exp_ok = exp_count >= gate.min_experiments_run
    checks.append({"check": "experiments_run", "required": gate.min_experiments_run, "actual": exp_count, "passed": exp_ok})
    if not exp_ok:
        blockers.append(f"Need {gate.min_experiments_run} experiments; have {exp_count}")

    # Evidence
    ev_ok = len(campaign.evidence) >= gate.min_evidence_records
    checks.append({
        "check": "evidence_records",
        "required": gate.min_evidence_records,
        "actual": len(campaign.evidence),
        "passed": ev_ok,
    })
    if not ev_ok:
        blockers.append(f"Need {gate.min_evidence_records} evidence records; have {len(campaign.evidence)}")

    # Checkpoints
    cp_ok = len(campaign.checkpoints) >= gate.min_checkpoints
    checks.append({
        "check": "checkpoints",
        "required": gate.min_checkpoints,
        "actual": len(campaign.checkpoints),
        "passed": cp_ok,
    })
    if not cp_ok:
        blockers.append(f"Need {gate.min_checkpoints} checkpoints; have {len(campaign.checkpoints)}")

    # Capability scores (if snapshot provided)
    if capability_snapshot:
        composite = capability_snapshot.get("composite_score", 0.0)
        if gate.min_composite_score is not None:
            comp_ok = composite >= gate.min_composite_score
            checks.append({
                "check": "composite_score",
                "required": gate.min_composite_score,
                "actual": composite,
                "passed": comp_ok,
            })
            if not comp_ok:
                blockers.append(f"Composite score {composite:.3f} < {gate.min_composite_score}")

        dimensions = capability_snapshot.get("dimensions", {})
        for dim, threshold in gate.min_dimension_scores.items():
            dim_data = dimensions.get(dim, {})
            score = dim_data.get("score", 0.0) if isinstance(dim_data, dict) else 0.0
            estimated = dim_data.get("estimated", True) if isinstance(dim_data, dict) else True
            dim_ok = score >= threshold
            checks.append({
                "check": f"dimension:{dim}",
                "required": threshold,
                "actual": score,
                "passed": dim_ok,
                "estimated": estimated,
            })
            if not dim_ok:
                blockers.append(f"{dim} score {score:.3f} < {threshold}")
            if estimated:
                warnings.append(f"{dim} score is estimated, not measured")
    else:
        warnings.append("No capability snapshot provided; dimension checks skipped")

    if gate.require_human_approval:
        approved = campaign.context.get("human_approval", {}).get(str(int(to_tier)), False)
        checks.append({"check": "human_approval", "required": True, "actual": approved, "passed": approved})
        if not approved:
            blockers.append(f"Human approval required for Tier {int(to_tier)} advancement")

    passed = len(blockers) == 0
    return GateEvaluation(
        gate_id=f"gate_{int(from_tier)}_to_{int(to_tier)}",
        passed=passed,
        tier_from=int(from_tier),
        tier_to=int(to_tier),
        checks=checks,
        blockers=blockers,
        warnings=warnings,
    )


def list_gates() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": f"gate_{int(g.tier_from)}_to_{int(g.tier_to)}",
            "from_tier": int(g.tier_from),
            "to_tier": int(g.tier_to),
            "description": g.description,
            "min_composite_score": g.min_composite_score,
            "min_dimension_scores": g.min_dimension_scores,
            "min_challenges_completed": g.min_challenges_completed,
            "min_experiments_run": g.min_experiments_run,
            "min_evidence_records": g.min_evidence_records,
            "min_checkpoints": g.min_checkpoints,
            "require_human_approval": g.require_human_approval,
            "notes": g.notes,
        }
        for g in GATE_REQUIREMENTS
    ]
