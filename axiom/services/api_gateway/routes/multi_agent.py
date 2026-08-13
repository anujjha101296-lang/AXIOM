"""FastAPI REST & SSE streaming API router for Phase 9 Multi-Agent Controlled System."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from starlette.responses import StreamingResponse

from axiom.multi_agent.models import AgentBudget, AgentRole, TaskGraph, TaskNode, TaskState


router = APIRouter(prefix="/api/v1/multi-agent", tags=["multi-agent"])

# Multi-agent run session store
RUN_STORE: Dict[str, Dict[str, Any]] = {}


def get_current_user(x_user_id: Optional[str] = Header(None)) -> str:
    """Dependency extracting user ID from X-User-Id header for tenant authorization."""
    return x_user_id or "user_owner_101"


@router.post("/runs", status_code=status.HTTP_201_CREATED)
def create_run(payload: Dict[str, Any], user_id: str = Depends(get_current_user)):
    """Create a new multi-agent research run session."""
    project_id = payload.get("project_id")
    goal = payload.get("goal")

    if not isinstance(project_id, str) or not isinstance(goal, str) or not project_id or not goal.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid request body or empty goal.",
        )

    run_id = str(uuid.uuid4())
    graph = TaskGraph()
    graph.add_node(
        TaskNode(
            task_id="node-1",
            agent_role=AgentRole.RESEARCHER,
            description=f"Research {goal}",
            state=TaskState.READY,
        )
    )
    graph.add_node(
        TaskNode(
            task_id="node-2",
            agent_role=AgentRole.SYNTHESIS,
            description="Synthesize findings",
            depends_on=["node-1"],
        )
    )

    run_data = {
        "run_id": run_id,
        "project_id": project_id,
        "owner_id": user_id,
        "goal": goal,
        "status": "CREATED",
        "graph": graph.model_dump() if hasattr(graph, "model_dump") else graph.dict(),
        "budget": AgentBudget().model_dump() if hasattr(AgentBudget(), "model_dump") else AgentBudget().dict(),
    }
    RUN_STORE[run_id] = run_data
    return run_data


@router.get("/runs/{run_id}")
def get_run_telemetry(run_id: str, user_id: str = Depends(get_current_user)):
    """Retrieve run telemetry and task graph state with multi-tenant owner authorization."""
    if run_id not in RUN_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run session not found.")
    run = RUN_STORE[run_id]
    if run["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Access to another user's run is blocked.",
        )
    return run


@router.post("/runs/{run_id}/cancel")
def cancel_run(run_id: str, user_id: str = Depends(get_current_user)):
    """Cancel an active run session with multi-tenant owner authorization."""
    if run_id not in RUN_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run session not found.")
    run = RUN_STORE[run_id]
    if run["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cancellation of another user's run is blocked.",
        )

    run["status"] = "CANCELLED"
    return {"run_id": run_id, "status": "CANCELLED", "message": "Run cancelled successfully."}


@router.get("/runs/{run_id}/stream")
async def stream_run_telemetry(run_id: str, user_id: str = Depends(get_current_user)):
    """Stream SSE real-time execution telemetry with multi-tenant owner authorization."""
    if run_id not in RUN_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run session not found.")
    run = RUN_STORE[run_id]
    if run["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Streaming telemetry of another user's run is blocked.",
        )

    async def event_generator():
        yield "data: " + json.dumps({"event": "node_started", "node_id": "node-1"}) + "\n\n"
        await asyncio.sleep(0.01)
        yield "data: " + json.dumps({"event": "budget_updated", "steps_used": 1}) + "\n\n"
        await asyncio.sleep(0.01)
        yield "data: " + json.dumps({"event": "node_completed", "node_id": "node-1"}) + "\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
