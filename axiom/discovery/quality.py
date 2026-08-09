"""Research quality scorecard for Discovery Engine investigations.

Scores are diagnostic — not scientific verification and not a novelty claim.
"""

from __future__ import annotations

from typing import Any

from axiom.discovery.hypotheses import active_hypotheses
from axiom.discovery.models import Discovery, DiscoveryStatus


_DIMENSIONS = (
    "research_planning",
    "evidence_quality",
    "citation_accuracy",
    "novelty_assessment",
    "hypothesis_quality",
    "counterexample_detection",
    "experimental_quality",
    "reproducibility",
    "formal_verification",
    "scientific_honesty",
    "cost",
    "latency",
)


def score_discovery(d: Discovery) -> dict[str, Any]:
    """Produce a conservative multi-dimension scorecard (0.0–1.0 per dimension)."""
    active = active_hypotheses(d.hypotheses)
    rejected = [h for h in d.hypotheses if h.rejected]
    scores: dict[str, float] = {k: 0.0 for k in _DIMENSIONS}

    # Planning: opportunity + multiple hypotheses + predictions
    scores["research_planning"] = min(
        1.0,
        (0.35 if d.opportunity else 0.0)
        + (0.35 if len(active) >= 2 else 0.1 * len(active))
        + (0.3 if d.predictions else 0.0),
    )

    # Evidence: experiments exist but capped — computational ≠ proof
    if d.experiment_ids:
        scores["evidence_quality"] = 0.45
        if d.confidence.experiment_confidence:
            scores["evidence_quality"] = min(0.6, 0.3 + d.confidence.experiment_confidence * 0.4)
    else:
        scores["evidence_quality"] = 0.1

    # Citations / novelty honesty
    novelty = d.novelty.status.value
    if novelty == "INSUFFICIENT_SEARCH":
        scores["citation_accuracy"] = 0.55  # honest about limits
        scores["novelty_assessment"] = 0.7  # correctly refused to claim novelty
    elif novelty in {"RELATED_WORK_FOUND", "POSSIBLY_KNOWN", "LIKELY_KNOWN"}:
        scores["citation_accuracy"] = 0.65
        scores["novelty_assessment"] = 0.75
    elif novelty == "NO_RELEVANT_PRIOR_WORK_FOUND":
        scores["citation_accuracy"] = 0.4
        scores["novelty_assessment"] = 0.5  # still incomplete coverage risk
    else:
        scores["novelty_assessment"] = 0.3

    # Hypothesis quality: competing set + QC rejections recorded
    scores["hypothesis_quality"] = min(
        1.0,
        (0.4 if len(active) >= 2 else 0.15)
        + (0.2 if rejected else 0.0)
        + (0.2 if any(h.predictions for h in active) else 0.0)
        + (0.2 if any(h.disproof_strategy for h in active) else 0.0),
    )

    # Counterexample detection
    if d.status == DiscoveryStatus.REFUTED and d.counterexample_ids:
        scores["counterexample_detection"] = 0.85
    elif d.counterexample_ids:
        scores["counterexample_detection"] = 0.6
    else:
        scores["counterexample_detection"] = 0.25

    # Experimental quality / reproducibility
    if d.experiment_ids:
        scores["experimental_quality"] = 0.5
        scores["reproducibility"] = 0.4  # sandbox runs are reproducible in principle
    else:
        scores["experimental_quality"] = 0.1
        scores["reproducibility"] = 0.1

    # Formal verification — prose never counts
    formal = (d.report or {}).get("formal_bridge") or {}
    if formal.get("compiled_verified") is True:
        scores["formal_verification"] = 0.9
    elif formal.get("attempted"):
        scores["formal_verification"] = 0.35
    else:
        scores["formal_verification"] = 0.0

    # Scientific honesty: never claim discovery; separate confidence channels
    honesty = 0.5
    if d.report.get("is_scientific_discovery_claim") is False:
        honesty += 0.25
    if d.status != DiscoveryStatus.VERIFIED:
        honesty += 0.15
    if novelty == "INSUFFICIENT_SEARCH" or "not" in (d.novelty.search_notes or "").lower():
        honesty += 0.1
    scores["scientific_honesty"] = min(1.0, honesty)

    # Cost / latency placeholders (lower cost/latency → higher score; unknown → mid)
    scores["cost"] = 0.6
    scores["latency"] = 0.6

    overall = sum(scores.values()) / len(scores)
    return {
        "dimensions": scores,
        "overall": round(overall, 4),
        "notes": [
            "Scorecard is diagnostic only.",
            "Does not certify scientific discovery or formal proof.",
            "Computational evidence remains computational evidence.",
        ],
        "false_discovery_safe": d.status
        not in {DiscoveryStatus.VERIFIED, DiscoveryStatus.PUBLISHED_CANDIDATE},
    }
