"""E&R Loop — Evidence & Reproducibility API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.evidence.integrity import audit_registry
from axiom.evidence.models import ClaimStatus, EvidenceType
from axiom.evidence.registry import get_claim_registry
from axiom.evidence.reproduction import compare_provenance_runs
from axiom.observability.run_provenance import RunType, get_provenance_store
from axiom.security.deps import evidence_route_auth

router = APIRouter(
    prefix="/evidence",
    tags=["evidence"],
    dependencies=[Depends(evidence_route_auth)],
)


class RegisterClaimRequest(BaseModel):
    statement: str
    author: str = "system"
    campaign_id: str | None = None
    parent_claim_ids: list[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.UNKNOWN


class AddEvidenceRequest(BaseModel):
    evidence_type: EvidenceType
    summary: str
    source_id: str | None = None
    experiment_id: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    verifier: str | None = None
    formally_verified: bool = False
    supports: bool = True


class UpdateStatusRequest(BaseModel):
    status: ClaimStatus
    reviewer: str | None = None


class DiscoveryLabelRequest(BaseModel):
    label: str
    reproduction_passed: bool = False
    independent_verification: bool = False
    human_review: bool = False


class RegisterSourceRequest(BaseModel):
    title: str
    url: str | None = None
    authors: list[str] = Field(default_factory=list)
    publication: str | None = None
    content_hash: str | None = None
    extraction_method: str | None = None
    version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegisterExperimentRequest(BaseModel):
    objective: str
    hypothesis: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)
    run_id: str | None = None


class ReproductionCompareRequest(BaseModel):
    run_type: RunType
    original_run_id: str
    reproduction_run_id: str
    score_tolerance: float = 0.01


@router.post("/claims")
def register_claim(body: RegisterClaimRequest) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    claim = registry.register_claim(
        body.statement,
        author=body.author,
        campaign_id=body.campaign_id,
        parent_claim_ids=body.parent_claim_ids,
        status=body.status,
    )
    return claim.to_dict()


@router.get("/claims")
def list_claims(limit: int = 100) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    claims = registry.list_claims(limit=limit)
    return {"count": len(claims), "claims": [c.to_dict() for c in claims]}


@router.get("/claims/{claim_id}")
def get_claim(claim_id: str) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    claim = registry.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim not found: {claim_id}")
    return claim.to_dict()


@router.post("/claims/{claim_id}/evidence")
def add_evidence(claim_id: str, body: AddEvidenceRequest) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    try:
        evidence = registry.add_evidence(
            claim_id,
            body.evidence_type,
            body.summary,
            source_id=body.source_id,
            experiment_id=body.experiment_id,
            provenance=body.provenance,
            verifier=body.verifier,
            formally_verified=body.formally_verified,
            supports=body.supports,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Claim not found: {claim_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return evidence.to_dict()


@router.post("/claims/{claim_id}/status")
def update_claim_status(claim_id: str, body: UpdateStatusRequest) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    try:
        claim, gate = registry.update_status(
            claim_id, body.status, reviewer=body.reviewer
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Claim not found: {claim_id}")

    if not gate.allowed:
        raise HTTPException(status_code=403, detail=gate.reason)
    return {"claim": claim.to_dict(), "gate": gate.to_dict()}


@router.post("/claims/{claim_id}/labels")
def add_discovery_label(claim_id: str, body: DiscoveryLabelRequest) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    try:
        claim, gate = registry.add_discovery_label(
            claim_id,
            body.label,
            reproduction_passed=body.reproduction_passed,
            independent_verification=body.independent_verification,
            human_review=body.human_review,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Claim not found: {claim_id}")

    if not gate.allowed:
        raise HTTPException(status_code=403, detail=gate.reason)
    return {"claim": claim.to_dict(), "gate": gate.to_dict()}


@router.get("/claims/{claim_id}/lineage")
def get_claim_lineage(claim_id: str) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    try:
        return registry.get_lineage(claim_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Claim not found: {claim_id}")


@router.get("/dashboard")
def evidence_dashboard() -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    stats = registry.dashboard_stats()
    integrity = audit_registry(registry)
    return {**stats, "integrity": integrity.to_dict()}


@router.post("/sources")
def register_source(body: RegisterSourceRequest) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    source = registry.register_source(
        body.title,
        url=body.url,
        authors=body.authors,
        publication=body.publication,
        content_hash=body.content_hash,
        extraction_method=body.extraction_method,
        version=body.version,
        metadata=body.metadata,
    )
    return source.to_dict()


@router.post("/experiments")
def register_experiment(body: RegisterExperimentRequest) -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    experiment = registry.register_experiment(
        body.objective,
        hypothesis=body.hypothesis,
        config=body.config,
        environment=body.environment,
        result=body.result,
        run_id=body.run_id,
    )
    return experiment.to_dict()


@router.post("/reproduction/compare")
def compare_reproduction_runs(body: ReproductionCompareRequest) -> dict[str, Any]:
    store = get_provenance_store(settings.db_path)
    original = store.get(body.run_type, body.original_run_id)
    reproduction = store.get(body.run_type, body.reproduction_run_id)
    if not original:
        raise HTTPException(
            status_code=404,
            detail=f"Original run not found: {body.run_type}/{body.original_run_id}",
        )
    if not reproduction:
        raise HTTPException(
            status_code=404,
            detail=f"Reproduction run not found: {body.run_type}/{body.reproduction_run_id}",
        )

    status, differences = compare_provenance_runs(
        original,
        reproduction,
        score_tolerance=body.score_tolerance,
    )
    return {
        "status": status.value,
        "differences": differences,
        "original_run_id": body.original_run_id,
        "reproduction_run_id": body.reproduction_run_id,
    }


@router.get("/integrity")
def integrity_audit() -> dict[str, Any]:
    registry = get_claim_registry(settings.db_path)
    return audit_registry(registry).to_dict()
