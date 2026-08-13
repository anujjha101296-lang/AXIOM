"""
AXIOM Phase 8 — Evaluation Framework Tests

Tests for the evaluation domain model, benchmark infrastructure,
and regression detection logic.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.eval_models import (
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkSuite,
    EvaluationResult,
    EvaluationRun,
    Metric,
    CapabilityClaim,
    CapabilityStatus,
    RegressionComparison,
    RegressionStatus,
)
from benchmarks.retrieval_benchmark import (
    run_retrieval_benchmark,
    retrieve,
    _build_index,
    _hit_at_k,
    _recall_at_k,
    _reciprocal_rank,
)
from benchmarks.grounding_benchmark import run_grounding_benchmark
from benchmarks.agent_benchmark import (
    run_agent_benchmark,
    _simulate_agent_task,
    _evaluate_task,
    _validate_state_transitions,
    ALLOWLISTED_TOOLS,
)
from benchmarks.regression import compare_runs, save_baseline, load_baseline
from benchmarks.capability_claims import build_initial_claims, update_claims_from_run


# ── Evaluation Model Tests ────────────────────────────────────────────────────

class TestMetric:
    def test_metric_passes_when_above_threshold(self):
        m = Metric("Hit@1", 0.8, threshold=0.6)
        assert m.passed is True

    def test_metric_fails_when_below_threshold(self):
        m = Metric("Hit@1", 0.4, threshold=0.6)
        assert m.passed is False

    def test_metric_no_threshold(self):
        m = Metric("duration", 1.23)
        assert m.passed is None

    def test_metric_serialization(self):
        m = Metric("Hit@1", 0.8, threshold=0.6)
        d = m.to_dict()
        assert d["name"] == "Hit@1"
        assert d["value"] == 0.8
        assert d["passed"] is True


class TestEvaluationResult:
    def _make_result(self, status: BenchmarkStatus) -> BenchmarkResult:
        return BenchmarkResult(case_id="test", status=status)

    def test_pass_rate_all_pass(self):
        er = EvaluationResult("s1", "Suite 1", results=[
            self._make_result(BenchmarkStatus.PASSED),
            self._make_result(BenchmarkStatus.PASSED),
        ])
        assert er.pass_rate == 1.0

    def test_pass_rate_mixed(self):
        er = EvaluationResult("s1", "Suite 1", results=[
            self._make_result(BenchmarkStatus.PASSED),
            self._make_result(BenchmarkStatus.FAILED),
        ])
        assert er.pass_rate == 0.5

    def test_pass_rate_empty(self):
        er = EvaluationResult("s1", "Suite 1")
        assert er.pass_rate == 0.0

    def test_serialization(self):
        er = EvaluationResult("s1", "Suite 1", results=[
            self._make_result(BenchmarkStatus.PASSED),
        ])
        d = er.to_dict()
        assert d["summary"]["total_cases"] == 1
        assert d["summary"]["pass_rate"] == 1.0


class TestEvaluationRun:
    def test_overall_pass_rate(self):
        r1 = EvaluationResult("s1", "Suite 1", results=[
            BenchmarkResult("c1", BenchmarkStatus.PASSED),
            BenchmarkResult("c2", BenchmarkStatus.PASSED),
        ])
        r2 = EvaluationResult("s2", "Suite 2", results=[
            BenchmarkResult("c3", BenchmarkStatus.FAILED),
            BenchmarkResult("c4", BenchmarkStatus.PASSED),
        ])
        run = EvaluationRun(suite_results=[r1, r2])
        assert run.overall_pass_rate == 0.75

    def test_save_and_load(self):
        run = EvaluationRun(git_commit="abc1234", git_branch="main")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            run.save(path)
            loaded = EvaluationRun.load(path)
            assert loaded.run_id == run.run_id
            assert loaded.git_commit == "abc1234"
        finally:
            os.unlink(path)


class TestCapabilityClaim:
    def test_initial_claims_are_unmeasured(self):
        claims = build_initial_claims()
        for claim in claims:
            assert claim.status in (CapabilityStatus.UNMEASURED, CapabilityStatus.PARTIALLY_MEASURED)

    def test_claims_have_limitations(self):
        claims = build_initial_claims()
        for claim in claims:
            assert len(claim.limitations) > 0, f"Claim {claim.capability_id} has no limitations"

    def test_claims_serialization(self):
        claims = build_initial_claims()
        for claim in claims:
            d = claim.to_dict()
            assert "capability_id" in d
            assert "limitations" in d
            assert "status" in d


# ── Retrieval Benchmark Tests ─────────────────────────────────────────────────

class TestRetrievalMetrics:
    def test_hit_at_k_found(self):
        assert _hit_at_k(["a", "b", "c"], ["b"], k=3) == 1.0

    def test_hit_at_k_not_found(self):
        assert _hit_at_k(["a", "b", "c"], ["d"], k=3) == 0.0

    def test_hit_at_k_boundary(self):
        assert _hit_at_k(["a", "b", "c"], ["c"], k=2) == 0.0
        assert _hit_at_k(["a", "b", "c"], ["c"], k=3) == 1.0

    def test_recall_at_k(self):
        assert _recall_at_k(["a", "b", "c"], ["a", "b"], k=3) == 1.0
        assert _recall_at_k(["a", "b", "c"], ["a", "b", "d"], k=3) == pytest.approx(2/3)

    def test_recall_at_k_empty_relevant(self):
        assert _recall_at_k(["a", "b"], [], k=5) == 1.0

    def test_mrr_first_position(self):
        assert _reciprocal_rank(["a", "b", "c"], ["a"]) == 1.0

    def test_mrr_second_position(self):
        assert _reciprocal_rank(["a", "b", "c"], ["b"]) == pytest.approx(0.5)

    def test_mrr_not_found(self):
        assert _reciprocal_rank(["a", "b", "c"], ["d"]) == 0.0


class TestRetrievalBenchmark:
    def test_benchmark_runs_successfully(self):
        result = run_retrieval_benchmark()
        assert result.suite_id == "retrieval_benchmark"
        assert result.total_cases == 5  # 5 queries in corpus
        assert result.duration_seconds > 0

    def test_benchmark_has_aggregate_metrics(self):
        result = run_retrieval_benchmark()
        metric_names = {m.name for m in result.aggregate_metrics}
        assert "Mean Hit@1" in metric_names
        assert "MRR" in metric_names

    def test_retrieval_is_deterministic(self):
        """Running same benchmark twice gives same results."""
        result1 = run_retrieval_benchmark()
        result2 = run_retrieval_benchmark()
        for r1, r2 in zip(result1.results, result2.results):
            assert r1.case_id == r2.case_id
            assert r1.status == r2.status

    def test_tfidf_retrieval_finds_relevant_chunks(self):
        """TF-IDF retrieval should find the most relevant chunk for a known query."""
        import json
        corpus_path = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "data", "retrieval_corpus.json")
        with open(corpus_path) as f:
            corpus = json.load(f)
        chunks, idf = _build_index(corpus)
        ranked = retrieve("supervised learning labeled data", chunks, idf, top_k=3)
        top_id = ranked[0][0]
        assert top_id == "doc_A_c0", f"Expected doc_A_c0, got {top_id}"


# ── Grounding Benchmark Tests ─────────────────────────────────────────────────

class TestGroundingBenchmark:
    def test_benchmark_runs_successfully(self):
        result = run_grounding_benchmark()
        assert result.suite_id == "grounding_benchmark"
        assert result.total_cases == 5

    def test_no_evidence_case_expresses_uncertainty(self):
        result = run_grounding_benchmark()
        no_evidence = next(r for r in result.results if r.case_id == "gc_003")
        assert no_evidence.actual_outputs["insufficient_evidence_stated"] is True

    def test_benchmark_has_citation_metrics(self):
        result = run_grounding_benchmark()
        metric_names = {m.name for m in result.aggregate_metrics}
        assert "Mean Citation Validity Rate" in metric_names


# ── Agent Benchmark Tests ─────────────────────────────────────────────────────

class TestStateMachineValidation:
    def test_valid_simple_path(self):
        valid, msg = _validate_state_transitions(["CREATED", "PLANNING", "RETRIEVING", "ANALYZING", "COMPLETED"])
        assert valid is True

    def test_invalid_transition(self):
        valid, msg = _validate_state_transitions(["CREATED", "COMPLETED"])
        assert valid is False

    def test_wrong_start_state(self):
        valid, msg = _validate_state_transitions(["PLANNING", "RETRIEVING", "COMPLETED"])
        assert valid is False

    def test_empty_transitions(self):
        valid, msg = _validate_state_transitions([])
        assert valid is False

    def test_valid_cancelled_path(self):
        valid, msg = _validate_state_transitions(["CREATED", "PLANNING", "CANCELLED"])
        assert valid is True


class TestAgentToolAllowlist:
    def test_allowlisted_tools(self):
        assert "SEARCH_PROJECT_KNOWLEDGE" in ALLOWLISTED_TOOLS
        assert "READ_DOCUMENT_EVIDENCE" in ALLOWLISTED_TOOLS
        assert "ASK_GROUNDED_RESEARCH_ENGINE" in ALLOWLISTED_TOOLS

    def test_unlisted_tools_rejected(self):
        assert "EXECUTE_SHELL" not in ALLOWLISTED_TOOLS
        assert "BROWSE_WEB" not in ALLOWLISTED_TOOLS
        assert "MODIFY_FILE" not in ALLOWLISTED_TOOLS


class TestAgentBenchmark:
    def test_benchmark_runs_successfully(self):
        result = run_agent_benchmark()
        assert result.suite_id == "agent_benchmark"
        assert result.total_cases == 7

    def test_simple_task_completes(self):
        result = run_agent_benchmark()
        simple_task = next(r for r in result.results if r.case_id == "at_001")
        assert simple_task.actual_outputs["final_state"] == "COMPLETED"

    def test_budget_exhaustion_stops(self):
        result = run_agent_benchmark()
        budget_task = next(r for r in result.results if r.case_id == "at_006")
        assert budget_task.actual_outputs["final_state"] == "FAILED"
        # The task correctly stops when budget is exhausted (stops_at_budget check passes)
        assert budget_task.actual_outputs["checks"].get("stops_at_budget") is True

    def test_cancellation_persists_state(self):
        result = run_agent_benchmark()
        cancel_task = next(r for r in result.results if r.case_id == "at_007")
        assert cancel_task.actual_outputs["final_state"] == "CANCELLED"

    def test_unsupported_question_expresses_uncertainty(self):
        result = run_agent_benchmark()
        unsupported = next(r for r in result.results if r.case_id == "at_003")
        assert unsupported.actual_outputs["insufficient_evidence_expressed"] is True

    def test_all_state_transitions_valid(self):
        result = run_agent_benchmark()
        for task_result in result.results:
            transitions = task_result.actual_outputs.get("states_visited", [])
            valid, msg = _validate_state_transitions(transitions)
            assert valid, f"Task {task_result.case_id}: {msg}"

    def test_budget_never_exceeded(self):
        """Agent must NEVER exceed budget limits."""
        import json
        tasks_path = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "data", "agent_tasks.json")
        with open(tasks_path) as f:
            tasks = json.load(f)["tasks"]

        for task in tasks:
            execution = _simulate_agent_task(task)
            budget = task.get("budget", {})
            max_steps = budget.get("max_steps", 10)
            max_tools = budget.get("max_tool_calls", 10)
            assert execution["step_count"] <= max_steps, \
                f"Task {task['task_id']} exceeded max_steps: {execution['step_count']} > {max_steps}"
            assert execution["tool_call_count"] <= max_tools, \
                f"Task {task['task_id']} exceeded max_tool_calls: {execution['tool_call_count']} > {max_tools}"


# ── Regression Tests ──────────────────────────────────────────────────────────

class TestRegression:
    def _make_run(self, pass_rate: float) -> EvaluationRun:
        results = []
        n = 10
        passed = int(pass_rate * n)
        for i in range(n):
            status = BenchmarkStatus.PASSED if i < passed else BenchmarkStatus.FAILED
            results.append(BenchmarkResult(f"c{i}", status))
        suite = EvaluationResult("test_suite", "Test Suite", results=results)
        return EvaluationRun(suite_results=[suite])

    def test_no_baseline(self):
        run = self._make_run(0.8)
        comparison = compare_runs(run, None)
        assert comparison.status == RegressionStatus.NO_BASELINE

    def test_improved_detection(self):
        baseline_run = self._make_run(0.5)
        current_run = self._make_run(0.9)
        comparison = compare_runs(current_run, baseline_run.to_dict(), tolerance=0.05)
        assert comparison.status == RegressionStatus.IMPROVED

    def test_regression_detection(self):
        baseline_run = self._make_run(0.9)
        current_run = self._make_run(0.5)
        comparison = compare_runs(current_run, baseline_run.to_dict(), tolerance=0.05)
        assert comparison.status == RegressionStatus.REGRESSED

    def test_unchanged_within_tolerance(self):
        baseline_run = self._make_run(0.8)
        current_run = self._make_run(0.82)  # Within 5% tolerance
        comparison = compare_runs(current_run, baseline_run.to_dict(), tolerance=0.05)
        assert comparison.status == RegressionStatus.UNCHANGED

    def test_save_and_load_baseline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "baseline.json")
            run = self._make_run(0.8)
            save_baseline(run, path)
            loaded = load_baseline(path)
            assert loaded is not None
            assert loaded["run_id"] == run.run_id

    def test_no_baseline_file(self):
        loaded = load_baseline("/tmp/nonexistent_axiom_baseline_xyz.json")
        assert loaded is None
