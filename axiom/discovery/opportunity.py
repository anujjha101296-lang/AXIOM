"""Opportunity scoring from research gaps — opportunities, not discoveries."""

from __future__ import annotations

from axiom.discovery.models import ResearchOpportunity, _new_id
from axiom.skai.models import ResearchGap


def score_opportunity(gap: ResearchGap) -> ResearchOpportunity:
    """Convert a ResearchGap into a scored ResearchOpportunity."""
    gap_type = (gap.gap_type or "").lower()
    importance = 0.7 if "conflict" in gap_type else 0.55
    if "open_question" in gap_type:
        importance = 0.65
    if "unverified" in gap_type:
        importance = 0.6

    gap_evidence = min(1.0, 0.4 + 0.1 * len(gap.related_entity_ids) + 0.15 * len(gap.related_conflict_ids))
    novelty = 0.35  # conservative default without literature search
    feasibility = 0.7 if "conflict" in gap_type else 0.55
    impact = float(gap.priority_score or 0.5)
    verification_difficulty = 0.6
    cost = 0.4
    info_gain = 0.55 + (0.1 if gap.related_conflict_ids else 0.0)

    # Balanced composite — not only easy or only impressive.
    composite = (
        0.18 * importance
        + 0.16 * gap_evidence
        + 0.12 * novelty
        + 0.14 * feasibility
        + 0.14 * impact
        + 0.08 * (1.0 - verification_difficulty)
        + 0.08 * (1.0 - cost)
        + 0.10 * info_gain
    )

    return ResearchOpportunity(
        opportunity_id=_new_id("opp"),
        title=gap.title,
        description=gap.description,
        gap_ids=[gap.gap_id],
        scientific_importance=round(importance, 3),
        gap_evidence=round(gap_evidence, 3),
        novelty_likelihood=round(novelty, 3),
        feasibility=round(feasibility, 3),
        potential_impact=round(impact, 3),
        verification_difficulty=round(verification_difficulty, 3),
        computational_cost=round(cost, 3),
        expected_information_gain=round(info_gain, 3),
        composite_score=round(composite, 3),
        rationale=(
            f"Scored from gap_type={gap.gap_type}; "
            f"entities={len(gap.related_entity_ids)}; conflicts={len(gap.related_conflict_ids)}. "
            "This is a RESEARCH_OPPORTUNITY, not a discovery."
        ),
    )


def rank_opportunities(gaps: list[ResearchGap], *, limit: int = 10) -> list[ResearchOpportunity]:
    scored = [score_opportunity(g) for g in gaps]
    scored.sort(key=lambda o: o.composite_score, reverse=True)
    return scored[:limit]
