"""HTTP API for the bounded, deterministic scientific research runtime."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from axiom.services.api_gateway.auth import verify_token
from axiom.science_runtime import ResearchQuestion, run_lorenz_reference_benchmark, run_research
from axiom.science_runtime.persistence import ResearchRunStore

router = APIRouter(prefix="/api/v1/science", tags=["science-runtime"])
_store = ResearchRunStore(os.getenv("AXIOM_RESEARCH_RUN_DIR", "data/research_runs"))


class ResearchRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    model: str = Field(default="lorenz", min_length=1, max_length=64)
    max_experiments: int = Field(default=3, ge=1, le=10)
    allowed_rho: list[float] = Field(default_factory=lambda: [20.0, 24.0, 28.0, 32.0, 40.0], min_length=1, max_length=10)


@router.post("/research", response_model=dict[str, Any])
async def start_bounded_research(
    payload: ResearchRequest,
    token: str = Depends(verify_token),
) -> dict[str, Any]:
    """Execute and persist a bounded deterministic research run."""
    if payload.model.lower() != "lorenz":
        raise HTTPException(status_code=422, detail="Only the Lorenz runtime is currently enabled")
    try:
        question = ResearchQuestion(
            text=payload.question.strip(),
            model=payload.model,
            max_experiments=payload.max_experiments,
            allowed_rho=tuple(payload.allowed_rho),
        )
        run = await run_in_threadpool(run_research, question)
        _store.append(run, "RUN_COMPLETED", {"experiment_count": len(run.evidence)})
        _store.snapshot(run)
        return run.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Scientific research run failed") from exc


@router.get("/research/{run_id}", response_model=dict[str, Any])
async def get_research_run(run_id: str, token: str = Depends(verify_token)) -> dict[str, Any]:
    """Return the immutable snapshot of a completed bounded research run."""
    path = _store.root / f"{run_id}.snapshot.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Research run not found")
    try:
        import json
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to read research run") from exc


@router.get("/research/{run_id}/events", response_model=list[dict[str, Any]])
async def get_research_events(run_id: str, token: str = Depends(verify_token)) -> list[dict[str, Any]]:
    """Return the append-only event history for a research run."""
    path = _store.root / f"{run_id}.jsonl"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Research run not found")
    import json
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@router.get("/benchmark/lorenz", response_model=dict[str, Any])
async def lorenz_benchmark(token: str = Depends(verify_token)) -> dict[str, Any]:
    """Run the fixed Lorenz evidence benchmark."""
    try:
        result = await run_in_threadpool(run_lorenz_reference_benchmark, 28.0)
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Lorenz benchmark failed") from exc
