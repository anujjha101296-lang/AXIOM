"""Research validation dashboard aggregation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from axiom.research_validation.dataset import dataset_stats
from axiom.research_validation.store import RVPStore


def build_dashboard(store: RVPStore) -> dict[str, Any]:
    """Aggregate dashboard metrics from stored runs."""
    runs = store.list_runs(limit=500)
    if not runs:
        return {
            "current_experiments": [],
            "completed_experiments": 0,
            "success_rate": 0.0,
            "failure_reasons": {},
            "capability_trends": {},
            "benchmark_trends": {},
            "cost_ms_total": 0.0,
            "latency_ms_avg": 0.0,
            "dataset": dataset_stats(),
        }

    passed = sum(1 for r in runs if r.get("passed"))
    failure_reasons: Counter[str] = Counter()
    for r in runs:
        if not r.get("passed"):
            failure_reasons["answer_score_below_threshold"] += 1

    capability_sums: dict[str, float] = {}
    capability_counts = 0
    benchmark_by_stage: dict[str, list[float]] = {}

    for r in runs:
        capability_counts += 1
        for dim, val in r.get("capability_score", {}).items():
            if dim == "composite":
                continue
            capability_sums[dim] = capability_sums.get(dim, 0.0) + val
        stage_key = str(r.get("stage", 0))
        benchmark_by_stage.setdefault(stage_key, []).append(r.get("answer_score", 0.0))

    capability_trends = {
        k: round(v / max(capability_counts, 1), 4) for k, v in capability_sums.items()
    }
    benchmark_trends = {
        k: round(sum(v) / len(v), 4) if v else 0.0 for k, v in benchmark_by_stage.items()
    }

    return {
        "current_experiments": runs[:5],
        "completed_experiments": len(runs),
        "success_rate": round(passed / len(runs), 4),
        "failure_reasons": dict(failure_reasons),
        "capability_trends": capability_trends,
        "benchmark_trends": benchmark_trends,
        "cost_ms_total": round(sum(r.get("cost_ms", 0) for r in runs), 2),
        "latency_ms_avg": round(sum(r.get("latency_ms", 0) for r in runs) / len(runs), 2),
        "dataset": dataset_stats(),
    }
