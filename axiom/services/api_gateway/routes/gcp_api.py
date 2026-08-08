"""Grand Challenge Program API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.grand_challenge.engine import GrandChallengeEngine
from axiom.grand_challenge.gates import list_gates
from axiom.grand_challenge.models import ChallengeTier
from axiom.grand_challenge.registry import get_challenge, list_challenges, program_manifest
from axiom.security.deps import gcp_route_auth

router = APIRouter(
    prefix="/gcp",
    tags=["grand-challenge"],
    dependencies=[Depends(gcp_route_auth)],
)


class CreateCampaignRequest(BaseModel):
    name: str
    description: str = ""
    tier: int = 0
    challenge_ids: list[str] | None = None


class AddHypothesisRequest(BaseModel):
    statement: str
    confidence: float = 0.5


class JournalEntryRequest(BaseModel):
    title: str
    content: str
    phase: str = "observation"


class AdvanceTierRequest(BaseModel):
    human_approved: bool = False


def _engine() -> GrandChallengeEngine:
    return GrandChallengeEngine(settings.db_path)


@router.get("/manifest")
def get_manifest() -> dict[str, Any]:
    return program_manifest()


@router.get("/tiers")
def list_tiers() -> list[dict[str, Any]]:
    manifest = program_manifest()
    return manifest["tiers"]


@router.get("/challenges")
def get_challenges(tier: int | None = None) -> dict[str, Any]:
    if tier is not None:
        challenges = list_challenges(ChallengeTier(tier))
    else:
        challenges = list_challenges()
    return {"count": len(challenges), "challenges": [c.model_dump(mode="json") for c in challenges]}


@router.get("/challenges/{challenge_id}")
def get_challenge_detail(challenge_id: str) -> dict[str, Any]:
    try:
        return get_challenge(challenge_id).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/gates")
def get_gates() -> dict[str, Any]:
    gates = list_gates()
    return {"count": len(gates), "gates": gates}


@router.post("/campaigns", status_code=201)
def create_campaign(body: CreateCampaignRequest) -> dict[str, Any]:
    campaign = _engine().create_campaign(
        name=body.name,
        description=body.description,
        tier=ChallengeTier(body.tier),
        challenge_ids=body.challenge_ids,
    )
    return campaign.model_dump(mode="json")


@router.get("/campaigns")
def list_campaigns(limit: int = 50, status: str | None = None) -> dict[str, Any]:
    campaigns = _engine().store.list_campaigns(limit=limit, status=status)
    return {"count": len(campaigns), "campaigns": [c.model_dump(mode="json") for c in campaigns]}


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str) -> dict[str, Any]:
    campaign = _engine().get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign.model_dump(mode="json")


@router.post("/campaigns/{campaign_id}/activate")
def activate_campaign(campaign_id: str) -> dict[str, Any]:
    try:
        return _engine().activate_campaign(campaign_id).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/hypotheses")
def add_hypothesis(campaign_id: str, body: AddHypothesisRequest) -> dict[str, Any]:
    try:
        return _engine().add_hypothesis(campaign_id, body.statement, body.confidence).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/journal")
def add_journal_entry(campaign_id: str, body: JournalEntryRequest) -> dict[str, Any]:
    try:
        return _engine().add_journal_entry(
            campaign_id, body.title, body.content, body.phase
        ).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/experiments/{challenge_id}")
def run_experiment(campaign_id: str, challenge_id: str) -> dict[str, Any]:
    try:
        return _engine().run_experiment(campaign_id, challenge_id).model_dump(mode="json")
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/run-tier")
def run_tier_batch(campaign_id: str, tier: int | None = None) -> dict[str, Any]:
    try:
        t = ChallengeTier(tier) if tier is not None else None
        return _engine().run_tier_batch(campaign_id, t).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/checkpoint")
def save_checkpoint(campaign_id: str) -> dict[str, Any]:
    try:
        return _engine().checkpoint(campaign_id).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/campaigns/{campaign_id}/readiness")
def check_readiness(campaign_id: str) -> dict[str, Any]:
    try:
        return _engine().evaluate_readiness(campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/campaigns/{campaign_id}/advance")
def advance_tier(campaign_id: str, body: AdvanceTierRequest | None = None) -> dict[str, Any]:
    try:
        approved = body.human_approved if body else False
        return _engine().advance_tier(campaign_id, human_approved=approved).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/campaigns/{campaign_id}/journal")
def get_journal(campaign_id: str) -> dict[str, Any]:
    try:
        return {"campaign_id": campaign_id, "journal": _engine().get_journal(campaign_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
