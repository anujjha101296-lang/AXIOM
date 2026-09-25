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
from axiom.science_runtime.postgres_persistence import PostgresResearchRunStore
from axiom.science_runtime.replay import replay_research_events, verify_snapshot_against_replay
from axiom.science_runtime.research_loop import (
    ResearchQuestion,
    ResearchRun,
    ResearchStage,
    Transition,
    run_research,
)

router = APIRouter(prefix="/api/v1/science", tags=["science-runtime"])


def _build_store() -> ResearchRunStore | PostgresResearchRunStore:
    """Select durable SQL storage when AXIOM_DATABASE_URL is configured.

    Local file persistence remains the explicit development/test fallback. The
    API never writes to both stores for one run, preventing split-brain state.
    """
    database_url = os.getenv("AXIOM_DATABASE_URL") or os.getenv("DATABASE_URL")
    environment = os.getenv("AXIOM_ENVIRONMENT") or os.getenv("ENVIRONMENT") or "development"
    if database_url:
        store = PostgresResearchRunStore(database_url, create_schema=False)
        if environment.lower() in {"production", "prod"}:
            store.check_ready()
        return store
    if environment.lower() in {"production", "prod"}:
        raise RuntimeError(
            "Durable scientific persistence is required in production. "
            "Set AXIOM_DATABASE_URL or DATABASE_URL."
        )
    return ResearchRunStore(os.getenv("AXIOM_RESEARCH_RUN_DIR", "data/research_runs"))


_store = _build_store()
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


def _persist_transition(run: ResearchRun, transition: Transition) -> None:
    """Persist every lifecycle transition before the next transition occurs."""
    run.metadata["persistence"] = {
        "backend": "postgresql" if isinstance(_store, PostgresResearchRunStore) else "local_test",
        "system_of_record": "database" if isinstance(_store, PostgresResearchRunStore) else "filesystem",
        "event_schema": "axiom.research.event.v1",
        "durable": isinstance(_store, PostgresResearchRunStore),
    }
    if isinstance(_store, PostgresResearchRunStore):
        _store.persist_transition(run, transition)
    else:
        _store.record_transition(run, transition)
        _store.snapshot(run)


def _initialize_queued_run(question: ResearchQuestion, run_id: str) -> None:
    """Create durable initial state before scheduling background execution.

    This closes the async API race where a client could receive a run_id and
    immediately subscribe before the worker had emitted its first transition.
    """
    run = ResearchRun(run_id=run_id, question=question)
    _persist_transition(
        run,
        Transition(
            ResearchStage.PLANNED.value,
            "run_queued",
            "Bounded research run accepted and queued for execution.",
        ),
    )


def _execute_and_persist(question: ResearchQuestion, run_id: str) -> ResearchRun:
    return run_research(question, event_sink=_persist_transition, run_id=run_id)


def _read_snapshot(run_id: str) -> dict[str, Any] | None:
    if isinstance(_store, PostgresResearchRunStore):
        return _store.read_snapshot(run_id)
    path = _store.root / f"{run_id}.snapshot.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_events(run_id: str, after_sequence: int = 0) -> list[dict[str, Any]]:
    if isinstance(_store, PostgresResearchRunStore):
        return _store.read_events(run_id, after_sequence=after_sequence)
    return _store.read_events(run_id, after_sequence=after_sequence)


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
    try:
        _initialize_queued_run(question, run_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Durable research queue is unavailable") from exc
    background_tasks.add_task(_execute_and_persist, question, run_id)
    return {"run_id": run_id, "status": "QUEUED"}


@router.get("/research/{run_id}", response_model=dict[str, Any])
async def get_research_run(run_id: str, token: str = Depends(verify_token)) -> dict[str, Any]:
    """Return the latest durable snapshot of a research run."""
    try:
        snapshot = _read_snapshot(run_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to read research run") from exc
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Research run not found")
    return snapshot


@router.get("/research/{run_id}/events", response_model=list[dict[str, Any]])
async def get_research_events(run_id: str, token: str = Depends(verify_token)) -> list[dict[str, Any]]:
    """Return the append-only event history for a research run."""
    if _read_snapshot(run_id) is None:
        raise HTTPException(status_code=404, detail="Research run not found")
    return _read_events(run_id)


@router.get("/research/{run_id}/replay", response_model=dict[str, Any])
async def replay_research_run(run_id: str, token: str = Depends(verify_token)) -> dict[str, Any]:
    """Rebuild the lifecycle projection from durable events and verify the snapshot."""
    snapshot = _read_snapshot(run_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Research run not found")
    events = _read_events(run_id)
    try:
        replay = replay_research_events(events)
        verify_snapshot_against_replay(snapshot, replay)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Research run replay integrity check failed") from exc
    return replay.to_dict()


@router.get("/research/{run_id}/events/stream")
async def stream_research_events(run_id: str, token: str = Depends(verify_token)) -> StreamingResponse:
    """Replay new lifecycle events as Server-Sent Events until the run terminates."""
    if _read_snapshot(run_id) is None:
        raise HTTPException(status_code=404, detail="Research run not found")

    async def event_generator() -> AsyncIterator[str]:
        sequence = 0
        idle_polls = 0
        while idle_polls < 300:
            events = _read_events(run_id, after_sequence=sequence)
            for event in events:
                sequence = max(sequence, int(event["sequence"]))
                yield f"id: {event['event_id']}\nevent: research\ndata: {json.dumps(event, sort_keys=True)}\n\n"
                idle_polls = 0
            snapshot = _read_snapshot(run_id)
            if snapshot and snapshot.get("stage") in _TERMINAL_STAGES:
                yield f"event: complete\ndata: {json.dumps({'run_id': run_id, 'stage': snapshot['stage']})}\n\n"
                return
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
