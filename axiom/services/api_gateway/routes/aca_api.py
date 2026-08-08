"""AXIOM Cognitive Architecture API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from axiom.cognitive.engine import CognitiveArchitecture
from axiom.cognitive.models import CognitiveLayer, LAYER_ORDER
from axiom.cognitive.registry import architecture_manifest
from axiom.config import settings

router = APIRouter(prefix="/aca", tags=["cognitive-architecture"])


class CreateCycleRequest(BaseModel):
    objective: str
    domain: str = "research"
    model_provider: str = "default"
    context: dict[str, Any] = Field(default_factory=dict)
    sme_session_id: str | None = None


class ExecuteLayerRequest(BaseModel):
    layer: CognitiveLayer | None = None


def _engine(provider: str = "default") -> CognitiveArchitecture:
    return CognitiveArchitecture(settings.db_path, model_provider_id=provider)


@router.get("/architecture")
def get_architecture() -> dict[str, Any]:
    """Return the full ACA manifest — layers, pillars, subsystem mappings."""
    return architecture_manifest()


@router.get("/layers")
def list_layers() -> list[dict[str, Any]]:
    manifest = architecture_manifest()
    return manifest["layers"]


@router.post("/cycles", status_code=201)
def create_cycle(body: CreateCycleRequest) -> dict[str, Any]:
    engine = _engine(body.model_provider)
    cycle = engine.create_cycle(
        objective=body.objective,
        domain=body.domain,
        context=body.context,
        model_provider=body.model_provider,
    )
    if body.sme_session_id:
        cycle = engine.link_sme(cycle.cycle_id, body.sme_session_id)
    return cycle.model_dump(mode="json")


@router.get("/cycles")
def list_cycles(limit: int = 50) -> dict[str, Any]:
    cycles = CognitiveArchitecture(settings.db_path).store.list_cycles(limit=limit)
    return {"count": len(cycles), "cycles": [c.model_dump(mode="json") for c in cycles]}


@router.get("/cycles/{cycle_id}")
def get_cycle(cycle_id: str) -> dict[str, Any]:
    cycle = CognitiveArchitecture(settings.db_path).store.get(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cognitive cycle not found")
    return cycle.model_dump(mode="json")


@router.post("/cycles/{cycle_id}/layers")
def execute_layer(cycle_id: str, body: ExecuteLayerRequest | None = None) -> dict[str, Any]:
    try:
        cycle = _engine().execute_layer(cycle_id, body.layer if body else None)
        return cycle.model_dump(mode="json")
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/cycles/{cycle_id}/run")
def run_full_cycle(cycle_id: str) -> dict[str, Any]:
    try:
        cycle = _engine().run_full_cycle(cycle_id)
        return cycle.model_dump(mode="json")
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/providers")
def list_providers() -> dict[str, Any]:
    return {
        "available": ["default", "heuristic"],
        "principle": "Models are interchangeable; cognitive architecture is permanent.",
    }
