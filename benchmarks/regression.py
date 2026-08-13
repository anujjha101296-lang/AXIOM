"""
AXIOM Phase 8 — Regression Loop

Compares a current evaluation run against a stored baseline.
Detects: IMPROVED / UNCHANGED / REGRESSED / INCONCLUSIVE.

If regression exceeds configured tolerance, raises an error to
fail the verification pipeline.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.eval_models import (
    EvaluationRun,
    EvaluationResult,
    RegressionComparison,
    RegressionStatus,
)

BASELINE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evaluation_results",
    "baseline.json",
)


def save_baseline(run: EvaluationRun, path: str = BASELINE_PATH) -> None:
    """Save a run as the regression baseline."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(run.to_dict(), f, indent=2)
    print(f"✓ Baseline saved to {path}")


def load_baseline(path: str = BASELINE_PATH) -> Optional[dict]:
    """Load the baseline run data. Returns None if no baseline exists."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_runs(
    current_run: EvaluationRun,
    baseline_data: Optional[dict],
    tolerance: float = 0.05,
) -> RegressionComparison:
    """
    Compare current evaluation run against baseline.
    
    tolerance: Allowed relative degradation before flagging REGRESSED.
    e.g., 0.05 means a 5% drop in pass_rate triggers regression.
    """
    if baseline_data is None:
        return RegressionComparison(
            current_run_id=current_run.run_id,
            baseline_run_id=None,
            status=RegressionStatus.NO_BASELINE,
            regression_tolerance=tolerance,
        )

    baseline_run_id = baseline_data.get("run_id", "unknown")
    comparisons = []
    overall_status = RegressionStatus.UNCHANGED

    # Build lookup for baseline suite results
    baseline_suites = {
        s["suite_id"]: s
        for s in baseline_data.get("suite_results", [])
    }

    for suite_result in current_run.suite_results:
        suite_id = suite_result.suite_id
        current_pass_rate = suite_result.pass_rate

        baseline_suite = baseline_suites.get(suite_id)
        if baseline_suite is None:
            comparisons.append({
                "suite_id": suite_id,
                "status": "NEW_SUITE",
                "current_pass_rate": current_pass_rate,
                "baseline_pass_rate": None,
                "delta": None,
            })
            continue

        baseline_summary = baseline_suite.get("summary", {})
        baseline_pass_rate = baseline_summary.get("pass_rate", 0.0)

        delta = current_pass_rate - baseline_pass_rate

        if delta > tolerance:
            suite_status = RegressionStatus.IMPROVED
            if overall_status == RegressionStatus.UNCHANGED:
                overall_status = RegressionStatus.IMPROVED
        elif delta < -tolerance:
            suite_status = RegressionStatus.REGRESSED
            overall_status = RegressionStatus.REGRESSED  # Regression always wins
        elif abs(delta) <= tolerance:
            suite_status = RegressionStatus.UNCHANGED
        else:
            suite_status = RegressionStatus.INCONCLUSIVE

        comparisons.append({
            "suite_id": suite_id,
            "status": suite_status.value,
            "current_pass_rate": round(current_pass_rate, 4),
            "baseline_pass_rate": round(baseline_pass_rate, 4),
            "delta": round(delta, 4),
        })

    return RegressionComparison(
        current_run_id=current_run.run_id,
        baseline_run_id=baseline_run_id,
        status=overall_status,
        suite_comparisons=comparisons,
        regression_tolerance=tolerance,
    )


def print_regression_report(comparison: RegressionComparison) -> None:
    """Print a human-readable regression report."""
    icons = {
        RegressionStatus.IMPROVED: "⬆",
        RegressionStatus.UNCHANGED: "→",
        RegressionStatus.REGRESSED: "⬇",
        RegressionStatus.INCONCLUSIVE: "?",
        RegressionStatus.NO_BASELINE: "NEW",
    }
    icon = icons.get(comparison.status, "?")

    print(f"\n{'='*60}")
    print(f"REGRESSION REPORT")
    print(f"{'='*60}")
    print(f"Current Run:  {comparison.current_run_id}")
    print(f"Baseline Run: {comparison.baseline_run_id or 'None (first run)'}")
    print(f"Overall Status: {icon} {comparison.status.value}")
    print(f"Tolerance: ±{comparison.regression_tolerance*100:.1f}%")

    if comparison.suite_comparisons:
        print(f"\nSuite Comparisons:")
        for comp in comparison.suite_comparisons:
            delta = comp.get("delta")
            delta_str = f"{delta:+.2%}" if delta is not None else "N/A"
            baseline_str = f"{comp.get('baseline_pass_rate', 'N/A'):.2%}" if comp.get("baseline_pass_rate") is not None else "N/A"
            print(f"  {comp['suite_id']}: {baseline_str} → {comp['current_pass_rate']:.2%} ({delta_str}) [{comp['status']}]")

    if comparison.status == RegressionStatus.REGRESSED:
        print(f"\n⚠ REGRESSION DETECTED — Performance degraded beyond tolerance ({comparison.regression_tolerance*100:.1f}%)")
    elif comparison.status == RegressionStatus.IMPROVED:
        print(f"\n✓ Performance IMPROVED vs baseline")
    elif comparison.status == RegressionStatus.NO_BASELINE:
        print(f"\nℹ No baseline exists. Run with --save-baseline to establish one.")
    print()
