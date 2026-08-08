"""Scientific Method Engine API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.scientific_method.engine import (
    SMEBypassError,
    SMEPhaseIncompleteError,
    ScientificMethodEngine,
)
from axiom.scientific_method.models import PHASE_ORDER, ProblemDefinition, SMEPhase

router = APIRouter(prefix="/sme", tags=["scientific-method"])


class CreateSessionRequest(BaseModel):
    objective: str
    domain: str = "research"
    research_question: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    workflow_id: str | None = None


class ExecutePhaseRequest(BaseModel):
    phase: SMEPhase | None = None


def _engine() -> ScientificMethodEngine:
    return ScientificMethodEngine(settings.db_path)


@router.get("/phases")
def list_phases() -> list[dict[str, Any]]:
    """Return the mandatory 10-phase scientific method workflow."""
    return [
        {"order": i + 1, "phase": p.value, "name": p.name}
        for i, p in enumerate(PHASE_ORDER)
    ]


@router.post("/sessions", status_code=201)
def create_session(body: CreateSessionRequest) -> dict[str, Any]:
    """Create a new SME-governed research session."""
    problem = None
    if body.research_question or body.assumptions or body.success_criteria:
        problem = ProblemDefinition(
            research_question=body.research_question or body.objective,
            assumptions=body.assumptions,
            success_criteria=body.success_criteria,
            constraints=body.constraints,
        )

    session = _engine().create_session(
        objective=body.objective,
        domain=body.domain,
        problem=problem,
        workflow_id=body.workflow_id,
    )
    return session.model_dump(mode="json")


@router.get("/sessions")
def list_sessions(limit: int = 50, status: str | None = None) -> dict[str, Any]:
    sessions = _engine().store.list_sessions(limit=limit, status=status)
    return {"count": len(sessions), "sessions": [s.model_dump(mode="json") for s in sessions]}


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    session = _engine().get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SME session not found")
    return session.model_dump(mode="json")


@router.post("/sessions/{session_id}/phases")
def execute_phase(session_id: str, body: ExecutePhaseRequest | None = None) -> dict[str, Any]:
    """Execute the next (or specified) SME phase."""
    try:
        session = _engine().execute_phase(
            session_id,
            body.phase if body else None,
        )
        return session.model_dump(mode="json")
    except SMEPhaseIncompleteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/run")
def run_full_cycle(session_id: str) -> dict[str, Any]:
    """Execute all 10 SME phases in order. Required before workflow execution."""
    try:
        session = _engine().run_full_cycle(session_id)
        return session.model_dump(mode="json")
    except SMEPhaseIncompleteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/notebook")
def get_research_notebook(session_id: str) -> dict[str, Any]:
    session = _engine().get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SME session not found")
    if not session.human_review:
        raise HTTPException(
            status_code=404,
            detail="Human review not generated. Run full cycle first.",
        )
    return session.human_review.model_dump(mode="json")


@router.post("/validate-gate")
def validate_gate(domain: str, sme_session_id: str, require_completed: bool = False) -> dict[str, Any]:
    """Validate that a workflow has a valid SME session (mandatory gate check)."""
    try:
        session = _engine().validate_workflow_gate(
            domain, sme_session_id, require_completed=require_completed
        )
        return {
            "valid": True,
            "session_id": session.session_id,
            "phases_completed": len(session.phases_completed),
            "is_complete": session.is_complete(),
        }
    except SMEBypassError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
