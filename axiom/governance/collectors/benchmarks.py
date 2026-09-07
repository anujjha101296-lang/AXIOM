"""Benchmark regression reporting."""

from __future__ import annotations

import json
from pathlib import Path

from axiom.governance.models import (
    CollectorResult,
    Finding,
    FindingCategory,
    MetricValue,
    Severity,
)

BENCHMARK_FILE = "benchmark_results.json"


def collect_benchmarks(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="benchmarks")
    bench_path = workspace / BENCHMARK_FILE

    if not bench_path.exists():
        result.findings.append(
            Finding(
                category=FindingCategory.BENCHMARK,
                severity=Severity.MEDIUM,
                title="No benchmark_results.json snapshot",
                detail="Scientific capability benchmarks have not been recorded.",
                recommendation="Run: python3 -m axiom.evaluation.run_benchmarks",
                source=BENCHMARK_FILE,
                score_impact=3.0,
            )
        )
        result.metrics.append(MetricValue("benchmark_snapshot", 0, target=1, status="warn"))
        return result

    try:
        data = json.loads(bench_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        result.findings.append(
            Finding(
                category=FindingCategory.BENCHMARK,
                severity=Severity.HIGH,
                title="Corrupt benchmark_results.json",
                detail="Cannot parse benchmark snapshot for regression analysis.",
                recommendation="Regenerate benchmark_results.json",
                source=BENCHMARK_FILE,
                score_impact=4.0,
            )
        )
        return result

    result.metrics.append(MetricValue("benchmark_snapshot", 1, target=1, status="ok"))
    regressions = 0
    improvements = 0

    deltas = data.get("dimension_deltas", {})
    for dim, info in deltas.items():
        delta_pct = info.get("delta_pct", 0)
        if delta_pct < -5:
            regressions += 1
            result.findings.append(
                Finding(
                    category=FindingCategory.BENCHMARK,
                    severity=Severity.HIGH,
                    title=f"Benchmark regression: {dim}",
                    detail=f"Score dropped {abs(delta_pct)}% ({info.get('prev_score')} → {info.get('curr_score')})",
                    recommendation=f"Investigate {dim} benchmark cases; add regression test",
                    source=BENCHMARK_FILE,
                    score_impact=4.0,
                )
            )
        elif delta_pct > 5:
            improvements += 1

    result.metrics.append(MetricValue("benchmark_regressions", regressions, target=0, status="ok" if regressions == 0 else "fail"))
    result.metrics.append(MetricValue("benchmark_improvements", improvements, unit="count"))

    composite = data.get("composite_delta_pct") or data.get("composite_score")
    if composite is not None:
        result.metrics.append(MetricValue("composite_benchmark_signal", composite, unit="varies"))

    result.raw["dimension_count"] = len(deltas)
    result.raw["regressions"] = regressions
    return result
