"""Scientific Knowledge Acquisition & Intelligence Loop (SKAI) — domain models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def _utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str = "skai") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class SourceType(str, Enum):
    RESEARCH_PAPER = "research_paper"
    PREPRINT = "preprint"
    BOOK = "book"
    CONFERENCE = "conference"
    DATASET = "dataset"
    FORMAL_LIBRARY = "formal_library"
    DOCUMENTATION = "documentation"
    REPOSITORY = "repository"
    BENCHMARK = "benchmark"
    RESEARCHER_DOCUMENT = "researcher_document"
    WEB = "web"


class SourceQualityTier(str, Enum):
    """Source quality ranking (SKAI §4) — explicit metadata, not implicit trust."""

    PEER_REVIEWED_PRIMARY = "peer_reviewed_primary"
    PRIMARY_PREPRINT = "primary_preprint"
    ESTABLISHED_TECHNICAL = "established_technical"
    RESEARCH_REPOSITORY = "research_repository"
    SECONDARY_ANALYSIS = "secondary_analysis"
    GENERAL_WEB = "general_web"
    UNVERIFIED = "unverified"


QUALITY_RANK: dict[SourceQualityTier, int] = {
    SourceQualityTier.PEER_REVIEWED_PRIMARY: 6,
    SourceQualityTier.PRIMARY_PREPRINT: 5,
    SourceQualityTier.ESTABLISHED_TECHNICAL: 4,
    SourceQualityTier.RESEARCH_REPOSITORY: 3,
    SourceQualityTier.SECONDARY_ANALYSIS: 2,
    SourceQualityTier.GENERAL_WEB: 1,
    SourceQualityTier.UNVERIFIED: 0,
}


class KnowledgeScope(str, Enum):
    """Knowledge isolation scopes (SKAI §15)."""

    GLOBAL = "global"
    ORGANIZATION = "organization"
    CAMPAIGN = "campaign"
    PRIVATE = "private"


class EntityType(str, Enum):
    THEOREM = "theorem"
    LEMMA = "lemma"
    DEFINITION = "definition"
    CONJECTURE = "conjecture"
    EXPERIMENT = "experiment"
    HYPOTHESIS = "hypothesis"
    METHOD = "method"
    DATASET = "dataset"
    RESULT = "result"
    LIMITATION = "limitation"
    OPEN_QUESTION = "open_question"
    COUNTEREXAMPLE = "counterexample"


class RelationType(str, Enum):
    DEPENDS_ON = "depends_on"
    PROVES = "proves"
    REFUTES = "refutes"
    EXTENDS = "extends"
    CITES = "cites"
    USES = "uses"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    FORMALIZED_AS = "formalized_as"
    LEAVES_OPEN = "leaves_open"
    CHALLENGES = "challenges"


class ConflictStatus(str, Enum):
    UNRESOLVED = "unresolved"
    PARTIALLY_RESOLVED = "partially_resolved"
    RESOLVED = "resolved"
    REQUIRES_INVESTIGATION = "requires_investigation"


class KnowledgeLayer(str, Enum):
    """Hierarchical memory compression (SKAI §16)."""

    RAW_SOURCE = "raw_source"
    EXTRACTED_EVIDENCE = "extracted_evidence"
    STRUCTURED_KNOWLEDGE = "structured_knowledge"
    RESEARCH_SUMMARY = "research_summary"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    GLOBAL_KNOWLEDGE = "global_knowledge"


@dataclass
class SourceProvenance:
    """Full provenance for every source (SKAI §3)."""

    source_id: str
    source_type: SourceType
    title: str
    authors: list[str] = field(default_factory=list)
    published_date: str | None = None
    identifier: str | None = None  # DOI, arXiv ID, etc.
    location: str | None = None
    content_hash: str | None = None
    extraction_method: str = "unknown"
    relevant_section: str | None = None
    quality_tier: SourceQualityTier = SourceQualityTier.UNVERIFIED
    reliability_score: float = 0.5
    scope: KnowledgeScope = KnowledgeScope.GLOBAL
    campaign_id: str | None = None
    organization_id: str | None = None
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "title": self.title,
            "authors": self.authors,
            "published_date": self.published_date,
            "identifier": self.identifier,
            "location": self.location,
            "content_hash": self.content_hash,
            "extraction_method": self.extraction_method,
            "relevant_section": self.relevant_section,
            "quality_tier": self.quality_tier.value,
            "reliability_score": self.reliability_score,
            "scope": self.scope.value,
            "campaign_id": self.campaign_id,
            "organization_id": self.organization_id,
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SourceProvenance:
        return cls(
            source_id=data["source_id"],
            source_type=SourceType(data["source_type"]),
            title=data["title"],
            authors=list(data.get("authors", [])),
            published_date=data.get("published_date"),
            identifier=data.get("identifier"),
            location=data.get("location"),
            content_hash=data.get("content_hash"),
            extraction_method=data.get("extraction_method", "unknown"),
            relevant_section=data.get("relevant_section"),
            quality_tier=SourceQualityTier(data.get("quality_tier", "unverified")),
            reliability_score=float(data.get("reliability_score", 0.5)),
            scope=KnowledgeScope(data.get("scope", "global")),
            campaign_id=data.get("campaign_id"),
            organization_id=data.get("organization_id"),
            version=int(data.get("version", 1)),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", _utc_now()),
            updated_at=data.get("updated_at", _utc_now()),
        )


@dataclass
class KnowledgeEntity:
    """Structured knowledge node beyond text chunks (SKAI §2)."""

    entity_id: str
    entity_type: EntityType
    title: str
    statement: str
    source_id: str
    confidence: float = 0.5
    verification_status: str = "unverified"
    scope: KnowledgeScope = KnowledgeScope.GLOBAL
    campaign_id: str | None = None
    egs_node_id: str | None = None
    claim_id: str | None = None
    layer: KnowledgeLayer = KnowledgeLayer.STRUCTURED_KNOWLEDGE
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "title": self.title,
            "statement": self.statement,
            "source_id": self.source_id,
            "confidence": self.confidence,
            "verification_status": self.verification_status,
            "scope": self.scope.value,
            "campaign_id": self.campaign_id,
            "egs_node_id": self.egs_node_id,
            "claim_id": self.claim_id,
            "layer": self.layer.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeEntity:
        return cls(
            entity_id=data["entity_id"],
            entity_type=EntityType(data["entity_type"]),
            title=data["title"],
            statement=data["statement"],
            source_id=data["source_id"],
            confidence=float(data.get("confidence", 0.5)),
            verification_status=data.get("verification_status", "unverified"),
            scope=KnowledgeScope(data.get("scope", "global")),
            campaign_id=data.get("campaign_id"),
            egs_node_id=data.get("egs_node_id"),
            claim_id=data.get("claim_id"),
            layer=KnowledgeLayer(data.get("layer", "structured_knowledge")),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", _utc_now()),
        )


@dataclass
class KnowledgeRelation:
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationType
    evidence: str = ""
    source_id: str | None = None
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relation_type": self.relation_type.value,
            "evidence": self.evidence,
            "source_id": self.source_id,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeRelation:
        return cls(
            relation_id=data["relation_id"],
            source_entity_id=data["source_entity_id"],
            target_entity_id=data["target_entity_id"],
            relation_type=RelationType(data["relation_type"]),
            evidence=data.get("evidence", ""),
            source_id=data.get("source_id"),
            confidence=float(data.get("confidence", 0.5)),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", _utc_now()),
        )


@dataclass
class KnowledgeConflict:
    """Explicit knowledge conflict (SKAI §7)."""

    conflict_id: str
    claim_statement: str
    positions: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    resolution: str = ""
    status: ConflictStatus = ConflictStatus.UNRESOLVED
    current_confidence: float = 0.5
    entity_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "claim_statement": self.claim_statement,
            "positions": self.positions,
            "evidence": self.evidence,
            "assumptions": self.assumptions,
            "resolution": self.resolution,
            "status": self.status.value,
            "current_confidence": self.current_confidence,
            "entity_ids": self.entity_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeConflict:
        return cls(
            conflict_id=data["conflict_id"],
            claim_statement=data["claim_statement"],
            positions=list(data.get("positions", [])),
            evidence=list(data.get("evidence", [])),
            assumptions=list(data.get("assumptions", [])),
            resolution=data.get("resolution", ""),
            status=ConflictStatus(data.get("status", "unresolved")),
            current_confidence=float(data.get("current_confidence", 0.5)),
            entity_ids=list(data.get("entity_ids", [])),
            created_at=data.get("created_at", _utc_now()),
            updated_at=data.get("updated_at", _utc_now()),
        )


@dataclass
class ResearchGap:
    """Research opportunity, not discovery (SKAI §9)."""

    gap_id: str
    title: str
    description: str
    gap_type: str  # unknown, unresolved_lemma, contradiction, technique_transfer, etc.
    related_entity_ids: list[str] = field(default_factory=list)
    related_conflict_ids: list[str] = field(default_factory=list)
    priority_score: float = 0.5
    evidence: list[str] = field(default_factory=list)
    campaign_id: str | None = None
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "title": self.title,
            "description": self.description,
            "gap_type": self.gap_type,
            "related_entity_ids": self.related_entity_ids,
            "related_conflict_ids": self.related_conflict_ids,
            "priority_score": self.priority_score,
            "evidence": self.evidence,
            "campaign_id": self.campaign_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchGap:
        return cls(
            gap_id=data["gap_id"],
            title=data["title"],
            description=data["description"],
            gap_type=data["gap_type"],
            related_entity_ids=list(data.get("related_entity_ids", [])),
            related_conflict_ids=list(data.get("related_conflict_ids", [])),
            priority_score=float(data.get("priority_score", 0.5)),
            evidence=list(data.get("evidence", [])),
            campaign_id=data.get("campaign_id"),
            created_at=data.get("created_at", _utc_now()),
        )


@dataclass
class KnowledgeVersion:
    """Versioned knowledge — never silently rewrite history (SKAI §8)."""

    version_id: str
    entity_id: str
    version_number: int
    snapshot: dict[str, Any]
    change_reason: str
    superseded_by: str | None = None
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_id": self.version_id,
            "entity_id": self.entity_id,
            "version_number": self.version_number,
            "snapshot": self.snapshot,
            "change_reason": self.change_reason,
            "superseded_by": self.superseded_by,
            "created_at": self.created_at,
        }


@dataclass
class LiteratureCoverage:
    """Literature saturation estimate (SKAI §10)."""

    research_question: str
    coverage_fraction: float
    sources_found: int
    sources_ingested: int
    known_gaps: list[str] = field(default_factory=list)
    search_strategies_used: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "research_question": self.research_question,
            "coverage_fraction": self.coverage_fraction,
            "sources_found": self.sources_found,
            "sources_ingested": self.sources_ingested,
            "known_gaps": self.known_gaps,
            "search_strategies_used": self.search_strategies_used,
            "created_at": self.created_at,
        }


@dataclass
class AcquisitionResult:
    """Result of a full knowledge acquisition cycle."""

    acquisition_id: str
    research_question: str
    sources: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    coverage: LiteratureCoverage | None = None
    expanded_questions: list[str] = field(default_factory=list)
    status: str = "completed"
    duplicate: bool = False
    untrusted: bool = False
    retrieved_at: str | None = None
    source_url: str | None = None
    instruction_pattern_hits: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "acquisition_id": self.acquisition_id,
            "research_question": self.research_question,
            "sources": self.sources,
            "entities": self.entities,
            "relations": self.relations,
            "conflicts": self.conflicts,
            "gaps": self.gaps,
            "coverage": self.coverage.to_dict() if self.coverage else None,
            "expanded_questions": self.expanded_questions,
            "status": self.status,
            "duplicate": self.duplicate,
            "untrusted": self.untrusted,
            "retrieved_at": self.retrieved_at,
            "source_url": self.source_url,
            "instruction_pattern_hits": self.instruction_pattern_hits,
            "created_at": self.created_at,
        }
