"""Verification Factory API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.security.deps import vfactory_route_auth
from axiom.vfactory.models import TestLevel
from axiom.vfactory.orchestrator import VFactoryOrchestrator
from axiom.vfactory.roles import default_verification_roles
from axiom.vfactory.scorer import compute_all_scores

router = APIRouter(
    prefix="/vfactory",
    tags=["verification-factory"],
    dependencies=[Depends(vfactory_route_auth)],
)


class RunCycleRequest(BaseModel):
    run_pyramid: bool = True
    run_journeys: bool = True
    run_health: bool = False
    changed_paths: list[str] = Field(default_factory=list)


class RunJourneyRequest(BaseModel):
    journey_key: str = Field(..., description="journey_a, journey_b, journey_c, or journey_d")


def _orchestrator() -> VFactoryOrchestrator:
    return VFactoryOrchestrator()


@router.get("/manifest")
def get_manifest() -> dict[str, Any]:
    return {
        "name": "AXIOM Verification Factory",
        "version": "1.0",
        "pyramid_levels": [level.name for level in TestLevel],
        "journeys": ["journey_a", "journey_b", "journey_c", "journey_d"],
        "roles": [r["role"] for r in default_verification_roles()],
    }


@router.get("/roles")
def get_roles() -> list[dict[str, Any]]:
    return default_verification_roles()


@router.post("/bootstrap")
def bootstrap() -> dict[str, Any]:
    return _orchestrator().bootstrap()


@router.get("/status")
def get_status() -> dict[str, Any]:
    return _orchestrator().get_status()


@router.get("/capabilities")
def list_capabilities(domain: str | None = None, status: str | None = None) -> dict[str, Any]:
    caps = _orchestrator().registry_store.list_capabilities(domain=domain, status=status)
    return {"count": len(caps), "capabilities": [c.to_dict() for c in caps]}


@router.get("/capabilities/{capability_id}")
def get_capability(capability_id: str) -> dict[str, Any]:
    cap = _orchestrator().registry_store.get_capability(capability_id)
    if not cap:
        raise HTTPException(status_code=404, detail=f"Capability not found: {capability_id}")
    return cap.to_dict()


@router.get("/scores")
def get_scores() -> dict[str, Any]:
    caps = _orchestrator().registry_store.list_capabilities()
    scores = compute_all_scores(caps)
    return {"scores": [s.to_dict() for s in scores]}


@router.post("/run/cycle")
def run_verification_cycle(body: RunCycleRequest) -> dict[str, Any]:
    vrun = _orchestrator().run_verification_cycle(
        run_pyramid=body.run_pyramid,
        run_journeys=body.run_journeys,
        run_health=body.run_health,
        changed_paths=body.changed_paths or None,
    )
    return vrun.to_dict()


@router.post("/run/journey")
def run_journey(body: RunJourneyRequest) -> dict[str, Any]:
    try:
        result = _orchestrator().run_journey(body.journey_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.to_dict()


@router.post("/run/pyramid/{level_name}")
def run_pyramid_level(level_name: str) -> dict[str, Any]:
    try:
        level = TestLevel[level_name.upper()]
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown level: {level_name}") from exc
    result = _orchestrator().run_pyramid_level(level)
    return result.to_dict()


@router.get("/runs")
def list_runs(limit: int = 20) -> dict[str, Any]:
    runs = _orchestrator().registry_store.list_verification_runs(limit=limit)
    return {"count": len(runs), "runs": [r.to_dict() for r in runs]}


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    vrun = _orchestrator().get_run(run_id)
    if not vrun:
        raise HTTPException(status_code=404, detail=f"Verification run not found: {run_id}")
    return vrun.to_dict()
