"""Research readiness + progression gates — evidence-based, no skip tiers."""

from __future__ import annotations

from typing import Any

from axiom.evaluation.arena.models import DimensionScores


# Minimum measured scores to unlock the *next* tier.
# Keys are the tier you want to ENTER.
TIER_GATES: dict[int, dict[str, float]] = {
    1: {"correctness": 0.5, "reliability": 0.5},
    2: {"correctness": 0.6, "reasoning": 0.55},
    3: {"reasoning": 0.6, "correctness": 0.65},
    4: {"formal_verification": 0.5, "reasoning": 0.65},
    5: {"reproduction": 0.5, "evidence": 0.45},
    6: {"scientific_honesty": 0.7, "false_discovery_rate": 0.15},
    7: {"scientific_honesty": 0.8, "counterexample_detection": 0.7},
    8: {"research_depth": 0.6, "reliability": 0.75, "long_horizon_floor": 0.55},
    9: {"research_depth": 0.75, "reproduction": 0.7, "long_horizon_floor": 0.7},
    10: {
        "formal_verification": 0.98,
        "scientific_honesty": 0.95,
        "long_horizon_floor": 0.95,
        "false_discovery_rate": 0.01,
    },
}

_RATE_METRICS = {"false_discovery_rate", "false_confidence_rate", "hallucination_rate"}


def evaluate_readiness(scores: DimensionScores) -> dict[str, Any]:
    """Compute readiness domains and highest unlocked tier from evidence."""
    d = scores.to_dict()
    lh_cases = float(d.get("long_horizon", 0.0) or 0.0)
    if lh_cases > 0:
        # Dedicated LH suite present — measure without soft-cap; hard-cap below Tier-10 threshold.
        long_horizon = _clamp(min(0.9, 0.35 + 0.55 * lh_cases))
        lh_note = "Measured from dedicated long-horizon cases (capped at 0.9)."
    else:
        long_horizon = _clamp((d["research_depth"] + d["reliability"]) / 2 * 0.35)
        lh_note = "No dedicated LH cases — soft-capped proxy (Tier 8+ blocked)."

    domains = {
        "basic_research": _clamp((d["correctness"] + d["reasoning"] + d["reliability"]) / 3),
        "advanced_research": _clamp((d["research_depth"] + d["research_breadth"] + d["evidence"]) / 3),
        "mathematics": _clamp((d["reasoning"] + d["correctness"]) / 2),
        "formal_mathematics": _clamp(d["formal_verification"]),
        "experimentation": _clamp((d["reproduction"] + d["evidence"] + d["counterexample_detection"]) / 3),
        "autonomy": _clamp((d["reliability"] + d["research_depth"]) / 2),
        "long_horizon_research": long_horizon,
        "scientific_reliability": _clamp(
            (d["scientific_honesty"] + (1 - d["false_discovery_rate"]) + d["counterexample_detection"]) / 3
        ),
    }
    d = {**d, "long_horizon_floor": domains["long_horizon_research"]}

    unlocked = 0
    gate_log: list[dict[str, Any]] = []
    for tier in range(1, 11):
        reqs = TIER_GATES.get(tier, {})
        ok = True
        details = []
        for metric, threshold in reqs.items():
            val = d.get(metric, 0.0)
            if metric in _RATE_METRICS:
                passed = val <= threshold
                details.append({"metric": metric, "value": val, "max": threshold, "passed": passed})
            else:
                passed = val >= threshold
                details.append({"metric": metric, "value": val, "min": threshold, "passed": passed})
            ok = ok and passed
        gate_log.append({"enter_tier": tier, "passed": ok, "checks": details})
        if ok:
            unlocked = tier
        else:
            break

    return {
        "domains": domains,
        "highest_unlocked_tier": unlocked,
        "millennium_ready": False,
        "gate_log": gate_log,
        "notes": [
            "Readiness is measured from Arena scores, not developer opinion.",
            lh_note,
            "Tier 10 / Millennium requires extraordinary independent evidence.",
        ],
    }


def _clamp(x: float) -> float:
    return round(max(0.0, min(1.0, float(x))), 4)
