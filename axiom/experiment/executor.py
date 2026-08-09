"""Experiment executor — sandboxed execution (SEC §8–11)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.experiment.environment import capture_environment
from axiom.experiment.models import (
    ExperimentFailure,
    ExperimentStatus,
)
from axiom.experiment.sandbox import execute_sandboxed, static_analyze_code
from axiom.experiment.spec import spec_from_dict, validate_spec
from axiom.experiment.store import ExperimentStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def execute_experiment(store: ExperimentStore, experiment_id: str) -> dict[str, Any]:
    """Run experiment through full lifecycle with sandboxed execution."""
    experiment = store.get(experiment_id)
    if not experiment:
        raise KeyError(f"Experiment not found: {experiment_id}")

    spec = spec_from_dict(experiment.spec)

    validation = validate_spec(spec)
    if not validation.valid:
        store.transition(experiment_id, ExperimentStatus.FAILED)
        failure = ExperimentFailure(
            failure_id=f"fail_{uuid.uuid4().hex[:12]}",
            experiment_id=experiment_id,
            failure_type="validation_error",
            error="; ".join(validation.errors),
            created_at=_utc_now(),
        )
        store.save_failure(failure)
        return {"status": "FAILED", "errors": validation.errors}

    if experiment.status == ExperimentStatus.DRAFT:
        store.transition(experiment_id, ExperimentStatus.VALIDATED)
    store.transition(experiment_id, ExperimentStatus.QUEUED)
    store.transition(experiment_id, ExperimentStatus.RUNNING)

    env = capture_environment(spec.environment_type.value)
    results: dict[str, Any] = {"environment": env}

    if spec.code:
        analysis = static_analyze_code(spec.code)
        if analysis:
            store.transition(experiment_id, ExperimentStatus.FAILED)
            failure = ExperimentFailure(
                failure_id=f"fail_{uuid.uuid4().hex[:12]}",
                experiment_id=experiment_id,
                failure_type="static_analysis",
                error="; ".join(analysis),
                created_at=_utc_now(),
                configuration=spec.to_dict(),
                environment=env,
            )
            store.save_failure(failure)
            return {"status": "FAILED", "static_analysis": analysis}

        sandbox_result = execute_sandboxed(
            spec.code,
            budget=spec.resource_budget,
            seed=spec.random_seed,
        )
        results["sandbox"] = sandbox_result.to_dict()
        results["evidence_class"] = "computational_evidence"
        results["not_mathematical_proof"] = True
        results["not_scientific_fact"] = True

        if not sandbox_result.success:
            store.transition(experiment_id, ExperimentStatus.FAILED)
            failure = ExperimentFailure(
                failure_id=f"fail_{uuid.uuid4().hex[:12]}",
                experiment_id=experiment_id,
                failure_type=sandbox_result.terminated_reason or "execution_error",
                error=sandbox_result.stderr,
                created_at=_utc_now(),
                configuration=spec.to_dict(),
                environment=env,
                root_cause=sandbox_result.terminated_reason or "runtime_error",
            )
            store.save_failure(failure)
            return {"status": "FAILED", "sandbox": sandbox_result.to_dict()}

    store.update_results(experiment_id, results, environment=env)
    store.transition(experiment_id, ExperimentStatus.COMPLETED)
    return {"status": "COMPLETED", "results": results}
