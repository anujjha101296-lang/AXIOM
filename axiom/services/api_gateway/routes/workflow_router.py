"""
AXIOM Workflow Engine — REST API Router
========================================
FastAPI router exposing the Workflow Engine over HTTP.
Mount in api_gateway/main.py with:
    app.include_router(workflow_router)
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from axiom.config import settings
from axiom.scientific_method.engine import SMEBypassError, ScientificMethodEngine
from axiom.workflow import (
    WorkflowEngine, WorkflowStatus, Workflow, WorkflowResult,
    get_engine,
)

logger = logging.getLogger(__name__)
workflow_router = APIRouter(prefix="/workflows", tags=["workflow"])


# ─── Request / Response Models ────────────────────────────────────────────────

class CreateWorkflowRequest(BaseModel):
    objective: str
    domain: str = "research"
    sme_session_id: str
    metadata: dict[str, Any] = {}


class AddTaskRequest(BaseModel):
    title: str
    description: str = ""
    worker_type: str
    inputs: dict[str, Any] = {}
    depends_on: list[str] = []
    max_retries: int = 2
    timeout_s: float = 300.0
    require_approval: bool = False


class ApproveRequest(BaseModel):
    task_id: str


class WorkflowSummary(BaseModel):
    id: str
    objective: str
    domain: str
    status: str
    task_count: int
    completed_tasks: int
    created_at: str


def _summarize(workflow: Workflow) -> WorkflowSummary:
    completed = sum(1 for t in workflow.tasks if t.status.value == "completed")
    return WorkflowSummary(
        id=workflow.id,
        objective=workflow.objective,
        domain=workflow.domain,
        status=workflow.status.value,
        task_count=len(workflow.tasks),
        completed_tasks=completed,
        created_at=workflow.created_at.isoformat(),
    )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@workflow_router.post("", response_model=WorkflowSummary, status_code=201)
async def create_workflow(body: CreateWorkflowRequest):
    """
    Create a new SME-governed workflow.
    Requires a completed SME session (POST /sme/sessions/{id}/run first).
    """
    sme = ScientificMethodEngine(settings.db_path)
    try:
        sme.validate_workflow_gate(
            body.domain, body.sme_session_id, require_completed=True
        )
    except SMEBypassError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    engine = get_engine(settings.db_path)
    metadata = {**body.metadata, "sme_session_id": body.sme_session_id}
    workflow = engine.create_workflow(
        objective=body.objective,
        domain=body.domain,
        metadata=metadata,
    )
    sme.link_workflow(body.sme_session_id, workflow.id)
    return _summarize(workflow)


@workflow_router.get("", response_model=list[WorkflowSummary])
async def list_workflows(
    status: Optional[str] = None,
    limit: int = 50,
):
    """List workflows, optionally filtered by status."""
    engine = get_engine(settings.db_path)
    wf_status = WorkflowStatus(status) if status else None
    workflows = engine.list_workflows(status=wf_status, limit=limit)
    return [_summarize(w) for w in workflows]


@workflow_router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get full workflow state including all tasks."""
    engine = get_engine(settings.db_path)
    workflow = engine.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return workflow.model_dump(mode="json")


@workflow_router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """
    Start executing a workflow.
    Runs in the background; poll GET /workflows/{id} for status.
    """
    engine = get_engine(settings.db_path)
    workflow = engine.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    if workflow.is_terminal():
        raise HTTPException(
            status_code=409,
            detail=f"Workflow is already in terminal state '{workflow.status}'"
        )

    background_tasks.add_task(_run_in_background, engine, workflow_id)
    return {"message": "Workflow execution started", "workflow_id": workflow_id}


async def _run_in_background(engine: WorkflowEngine, workflow_id: str) -> None:
    try:
        await engine.run(workflow_id)
    except Exception as exc:
        logger.exception(f"Background workflow {workflow_id!r} failed: {exc}")


@workflow_router.post("/{workflow_id}/pause")
async def pause_workflow(workflow_id: str):
    """Pause a running workflow (current batch completes, then stops)."""
    engine = get_engine(settings.db_path)
    await engine.pause(workflow_id)
    return {"message": "Pause requested", "workflow_id": workflow_id}


@workflow_router.post("/{workflow_id}/resume")
async def resume_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """Resume a paused workflow from the latest checkpoint."""
    engine = get_engine(settings.db_path)
    workflow = engine.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    background_tasks.add_task(engine.resume, workflow_id)
    return {"message": "Resume requested", "workflow_id": workflow_id}


@workflow_router.post("/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """Cancel a running or paused workflow."""
    engine = get_engine(settings.db_path)
    await engine.cancel(workflow_id)
    return {"message": "Cancellation requested", "workflow_id": workflow_id}


@workflow_router.post("/{workflow_id}/approve")
async def approve_task(workflow_id: str, body: ApproveRequest):
    """Unblock a task that is waiting for human approval."""
    engine = get_engine(settings.db_path)
    await engine.approve(workflow_id, body.task_id)
    return {"message": "Task approved", "task_id": body.task_id}


@workflow_router.get("/{workflow_id}/artifacts")
async def get_artifacts(workflow_id: str):
    """Get all artifacts produced by a workflow."""
    engine = get_engine(settings.db_path)
    artifacts = engine.get_artifacts(workflow_id)
    return [a.model_dump(mode="json") for a in artifacts]


@workflow_router.get("/{workflow_id}/artifacts/{artifact_id}")
async def get_artifact(workflow_id: str, artifact_id: str):
    """Get a specific artifact by ID."""
    engine = get_engine(settings.db_path)
    store = engine.artifact_store
    artifact = store.get(artifact_id)
    if artifact is None or artifact.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found")
    return artifact.model_dump(mode="json")


@workflow_router.get("/{workflow_id}/events")
async def get_events(workflow_id: str):
    """Get the full event log for a workflow."""
    engine = get_engine(settings.db_path)
    events = engine.get_events(workflow_id)
    return [e.model_dump(mode="json") for e in events]


@workflow_router.get("/{workflow_id}/checkpoints")
async def get_checkpoints(workflow_id: str):
    """List all checkpoints for a workflow (for recovery)."""
    engine = get_engine(settings.db_path)
    checkpoints = engine.get_checkpoints(workflow_id)
    return [c.model_dump(mode="json") for c in checkpoints]


@workflow_router.post("/{workflow_id}/replay/{checkpoint_id}")
async def replay_from_checkpoint(
    workflow_id: str, checkpoint_id: str, background_tasks: BackgroundTasks
):
    """Replay a workflow from a specific checkpoint."""
    engine = get_engine(settings.db_path)
    background_tasks.add_task(engine.replay_from_checkpoint, workflow_id, checkpoint_id)
    return {
        "message": "Replay started from checkpoint",
        "workflow_id": workflow_id,
        "checkpoint_id": checkpoint_id,
    }


@workflow_router.get("/workers/list")
async def list_workers():
    """List all registered workers and their capabilities."""
    engine = get_engine(settings.db_path)
    return engine.registry.list_all()
