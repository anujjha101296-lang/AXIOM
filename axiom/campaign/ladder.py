"""Challenge ladder levels 0–9 (FRCE §14)."""

from __future__ import annotations

from axiom.campaign.models import ContributionLevel, FrontierCampaign, LadderLevel
from axiom.grand_challenge.models import ChallengeTier


LADDER_DESCRIPTIONS: dict[LadderLevel, str] = {
    LadderLevel.LEVEL_0_SIMPLE_REASONING: "Simple reasoning — infrastructure validation",
    LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH: "Known-answer mathematics — hidden ground truth",
    LadderLevel.LEVEL_2_FORMAL_REPRODUCTION: "Formal theorem reproduction",
    LadderLevel.LEVEL_3_PUBLISHED_REPRODUCTION: "Published research reproduction",
    LadderLevel.LEVEL_4_RESEARCH_BENCHMARK: "Research-grade benchmark problems",
    LadderLevel.LEVEL_5_SMALL_OPEN: "Small open problems",
    LadderLevel.LEVEL_6_OPEN_SUBPROBLEM: "Meaningful open subproblems",
    LadderLevel.LEVEL_7_MAJOR_OPEN: "Major open research questions",
    LadderLevel.LEVEL_8_FRONTIER: "Frontier mathematical/scientific problems",
    LadderLevel.LEVEL_9_MILLENNIUM: "Millennium-level campaigns — earned through evidence",
}


# Map GCP tiers to FRCE ladder levels
_GCP_TO_LADDER: dict[int, LadderLevel] = {
    0: LadderLevel.LEVEL_0_SIMPLE_REASONING,
    1: LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH,
    2: LadderLevel.LEVEL_3_PUBLISHED_REPRODUCTION,
    3: LadderLevel.LEVEL_5_SMALL_OPEN,
    4: LadderLevel.LEVEL_7_MAJOR_OPEN,
    5: LadderLevel.LEVEL_8_FRONTIER,
}


CONTRIBUTION_TO_LADDER_READINESS: dict[ContributionLevel, int] = {
    ContributionLevel.NO_PROGRESS: 0,
    ContributionLevel.USEFUL_OBSERVATION: 0,
    ContributionLevel.NEW_CONJECTURE: 1,
    ContributionLevel.COUNTEREXAMPLE: 1,
    ContributionLevel.NEW_LEMMA: 2,
    ContributionLevel.VERIFIED_LEMMA: 3,
    ContributionLevel.PARTIAL_THEOREM: 4,
    ContributionLevel.NEW_METHOD: 3,
    ContributionLevel.PUBLISHED_CONTRIBUTION: 5,
    ContributionLevel.MAJOR_BREAKTHROUGH: 6,
    ContributionLevel.POTENTIAL_COMPLETE_SOLUTION: 8,
}


def ladder_manifest() -> dict:
    return {
        "levels": [
            {"level": int(level), "description": desc}
            for level, desc in LADDER_DESCRIPTIONS.items()
        ],
        "advancement_rule": "AXIOM earns the right to move upward through evidence",
        "millennium_gate": "Level 9 requires human strategic approval and FMTP millennium gate",
    }


def gcp_tier_to_ladder(tier: ChallengeTier | int) -> LadderLevel:
    t = int(tier)
    return _GCP_TO_LADDER.get(t, LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH)


def can_advance_ladder(campaign: FrontierCampaign) -> dict:
    """Check if campaign evidence supports ladder advancement."""
    readiness = CONTRIBUTION_TO_LADDER_READINESS.get(campaign.contribution_level, 0)
    current = int(campaign.ladder_level)
    target = current + 1
    can_advance = readiness >= target and target <= 9
    return {
        "current_level": current,
        "target_level": target,
        "contribution_level": campaign.contribution_level.value,
        "readiness_score": readiness,
        "can_advance": can_advance,
        "requires_human_approval": target >= 7,
    }
