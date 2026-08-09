"""Open Problem Research Lab API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.open_problems.engine import OpenProblemError, OpenProblemLab
from axiom.open_problems.models import ResearchStatus
from axiom.services.api_gateway.auth import optional_token_owner_id

router = APIRouter(prefix="/open-problems", tags=["open-problem-research-lab"])


class CreateProblemRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    informal_statement: str = Field(..., min_length=8, max_length=8000)
    domain: str = "mathematics"
    known_info: str = ""
    sources: list[str] = Field(default_factory=list)
    research_objective: str = ""
    constraints: list[str] = Field(default_factory=list)
    stage_level: int = Field(default=1, ge=1, le=8)
    formal_statement: str = ""


class TransitionRequest(BaseModel):
    status: str
    reason: str = Field(..., min_length=3)
    allow_resolved: bool = False


class AbandonRequest(BaseModel):
    strategy_id: str
    reason: str = Field(..., min_length=3)


def _lab() -> OpenProblemLab:
    return OpenProblemLab(settings.db_path)


def _owned(problem_id: str, owner_id: str):
    lab = _lab()
    p = lab.store.get(problem_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Open problem not found: {problem_id}")
    if owner_id != "dev" and p.owner_id and p.owner_id != owner_id:
        raise HTTPException(status_code=404, detail=f"Open problem not found: {problem_id}")
    return lab, p


@router.get("/manifest")
def manifest() -> dict[str, Any]:
    return {
        "name": "AXIOM Open Problem Research Lab",
        "version": "0.1",
        "reuses": ["FRCE", "Discovery", "SKAI", "FMTP", "SEC", "Arena"],
        "millennium_auto_start": False,
        "loop": [
            "understand",
            "map",
            "decompose",
            "strategies",
            "compete",
            "experiment",
            "attack",
            "formalize",
            "verify",
            "remember",
            "continue",
        ],
        "stages": OpenProblemLab(settings.db_path).stage_manifest(),
    }


@router.post("")
def create_problem(
    body: CreateProblemRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    try:
        p = _lab().create(
            body.title,
            body.informal_statement,
            domain=body.domain,
            known_info=body.known_info,
            sources=body.sources,
            research_objective=body.research_objective,
            constraints=body.constraints,
            stage_level=body.stage_level,
            owner_id=owner_id,
            formal_statement=body.formal_statement,
        )
    except OpenProblemError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return p.to_dict()


@router.get("")
def list_problems(
    limit: int = 50,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    items = _lab().store.list(owner_id=owner_id, limit=limit)
    return {"count": len(items), "problems": [p.to_dict() for p in items]}


@router.get("/{problem_id}")
def get_problem(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    _, p = _owned(problem_id, owner_id)
    return p.to_dict()


@router.post("/{problem_id}/map")
def map_knowledge(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.map_knowledge(problem_id).to_dict()


@router.post("/{problem_id}/decompose")
def decompose(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.decompose(problem_id).to_dict()


@router.post("/{problem_id}/strategies")
def strategies(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.generate_strategies(problem_id).to_dict()


@router.post("/{problem_id}/campaign")
def start_campaign(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.start_campaign(problem_id).to_dict()


@router.post("/{problem_id}/cycle")
def run_cycle(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.run_investigation_cycle(problem_id)


@router.get("/{problem_id}/report")
def report(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, p = _owned(problem_id, owner_id)
    if not p.report:
        lab.run_investigation_cycle(problem_id)
        p = lab.store.get(problem_id)
    assert p is not None
    return p.report


@router.get("/{problem_id}/tracks")
def tracks(problem_id: str, owner_id: str = Depends(optional_token_owner_id)) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.compare_tracks(problem_id)


@router.post("/{problem_id}/abandon-strategy")
def abandon(
    problem_id: str,
    body: AbandonRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    return lab.abandon_strategy(problem_id, body.strategy_id, body.reason).to_dict()


@router.post("/{problem_id}/transition")
def transition(
    problem_id: str,
    body: TransitionRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    lab, _ = _owned(problem_id, owner_id)
    try:
        return lab.transition(
            problem_id,
            ResearchStatus(body.status),
            reason=body.reason,
            allow_resolved=body.allow_resolved,
        ).to_dict()
    except OpenProblemError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
