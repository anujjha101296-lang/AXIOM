"""Tests for Phase 15 — Self-Improving Research Agent & System Regression Loop."""
import pytest
from axiom.self_improvement.models import RegressionStatus
from axiom.self_improvement.evaluator import SystemEvaluator
from axiom.self_improvement.regression_guard import RegressionGuard
from axiom.self_improvement.loop import SelfImprovementLoop


def test_system_evaluator():
    evaluator = SystemEvaluator()
    evals = evaluator.evaluate_all_phases()

    assert len(evals) == 4  # Phases 11, 12, 13, 14
    assert all(e.pass_rate == 1.0 for e in evals)
    assert all(e.benchmarks_passed == 8 for e in evals)


def test_regression_guard():
    guard = RegressionGuard()
    evaluator = SystemEvaluator()
    evals = evaluator.evaluate_all_phases()

    # Unchanged case
    status, rate = guard.check_regression(baseline_pass_rate=1.0, current_evals=evals)
    assert status == RegressionStatus.UNCHANGED
    assert rate == 1.0

    # Improved case
    status_imp, _ = guard.check_regression(baseline_pass_rate=0.9, current_evals=evals)
    assert status_imp == RegressionStatus.IMPROVED


def test_self_improvement_loop():
    loop = SelfImprovementLoop()
    report = loop.run_cycle(baseline_pass_rate=1.0)

    assert report.baseline_pass_rate == 1.0
    assert report.current_pass_rate == 1.0
    assert report.regression_status == RegressionStatus.UNCHANGED
    assert len(report.phase_summaries) == 4
    assert len(report.recommendations) > 0
