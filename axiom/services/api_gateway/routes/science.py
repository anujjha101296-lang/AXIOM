"""HTTP API for the bounded, deterministic scientific research runtime."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, AsyncIterator
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from axiom.services.api_gateway.auth import verify_token
from axiom.science_runtime.benchmark import run_lorenz_reference_benchmark
from axiom.science_runtime.persistence import ResearchRunStore
from axiom.science_runtime.research_loop import ResearchQuestion, ResearchRun, ResearchStage, run_research

router = APIRouter(prefix="/api/v1/science", tags=["science-runtime"])
_store = ResearchRunStore(os.getenv("AXIOM_RESEARCH_RUN_DIR", "data/research_runs"))
_TERMINAL_STAGES = {ResearchStage.COMPLETED.value, ResearchStage.FAILED.value}


class ResearchRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    model: str = Field(default="lorenz", min_length=1, max_length=64)
    max_experiments: int = Field(default=3, ge=1, le=10)
    allowed_rho: list[float] = Field(
        default_factory=lambda: [20.0, 24.0, 28.0, 32.0, 40.0],
        min_length=1,
        max_length=10,
    )


def _question(payload: ResearchRequest) -> ResearchQuestion:
    if payload.model.lower() != "lorenz":
        raise HTTPException(status_code=422, detail="Only the Lorenz runtime is currently enabled")
    return ResearchQuestion(
        text=payload.question.strip(),
        model=payload.model,
        max_experiments=payload.max_experiments,
        allowed_rho=tuple(payload.allowed_rho),
    )


def _execute_and_persist(question: ResearchQuestion, run_id: str) -> ResearchRun:
    run = run_research(question, event_sink=_store.record_transition, run_id=run_id)
    _store.snapshot(run)
    return run


@router.post("/research", response_model=dict[str, Any])
async def start_bounded_research(
    payload: ResearchRequest,
    token: str = Depends(verify_token),
) -> dict[str, Any]:
    """Execute and persist a bounded deterministic research run synchronously."""
    try:
        run = await run_in_threadpool(_execute_and_persist, _question(payload), f"research-{uuid4().hex[:12]}")
        return run.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Scientific research run failed") from exc


@router.post("/research/async", response_model=dict[str, str], status_code=202)
async def queue_bounded_research(
    payload: ResearchRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token),
) -> dict[str, str]:
    """Queue a run so clients can subscribe to its lifecycle stream immediately."""
    question = _question(payload)
    run_id = f"research-{uuid4().hex[:12]}"
    background_tasks.add_task(_execute_and_persist, question, run_id)
    return {"run_id": run_id, "status": "QUEUED"}


@router.get("/research/{run_id}", response_model=dict[str, Any])
async def get_research_run(run_id: str, token: str = Depends(verify_token)) -> dict[str, Any]:
    """Return the latest snapshot of a research run."""
    path = _store.root / f"{run_id}.snapshot.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Research run not found")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to read research run") from exc


@router.get("/research/{run_id}/events", response_model=list[dict[str, Any]])
async def get_research_events(run_id: str, token: str = Depends(verify_token)) -> list[dict[str, Any]]:
    """Return the append-only event history for a research run."""
    path = _store.root / f"{run_id}.jsonl"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Research run not found")
    return _store.read_events(run_id)


@router.get("/research/{run_id}/events/stream")
async def stream_research_events(run_id: str, token: str = Depends(verify_token)) -> StreamingResponse:
    """Replay new lifecycle events as Server-Sent Events until the run terminates."""
    event_path = _store.root / f"{run_id}.jsonl"
    snapshot_path = _store.root / f"{run_id}.snapshot.json"
    if not event_path.exists() and not snapshot_path.exists():
        raise HTTPException(status_code=404, detail="Research run not found")

    async def event_generator() -> AsyncIterator[str]:
        sequence = 0
        idle_polls = 0
        while idle_polls < 300:
            events = _store.read_events(run_id, after_sequence=sequence)
            for event in events:
                sequence = max(sequence, int(event["sequence"]))
                yield f"id: {event['event_id']}\nevent: research\ndata: {json.dumps(event, sort_keys=True)}\n\n"
                idle_polls = 0
            if snapshot_path.exists():
                try:
                    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                    if snapshot.get("stage") in _TERMINAL_STAGES:
                        yield f"event: complete\ndata: {json.dumps({'run_id': run_id, 'stage': snapshot['stage']})}\n\n"
                        return
                except (OSError, json.JSONDecodeError):
                    pass
            idle_polls += 1
            yield ": keep-alive\n\n"
            await asyncio.sleep(0.25)
        yield f"event: timeout\ndata: {json.dumps({'run_id': run_id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/benchmark/lorenz", response_model=dict[str, Any])
async def lorenz_benchmark(token: str = Depends(verify_token)) -> dict[str, Any]:
    """Run the fixed Lorenz evidence benchmark."""
    try:
        result = await run_in_threadpool(run_lorenz_reference_benchmark, 28.0)
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Lorenz benchmark failed") from exc
