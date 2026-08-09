"""Frontier Research Campaign Engine API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.campaign.models import LadderLevel, ResourceBudget
from axiom.campaign.orchestrator import FrontierCampaignEngine
from axiom.config import settings
from axiom.security.deps import frce_route_auth
from axiom.services.api_gateway.auth import optional_token_owner_id

router = APIRouter(
    prefix="/frce",
    tags=["frontier-research-campaign"],
    dependencies=[Depends(frce_route_auth)],
)


class CreateCampaignRequest(BaseModel):
    name: str
    objective: str
    problem_definition: str = ""
    domain: str = "mathematics"
    ladder_level: int = Field(default=1, ge=0, le=9)
    success_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    link_gcp: bool = False
    budget: dict[str, Any] | None = None


class ResolveGateRequest(BaseModel):
    approved: bool
    notes: str = ""


class AbandonRequest(BaseModel):
    reason: str = ""


def _engine() -> FrontierCampaignEngine:
    return FrontierCampaignEngine(settings.db_path)


def _owned_campaign(campaign_id: str, owner_id: str):
    campaign = _engine().get_campaign(campaign_id, owner_id=owner_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign not found: {campaign_id}")
    return campaign


@router.get("/manifest")
def get_manifest() -> dict[str, Any]:
    return _engine().manifest()


@router.get("/ladder")
def get_ladder() -> dict[str, Any]:
    from axiom.campaign.ladder import ladder_manifest
    return ladder_manifest()


@router.get("/roles")
def get_roles() -> list[dict[str, Any]]:
    from axiom.campaign.roles import list_roles
    return list_roles()


@router.post("/campaigns")
def create_campaign(
    body: CreateCampaignRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    budget = ResourceBudget.from_dict(body.budget) if body.budget else None
    campaign = _engine().create_campaign(
        name=body.name,
        objective=body.objective,
        problem_definition=body.problem_definition,
        domain=body.domain,
        ladder_level=LadderLevel(body.ladder_level),
        success_criteria=body.success_criteria,
        constraints=body.constraints,
        budget=budget,
        link_gcp=body.link_gcp,
        owner_id=owner_id,
    )
    return campaign.to_dict()


@router.get("/campaigns")
def list_campaigns(
    phase: str | None = None,
    limit: int = 50,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    campaigns = _engine().list_campaigns(phase=phase, limit=limit, owner_id=owner_id)
    return {"count": len(campaigns), "campaigns": [c.to_dict() for c in campaigns]}


@router.get("/campaigns/{campaign_id}")
def get_campaign(
    campaign_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    return _owned_campaign(campaign_id, owner_id).to_dict()


@router.get("/campaigns/{campaign_id}/dashboard")
def campaign_dashboard(
    campaign_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().dashboard(campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/scope")
def scope_campaign(
    campaign_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().scope(campaign_id).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/plan")
def plan_campaign(
    campaign_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().plan(campaign_id).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/cycle")
def run_cycle(
    campaign_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().run_cycle(campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/checkpoint")
def checkpoint_campaign(
    campaign_id: str,
    title: str = "Manual checkpoint",
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().checkpoint(campaign_id, title=title).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/gates/{gate_id}/resolve")
def resolve_gate(
    campaign_id: str,
    gate_id: str,
    body: ResolveGateRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().resolve_human_gate(
            campaign_id, gate_id, approved=body.approved, notes=body.notes
        ).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/abandon")
def abandon_campaign(
    campaign_id: str,
    body: AbandonRequest,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        return _engine().abandon(campaign_id, reason=body.reason).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/compound-memory")
def compound_memory(
    campaign_id: str,
    owner_id: str = Depends(optional_token_owner_id),
) -> dict[str, Any]:
    _owned_campaign(campaign_id, owner_id)
    try:
        entry_ids = _engine().compound_memory(campaign_id)
        return {"campaign_id": campaign_id, "global_memory_entry_ids": entry_ids}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/global-memory")
def global_memory(limit: int = 100) -> dict[str, Any]:
    from axiom.campaign.store import get_campaign_store
    entries = get_campaign_store(settings.db_path).list_global_memory(limit=limit)
    return {"count": len(entries), "entries": entries}
