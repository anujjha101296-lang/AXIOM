"""Evidence & Reproducibility Loop (E&R) — domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ClaimStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    SPECULATIVE = "SPECULATIVE"
    PLAUSIBLE = "PLAUSIBLE"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"
    REJECTED = "REJECTED"
    DISPROVED = "DISPROVED"


class EvidenceType(str, Enum):
    PAPER = "paper"
    QUOTATION = "quotation"
    DATASET = "dataset"
    EXPERIMENT = "experiment"
    COMPUTATION = "computation"
    FORMAL_PROOF = "formal_proof"
    COUNTEREXAMPLE = "counterexample"
    SIMULATION = "simulation"
    HUMAN_REVIEW = "human_review"


class ReproductionStatus(str, Enum):
    REPRODUCED = "REPRODUCED"
    PARTIALLY_REPRODUCED = "PARTIALLY_REPRODUCED"
    NOT_REPRODUCED = "NOT_REPRODUCED"
    UNABLE_TO_REPRODUCE = "UNABLE_TO_REPRODUCE"


class ProvenanceEdgeType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    DEPENDS_ON = "depends_on"
    CITES = "cites"
    PRODUCED_BY = "produced_by"
    VERIFIED_BY = "verified_by"


# Status ordering for upgrade validation
_STATUS_RANK = {
    ClaimStatus.UNKNOWN: 0,
    ClaimStatus.SPECULATIVE: 1,
    ClaimStatus.PLAUSIBLE: 2,
    ClaimStatus.SUPPORTED: 3,
    ClaimStatus.VERIFIED: 4,
    ClaimStatus.FORMALLY_VERIFIED: 5,
    ClaimStatus.REJECTED: 1,
    ClaimStatus.DISPROVED: 2,
}

DISCOVERY_LABELS = frozenset({
    "NEW_DISCOVERY",
    "NEW_THEOREM",
    "NOVEL_RESULT",
    "PROOF_OF_OPEN_PROBLEM",
})


@dataclass
class SourceRecord:
    source_id: str
    title: str
    retrieved_at: str
    url: str | None = None
    authors: list[str] = field(default_factory=list)
    publication: str | None = None
    content_hash: str | None = None
    extraction_method: str | None = None
    version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "authors": self.authors,
            "publication": self.publication,
            "retrieved_at": self.retrieved_at,
            "content_hash": self.content_hash,
            "extraction_method": self.extraction_method,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass
class EvidenceObject:
    evidence_id: str
    evidence_type: EvidenceType
    summary: str
    created_at: str
    claim_id: str | None = None
    source_id: str | None = None
    experiment_id: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    verifier: str | None = None
    formally_verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "summary": self.summary,
            "created_at": self.created_at,
            "claim_id": self.claim_id,
            "source_id": self.source_id,
            "experiment_id": self.experiment_id,
            "provenance": self.provenance,
            "verifier": self.verifier,
            "formally_verified": self.formally_verified,
        }


@dataclass
class ExperimentRecord:
    experiment_id: str
    objective: str
    created_at: str
    hypothesis: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    run_id: str | None = None
    reproduction_status: ReproductionStatus | None = None
    verification_status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "objective": self.objective,
            "hypothesis": self.hypothesis,
            "created_at": self.created_at,
            "config": self.config,
            "environment": self.environment,
            "result": self.result,
            "artifacts": self.artifacts,
            "run_id": self.run_id,
            "reproduction_status": (
                self.reproduction_status.value if self.reproduction_status else None
            ),
            "verification_status": self.verification_status,
        }


@dataclass
class ScientificClaim:
    claim_id: str
    statement: str
    status: ClaimStatus
    version: int
    created_at: str
    updated_at: str
    author: str = "system"
    campaign_id: str | None = None
    parent_claim_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reviewer: str | None = None
    supporting_evidence_ids: list[str] = field(default_factory=list)
    contradicting_evidence_ids: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    experiment_ids: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "author": self.author,
            "campaign_id": self.campaign_id,
            "parent_claim_ids": self.parent_claim_ids,
            "confidence": self.confidence,
            "reviewer": self.reviewer,
            "supporting_evidence_ids": self.supporting_evidence_ids,
            "contradicting_evidence_ids": self.contradicting_evidence_ids,
            "source_ids": self.source_ids,
            "experiment_ids": self.experiment_ids,
            "labels": self.labels,
            "limitations": self.limitations,
        }


def status_rank(status: ClaimStatus) -> int:
    return _STATUS_RANK.get(status, 0)
