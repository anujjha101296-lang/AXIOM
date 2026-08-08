"""Research Validation Program API routes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.research_validation.dashboard import build_dashboard
from axiom.research_validation.dataset import dataset_stats
from axiom.research_validation.engine import ResearchValidationEngine
from axiom.research_validation.models import ResearchRunConfig
from axiom.research_validation.reports import write_all_reports
from axiom.research_validation.reproducibility import config_hash

router = APIRouter(prefix="/rvp", tags=["research-validation"])


class RunValidationRequest(BaseModel):
    stage: int = Field(0, ge=0, le=6)
    problem_ids: list[str] = Field(default_factory=list)
    seed: int = 42
    max_attempts: int = 3
    limit: int = Field(10, ge=1, le=100)


def _engine() -> ResearchValidationEngine:
    return ResearchValidationEngine(settings.db_path)


@router.get("/stages")
def list_stages() -> list[dict[str, Any]]:
    return _engine().list_stages()


@router.get("/problems")
def list_problems(stage: int | None = None, limit: int = 100) -> dict[str, Any]:
    return {
        "problems": _engine().list_problems(stage=stage, limit=limit),
        "dataset": dataset_stats(),
    }


@router.get("/dashboard")
def get_dashboard() -> dict[str, Any]:
    engine = _engine()
    return build_dashboard(engine.store)


@router.post("/runs")
def start_validation_run(body: RunValidationRequest) -> dict[str, Any]:
    engine = _engine()
    problem_ids = body.problem_ids
    if not problem_ids:
        problem_ids = [p["id"] for p in engine.list_problems(stage=body.stage, limit=body.limit)]
    if not problem_ids:
        raise HTTPException(status_code=400, detail="No problems found for stage")

    config = ResearchRunConfig(
        stage=body.stage,
        problem_ids=problem_ids,
        seed=body.seed,
        max_attempts=body.max_attempts,
    )
    results = engine.run_validation(config)
    return {
        "config_hash": config_hash(config),
        "run_count": len(results),
        "runs": [r.to_dict() for r in results],
    }


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    result = _engine().store.get_run(run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Run not found")
    return result


@router.post("/runs/replay")
def replay_validation(body: RunValidationRequest) -> dict[str, Any]:
    engine = _engine()
    config = ResearchRunConfig(
        stage=body.stage,
        problem_ids=body.problem_ids,
        seed=body.seed,
        max_attempts=body.max_attempts,
    )
    results = engine.replay(config)
    return {
        "config_hash": config_hash(config),
        "replayed": len(results),
        "runs": [r.to_dict() for r in results],
    }


@router.post("/reports/generate")
def generate_reports() -> dict[str, str]:
    written = write_all_reports(Path("."), settings.db_path)
    return {name: str(path) for name, path in written.items()}
