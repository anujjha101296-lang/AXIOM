"""Tests for SEC experiment kernel, sandbox, and lifecycle."""

from __future__ import annotations

import pytest

from axiom.experiment.executor import execute_experiment
from axiom.experiment.integrity_gate import check_experiment_integrity
from axiom.experiment.models import (
    ExperimentSpec,
    ExperimentStatus,
    ResourceBudget,
    can_transition,
)
from axiom.experiment.parameter_search import generate_parameter_configs
from axiom.experiment.planner import plan_experiments
from axiom.experiment.reproduction import compare_experiment_results
from axiom.experiment.sandbox import execute_sandboxed, static_analyze_code
from axiom.experiment.spec import validate_spec
from axiom.experiment.store import ExperimentStore


@pytest.fixture
def store() -> ExperimentStore:
    return ExperimentStore(":memory:")


def test_lifecycle_transitions():
    assert can_transition(ExperimentStatus.DRAFT, ExperimentStatus.VALIDATED)
    assert can_transition(ExperimentStatus.RUNNING, ExperimentStatus.COMPLETED)
    assert not can_transition(ExperimentStatus.DRAFT, ExperimentStatus.COMPLETED)
    assert not can_transition(ExperimentStatus.ARCHIVED, ExperimentStatus.DRAFT)


def test_validate_spec_requires_fields():
    spec = ExperimentSpec(research_question="", hypothesis="", objective="")
    result = validate_spec(spec)
    assert not result.valid
    assert len(result.errors) >= 3


def test_sandbox_blocks_forbidden_imports():
    issues = static_analyze_code("import os\nos.system('ls')")
    assert issues


def test_sandbox_executes_safe_code():
    result = execute_sandboxed("print(2 + 2)", budget=ResourceBudget(timeout_seconds=5.0))
    assert result.success
    assert "4" in result.stdout


def test_sandbox_timeout():
    result = execute_sandboxed(
        "import time\ntime.sleep(60)",
        budget=ResourceBudget(timeout_seconds=1.0),
    )
    assert not result.success
    assert result.terminated_reason == "timeout" or "timeout" in result.stderr.lower()


def test_create_and_run_experiment(store: ExperimentStore):
    spec = ExperimentSpec(
        research_question="Does n+0=n?",
        hypothesis="Addition identity holds",
        objective="Verify for small n",
        code="for n in range(10):\n    assert n + 0 == n\nprint('OK')",
        random_seed=42,
    )
    experiment = store.create_experiment(spec)
    result = execute_experiment(store, experiment.experiment_id)
    assert result["status"] == "COMPLETED"
    updated = store.get(experiment.experiment_id)
    assert updated is not None
    assert updated.status == ExperimentStatus.COMPLETED
    assert updated.results.get("not_mathematical_proof") is True


def test_failed_experiment_preserved(store: ExperimentStore):
    spec = ExperimentSpec(
        research_question="Test failure",
        hypothesis="Will fail",
        objective="Trigger error",
        code="raise ValueError('expected')",
    )
    experiment = store.create_experiment(spec)
    result = execute_experiment(store, experiment.experiment_id)
    assert result["status"] == "FAILED"
    updated = store.get(experiment.experiment_id)
    assert updated is not None
    assert updated.status == ExperimentStatus.FAILED


def test_integrity_gate_labels_computational_evidence(store: ExperimentStore):
    spec = ExperimentSpec(
        research_question="Q",
        hypothesis="H",
        objective="O",
        code="print(1)",
    )
    experiment = store.create_experiment(spec)
    execute_experiment(store, experiment.experiment_id)
    updated = store.get(experiment.experiment_id)
    gate = check_experiment_integrity(updated)
    assert gate.allowed
    assert "computational" in gate.reason.lower() or "not mathematical" in gate.reason.lower()


def test_parameter_search_records_configs():
    configs = generate_parameter_configs({"x": [1, 2], "y": [3, 4]}, max_configs=10)
    assert len(configs) == 4


def test_plan_discriminates_hypotheses():
    plans = plan_experiments(["H1: primes are infinite", "H2: primes are finite"])
    assert len(plans) >= 2
    assert plans[0]["experiment_type"] == "discriminative"


def test_reproduction_exact_match(store: ExperimentStore):
    spec = ExperimentSpec(
        research_question="Q",
        hypothesis="H",
        objective="O",
        code="print('same')",
        random_seed=1,
    )
    e1 = store.create_experiment(spec)
    e2 = store.create_experiment(spec)
    execute_experiment(store, e1.experiment_id)
    execute_experiment(store, e2.experiment_id)
    a = store.get(e1.experiment_id)
    b = store.get(e2.experiment_id)
    from axiom.experiment.models import ExperimentReproductionStatus
    status, _ = compare_experiment_results(a, b)
    assert status == ExperimentReproductionStatus.EXACT_REPRODUCTION


def test_version_on_transition(store: ExperimentStore):
    spec = ExperimentSpec(research_question="Q", hypothesis="H", objective="O")
    experiment = store.create_experiment(spec)
    assert experiment.version == 1
    updated = store.transition(experiment.experiment_id, ExperimentStatus.VALIDATED)
    assert updated.version == 2
