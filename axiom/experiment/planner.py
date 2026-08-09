"""Experiment planning — hypothesis discrimination (SEC §7)."""

from __future__ import annotations

from typing import Any


def plan_experiments(
    hypotheses: list[str],
    *,
    budget_usd: float = 1.0,
) -> list[dict[str, Any]]:
    """Propose experiments that distinguish competing hypotheses."""
    if len(hypotheses) < 2:
        return [{
            "hypothesis": hypotheses[0] if hypotheses else "H1",
            "experiment_type": "confirmatory",
            "expected_information_gain": 0.3,
            "estimated_cost": 0.1,
            "rationale": "Single hypothesis — confirmatory experiment",
        }]

    plans = []
    for i, h in enumerate(hypotheses):
        others = [hypotheses[j] for j in range(len(hypotheses)) if j != i]
        plans.append({
            "hypothesis": h,
            "experiment_type": "discriminative",
            "competing_hypotheses": others,
            "expected_information_gain": round(0.5 + 0.1 * len(others), 2),
            "estimated_cost": round(0.1 * (i + 1), 2),
            "estimated_runtime_minutes": 5 * (i + 1),
            "rationale": f"Test {h} against {', '.join(others)}",
        })

    plans.sort(key=lambda p: p["expected_information_gain"] / max(p["estimated_cost"], 0.01), reverse=True)
    affordable = [p for p in plans if p["estimated_cost"] <= budget_usd]
    return affordable or plans[:1]
