"""Self-Improvement Loop Orchestrator for Phase 15."""
import json, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from axiom.self_improvement.models import SelfImprovementReport, RegressionStatus
from axiom.self_improvement.evaluator import SystemEvaluator
from axiom.self_improvement.regression_guard import RegressionGuard


class SelfImprovementLoop:
    """Orchestrates system evaluation, regression guarding, and learning reporting."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.evaluator = SystemEvaluator()
        self.guard = RegressionGuard()
        self.output_dir = output_dir or (Path(__file__).parent.parent.parent / "evaluation_results" / "phase15")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_cycle(self, baseline_pass_rate: float = 1.0) -> SelfImprovementReport:
        """Run evaluation across all phases and generate self-improvement report."""
        evals = self.evaluator.evaluate_all_phases()
        status, current_rate = self.guard.check_regression(baseline_pass_rate, evals)

        recommendations = []
        if status == RegressionStatus.REGRESSED:
            recommendations.append("Revert recent changes or fix failing benchmark targets.")
        elif status == RegressionStatus.IMPROVED:
            recommendations.append("Update system baseline to lock in capability gains.")
        else:
            recommendations.append("System stable: Maintain test coverage and benchmark parity.")

        report = SelfImprovementReport(
            baseline_pass_rate=baseline_pass_rate,
            current_pass_rate=current_rate,
            regression_status=status,
            phase_summaries=evals,
            recommendations=recommendations,
        )

        out_file = self.output_dir / f"self_improvement_{int(time.time())}.json"
        out_file.write_text(json.dumps(report.model_dump(), indent=2))

        return report
