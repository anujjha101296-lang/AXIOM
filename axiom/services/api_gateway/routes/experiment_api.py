"""SEC Loop — Scientific Experimentation & Compute API."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.experiment.comparison import compare_experiments
from axiom.experiment.counterexample import search_computational_counterexample
from axiom.experiment.discovery import detect_discovery_signals
from axiom.experiment.executor import execute_experiment
from axiom.experiment.integrity_gate import check_experiment_integrity
from axiom.experiment.models import (
    DatasetRecord,
    ExperimentSpec,
    ExperimentStatus,
    ResourceBudget,
    SearchStrategy,
)
from axiom.experiment.parameter_search import generate_parameter_configs
from axiom.experiment.planner import plan_experiments
from axiom.experiment.plugins import get_plugin, list_plugins
from axiom.experiment.reproduction import compare_experiment_results
from axiom.experiment.spec import validate_spec
from axiom.experiment.store import get_experiment_store
from axiom.security.deps import experiment_route_auth

router = APIRouter(
    prefix="/experiments",
    tags=["experiments"],
    dependencies=[Depends(experiment_route_auth)],
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CreateExperimentRequest(BaseModel):
    research_question: str
    hypothesis: str
    objective: str
    code: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    environment_type: str = "python"
    timeout_seconds: float = 30.0
    random_seed: int | None = None
    campaign_id: str | None = None
    claim_id: str | None = None
    hypothesis_id: str | None = None


class PlanRequest(BaseModel):
    hypotheses: list[str]
    budget_usd: float = 1.0


class ParameterSearchRequest(BaseModel):
    experiment_id: str
    param_space: dict[str, list[Any]]
    strategy: str = "grid"
    max_configs: int = 10


class CounterexampleRequest(BaseModel):
    claim: str
    test_code: str
    timeout_seconds: float = 10.0


class DatasetRequest(BaseModel):
    name: str
    version: str
    source: str
    license: str = "unknown"
    content_hash: str | None = None
    schema: dict[str, Any] = Field(default_factory=dict)


@router.post("/")
def create_experiment(body: CreateExperimentRequest) -> dict[str, Any]:
    spec = ExperimentSpec(
        research_question=body.research_question,
        hypothesis=body.hypothesis,
        objective=body.objective,
        code=body.code,
        variables=body.variables,
        inputs=body.inputs,
        resource_budget=ResourceBudget(timeout_seconds=body.timeout_seconds),
        random_seed=body.random_seed,
    )
    validation = validate_spec(spec)
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.errors)

    experiment = get_experiment_store(settings.db_path).create_experiment(
        spec,
        campaign_id=body.campaign_id,
        claim_id=body.claim_id,
        hypothesis_id=body.hypothesis_id,
    )
    return experiment.to_dict()


@router.get("/")
def list_experiments(status: str | None = None, limit: int = 50) -> dict[str, Any]:
    store = get_experiment_store(settings.db_path)
    exp_status = ExperimentStatus(status) if status else None
    experiments = store.list_experiments(status=exp_status, limit=limit)
    return {"count": len(experiments), "experiments": [e.to_dict() for e in experiments]}


@router.post("/plan")
def plan_research_experiments(body: PlanRequest) -> dict[str, Any]:
    plans = plan_experiments(body.hypotheses, budget_usd=body.budget_usd)
    return {"plans": plans}


@router.post("/parameter-search")
def run_parameter_search(body: ParameterSearchRequest) -> dict[str, Any]:
    configs = generate_parameter_configs(
        body.param_space,
        SearchStrategy(body.strategy),
        max_configs=body.max_configs,
    )
    store = get_experiment_store(settings.db_path)
    runs = []
    for config in configs:
        run_id = store.record_parameter_run(body.experiment_id, config, {"status": "recorded"})
        runs.append({"run_id": run_id, "config": config})
    return {"count": len(runs), "runs": runs}


@router.post("/counterexample")
def find_counterexample(body: CounterexampleRequest) -> dict[str, Any]:
    return search_computational_counterexample(
        body.claim,
        body.test_code,
        budget=ResourceBudget(timeout_seconds=body.timeout_seconds),
    )


@router.post("/compare")
def compare_two_experiments(experiment_a: str, experiment_b: str) -> dict[str, Any]:
    store = get_experiment_store(settings.db_path)
    a = store.get(experiment_a)
    b = store.get(experiment_b)
    if not a or not b:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return compare_experiments(a, b)


@router.post("/reproduce")
def reproduce_experiment(original_id: str, reproduction_id: str) -> dict[str, Any]:
    store = get_experiment_store(settings.db_path)
    original = store.get(original_id)
    reproduction = store.get(reproduction_id)
    if not original or not reproduction:
        raise HTTPException(status_code=404, detail="Experiment not found")
    status, diffs = compare_experiment_results(original, reproduction)
    return {"status": status.value, "differences": diffs}


@router.post("/datasets")
def register_dataset(body: DatasetRequest) -> dict[str, Any]:
    record = DatasetRecord(
        dataset_id=f"ds_{uuid.uuid4().hex[:12]}",
        name=body.name,
        version=body.version,
        source=body.source,
        created_at=_utc_now(),
        license=body.license,
        content_hash=body.content_hash,
        schema=body.schema,
    )
    get_experiment_store(settings.db_path).register_dataset(record)
    return record.to_dict()


@router.get("/plugins/list")
def list_domain_plugins() -> dict[str, Any]:
    return {"plugins": list_plugins()}


@router.get("/plugins/{domain_id}")
def get_domain_plugin(domain_id: str) -> dict[str, Any]:
    plugin = get_plugin(domain_id)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {domain_id}")
    return {
        "domain_id": plugin.domain_id,
        "experiment_types": plugin.supported_experiment_types(),
    }


@router.get("/dashboard/summary")
def experiment_dashboard() -> dict[str, Any]:
    return get_experiment_store(settings.db_path).dashboard_stats()


@router.get("/{experiment_id}")
def get_experiment(experiment_id: str) -> dict[str, Any]:
    experiment = get_experiment_store(settings.db_path).get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    return experiment.to_dict()


@router.post("/{experiment_id}/run")
def run_experiment(experiment_id: str) -> dict[str, Any]:
    try:
        return execute_experiment(get_experiment_store(settings.db_path), experiment_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{experiment_id}/transition")
def transition_experiment(experiment_id: str, status: str) -> dict[str, Any]:
    try:
        experiment = get_experiment_store(settings.db_path).transition(
            experiment_id, ExperimentStatus(status)
        )
        return experiment.to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{experiment_id}/integrity")
def check_integrity(experiment_id: str) -> dict[str, Any]:
    experiment = get_experiment_store(settings.db_path).get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    return check_experiment_integrity(experiment).to_dict()


@router.get("/{experiment_id}/signals")
def get_discovery_signals(experiment_id: str) -> dict[str, Any]:
    experiment = get_experiment_store(settings.db_path).get(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    signals = detect_discovery_signals(experiment.results)
    return {"signals": signals, "auto_discovery": False}
