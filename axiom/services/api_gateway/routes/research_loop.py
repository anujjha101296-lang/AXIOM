"""REST API for Autonomous Research Loop v1."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.research_loop.benchmarks import list_benchmarks
from axiom.research_loop.engine import ResearchLoopEngine, get_research_loop_engine
from axiom.research_loop.roles import list_roles
from axiom.research_loop.schema import ResearchRunConfig, ResearchRunStatus, ResearchState
from axiom.services.api_gateway.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research-loop", tags=["research-loop"])

_engine: ResearchLoopEngine | None = None


def get_engine() -> ResearchLoopEngine:
    global _engine
    if _engine is None:
        _engine = ResearchLoopEngine(settings.db_path)
    return _engine


class CreateRunRequest(BaseModel):
    research_question: str = Field(..., min_length=10)
    max_iterations: int = Field(5, ge=1, le=20)
    benchmark_id: Optional[str] = None
    project_id: Optional[str] = None
    require_approval_before_attempt: bool = False
    stop_on_supported_solution: bool = True


class BenchmarkRunRequest(BaseModel):
    benchmark_id: str
    max_iterations: int = Field(5, ge=1, le=20)
    project_id: Optional[str] = None


class RejectHypothesisRequest(BaseModel):
    reason: str = ""


class AddEvidenceRequest(BaseModel):
    source: str
    content: str = Field(..., min_length=1)


class ChangeObjectiveRequest(BaseModel):
    research_question: str = Field(..., min_length=10)


class ApproveIterationRequest(BaseModel):
    iteration: int = Field(..., ge=1)


def _run_background(engine: ResearchLoopEngine, run_id: str) -> None:
    try:
        asyncio.run(engine.run(run_id))
    except Exception as exc:
        logger.exception(f"Background research loop {run_id} failed: {exc}")


@router.get("/roles")
def get_roles(token: str = Depends(verify_token)):
    """List research loop agent roles and their specifications."""
    return [r.__dict__ for r in list_roles()]


@router.get("/benchmarks")
def get_benchmarks(token: str = Depends(verify_token)):
    """List historical benchmark problems (solutions hidden during execution)."""
    return [
        {
            "id": b.id,
            "title": b.title,
            "problem_statement": b.problem_statement,
            "domain": b.domain,
            "difficulty": b.difficulty,
        }
        for b in list_benchmarks()
    ]


@router.post("/runs", status_code=201)
def create_run(
    body: CreateRunRequest,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    config = ResearchRunConfig(
        max_iterations=body.max_iterations,
        benchmark_id=body.benchmark_id,
        project_id=body.project_id,
        require_approval_before_attempt=body.require_approval_before_attempt,
        stop_on_supported_solution=body.stop_on_supported_solution,
    )
    state = engine.create_run(body.research_question, config)
    return state.model_dump(mode="json")


@router.post("/benchmarks/run", status_code=201)
def create_benchmark_run(
    body: BenchmarkRunRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    config = ResearchRunConfig(
        max_iterations=body.max_iterations,
        project_id=body.project_id,
    )
    try:
        state = engine.create_benchmark_run(body.benchmark_id, config)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    background_tasks.add_task(_run_background, engine, state.run_id)
    return {"run_id": state.run_id, "status": "started", "benchmark_id": body.benchmark_id}


@router.get("/runs")
def list_runs(
    limit: int = 50,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    return engine.list_runs(limit)


@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    state = engine.get_state(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    row = engine.store.get_run_row(run_id)
    return {
        "state": state.model_dump(mode="json"),
        "status": row["status"] if row else "unknown",
        "created_at": row["created_at"] if row else None,
        "completed_at": row["completed_at"] if row else None,
    }


@router.post("/runs/{run_id}/start")
def start_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    if not engine.get_state(run_id):
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    background_tasks.add_task(_run_background, engine, run_id)
    return {"run_id": run_id, "status": "started"}


@router.post("/runs/{run_id}/pause")
async def pause_run(
    run_id: str,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    await engine.pause(run_id)
    return {"run_id": run_id, "status": "pause_requested"}


@router.post("/runs/{run_id}/resume")
def resume_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    background_tasks.add_task(_run_background, engine, run_id)
    return {"run_id": run_id, "status": "resume_requested"}


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    run_id: str,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    await engine.cancel(run_id)
    return {"run_id": run_id, "status": "cancelled"}


@router.post("/runs/{run_id}/approve")
def approve_iteration(
    run_id: str,
    body: ApproveIterationRequest,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    engine.approve_iteration(run_id, body.iteration)
    return {"run_id": run_id, "iteration": body.iteration, "approved": True}


@router.post("/runs/{run_id}/hypotheses/{hypothesis_id}/reject")
def reject_hypothesis(
    run_id: str,
    hypothesis_id: str,
    body: RejectHypothesisRequest,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    try:
        state = engine.reject_hypothesis(run_id, hypothesis_id, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return state.model_dump(mode="json")


@router.post("/runs/{run_id}/evidence")
def add_evidence(
    run_id: str,
    body: AddEvidenceRequest,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    try:
        state = engine.add_evidence(run_id, body.source, body.content)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return state.model_dump(mode="json")


@router.put("/runs/{run_id}/objective")
def change_objective(
    run_id: str,
    body: ChangeObjectiveRequest,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    try:
        state = engine.change_objective(run_id, body.research_question)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return state.model_dump(mode="json")


@router.get("/runs/{run_id}/events")
def get_run_events(
    run_id: str,
    token: str = Depends(verify_token),
    engine: ResearchLoopEngine = Depends(get_engine),
):
    events = engine.get_events(run_id)
    return [e.model_dump(mode="json") for e in events]
