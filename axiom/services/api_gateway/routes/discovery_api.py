"""Scientific Discovery Engine API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.discovery.benchmarks import run_all_benchmarks
from axiom.discovery.engine import DiscoveryEngine, DiscoveryTransitionError
from axiom.discovery.models import DiscoveryStatus
from axiom.services.api_gateway.auth import optional_token_owner_id

router = APIRouter(prefix="/discovery", tags=["scientific-discovery-engine"])


class CreateDiscoveryRequest(BaseModel):
    research_question: str = Field(..., min_length=8, max_length=4000)
    knowledge_context: str = ""
    seed_text: str | None = None
    campaign_id: str | None = None


class TransitionRequest(BaseModel):
    status: str
    reason: str = Field(..., min_length=3)
    allow_verified: bool = False


class HumanDecisionRequest(BaseModel):
    action: str = Field(
        ...,
        description="approve_hypothesis | reject_hypothesis | pause | stop",
    )
    reason: str = Field(..., min_length=3)
    hypothesis_id: str | None = None


def _engine() -> DiscoveryEngine:
    return DiscoveryEngine(settings.db_path)


def _owned(discovery_id: str, owner_id: str):
    engine = _engine()
    d = engine.store.get(discovery_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Discovery not found: {discovery_id}")
    if owner_id != "dev" and d.owner_id and d.owner_id != owner_id:
        raise HTTPException(status_code=404, detail=f"Discovery not found: {discovery_id}")
    return engine, d


@router.get("/manifest")
def manifest() -> dict[str, Any]:
    return {
        "name": "AXIOM Scientific Discovery Engine",
        "version": "0.1",
        "principle": "Hypothesis ≠ fact; computational evidence ≠ proof; missing papers ≠ novelty",
        "states": [s.value for s in DiscoveryStatus],
        "loop": [
            "knowledge",
            "gap",
            "opportunity",
            "hypotheses",
            "predictions",
            "experiment",
            "counterexample",
            "independent_attack",
            "report",
            "knowledge_update",
        ],
        "millennium_attempt": False,
    }


@router.post("/investigations")
def create_discovery(
    body: CreateDiscoveryRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    d = _engine().create(
        body.research_question,
        knowledge_context=body.knowledge_context,
        seed_text=body.seed_text,
        campaign_id=body.campaign_id,
        owner_id=owner_id,
    )
    return d.to_dict()


@router.get("/investigations")
def list_discoveries(
    status: str | None = None,
    limit: int = 50,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    items = _engine().store.list(status=status, owner_id=owner_id, limit=limit)
    return {"count": len(items), "investigations": [d.to_dict() for d in items]}


@router.get("/investigations/{discovery_id}")
def get_discovery(
    discovery_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _, d = _owned(discovery_id, owner_id)
    return d.to_dict()


@router.post("/investigations/{discovery_id}/opportunities")
def detect_opportunities(
    discovery_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    engine, _ = _owned(discovery_id, owner_id)
    return engine.detect_opportunities(discovery_id).to_dict()


@router.post("/investigations/{discovery_id}/hypotheses")
def generate_hypotheses(
    discovery_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    engine, _ = _owned(discovery_id, owner_id)
    return engine.generate_hypotheses(discovery_id).to_dict()


@router.post("/investigations/{discovery_id}/cycle")
def run_cycle(
    discovery_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    engine, _ = _owned(discovery_id, owner_id)
    return engine.run_cycle(discovery_id)


@router.post("/investigations/{discovery_id}/transition")
def transition(
    discovery_id: str,
    body: TransitionRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    engine, _ = _owned(discovery_id, owner_id)
    try:
        return engine.transition(
            discovery_id,
            DiscoveryStatus(body.status),
            reason=body.reason,
            actor=owner_id,
            allow_verified=body.allow_verified,
        ).to_dict()
    except DiscoveryTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/investigations/{discovery_id}/human")
def human_decide(
    discovery_id: str,
    body: HumanDecisionRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    """Human researcher control — approve / reject / pause / stop."""
    engine, _ = _owned(discovery_id, owner_id)
    try:
        return engine.human_decide(
            discovery_id,
            action=body.action,
            reason=body.reason,
            actor=owner_id,
            hypothesis_id=body.hypothesis_id,
        ).to_dict()
    except DiscoveryTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/investigations/{discovery_id}/report")
def get_report(
    discovery_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    engine, d = _owned(discovery_id, owner_id)
    if not d.report:
        d = engine.synthesize_report(discovery_id)
    return d.report


@router.post("/benchmarks/run")
def run_benchmarks() -> dict[str, Any]:
    """Run deterministic discovery benchmarks (including false-discovery traps)."""
    import tempfile
    from pathlib import Path

    db = Path(tempfile.mkdtemp()) / "discovery_bench.db"
    return run_all_benchmarks(str(db))
