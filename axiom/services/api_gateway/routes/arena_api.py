"""Research Benchmark Arena API — catalog (no answers), runs, readiness, regression."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.evaluation.arena.runner import get_public_catalog, run_arena
from axiom.evaluation.arena.store import ArenaStore

router = APIRouter(prefix="/arena", tags=["research-benchmark-arena"])


class ArenaRunRequest(BaseModel):
    is_baseline: bool = False
    case_ids: list[str] | None = None
    notes: str = Field(default="", max_length=2000)


@router.get("/manifest")
def arena_manifest() -> dict[str, Any]:
    return {
        "name": "AXIOM Research Benchmark Arena",
        "dataset_version": "arena_v1",
        "principle": "Measured scores only; no fabricated readiness; prose ≠ formal proof",
        "tiers": list(range(0, 11)),
        "ground_truth_exposed": False,
        "millennium_auto_claim": False,
    }


@router.get("/catalog")
def arena_catalog() -> dict[str, Any]:
    """Public catalog — ground-truth answers intentionally omitted."""
    return get_public_catalog()


@router.post("/run")
def arena_run(body: ArenaRunRequest) -> dict[str, Any]:
    return run_arena(
        settings.db_path,
        is_baseline=body.is_baseline,
        case_ids=body.case_ids,
        environment="api",
        notes=body.notes,
    )


@router.get("/runs")
def arena_runs(limit: int = 20) -> dict[str, Any]:
    store = ArenaStore(settings.db_path)
    return {"runs": store.list_runs(limit=limit)}


@router.get("/runs/{run_id}")
def arena_run_detail(run_id: str) -> dict[str, Any]:
    store = ArenaStore(settings.db_path)
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/baseline")
def arena_baseline() -> dict[str, Any]:
    store = ArenaStore(settings.db_path)
    baseline = store.baseline_run()
    if not baseline:
        return {"baseline": None, "notes": "No baseline recorded yet. POST /arena/run with is_baseline=true."}
    return {"baseline": baseline}


@router.get("/readiness")
def arena_readiness() -> dict[str, Any]:
    store = ArenaStore(settings.db_path)
    latest = store.latest_run()
    if not latest:
        return {"readiness": None, "notes": "No arena runs yet."}
    return {
        "run_id": latest.get("run_id"),
        "git_commit": latest.get("git_commit"),
        "readiness": latest.get("readiness"),
        "dimension_scores": latest.get("dimension_scores"),
        "weaknesses": latest.get("weaknesses"),
        "summary": latest.get("summary"),
    }
