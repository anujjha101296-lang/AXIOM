"""Regression Guard for Phase 15.

Detects regressions in pass rates between current run and baseline.
"""
from typing import List, Tuple
from axiom.self_improvement.models import PhaseBenchmarkResult, RegressionStatus


class RegressionGuard:
    """Monitors pass rates and flags regressions."""

    def check_regression(
        self,
        baseline_pass_rate: float,
        current_evals: List[PhaseBenchmarkResult],
    ) -> Tuple[RegressionStatus, float]:
        """Compare current pass rate against baseline."""
        total_benchmarks = sum(e.benchmarks_total for e in current_evals)
        total_passed = sum(e.benchmarks_passed for e in current_evals)
        current_rate = total_passed / max(1, total_benchmarks)

        if current_rate > baseline_pass_rate:
            status = RegressionStatus.IMPROVED
        elif current_rate == baseline_pass_rate:
            status = RegressionStatus.UNCHANGED
        else:
            status = RegressionStatus.REGRESSED

        return status, round(current_rate, 4)
