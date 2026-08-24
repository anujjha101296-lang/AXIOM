"""
axiom.knowledge_graph.models
============================
Domain models for the Scientific Knowledge Graph & Claim Graph.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def generate_uuid() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ClaimType(str, Enum):
    FACTUAL = "FACTUAL"
    DEFINITIONAL = "DEFINITIONAL"
    QUANTITATIVE = "QUANTITATIVE"
    CAUSAL = "CAUSAL"
    COMPARATIVE = "COMPARATIVE"
    METHODOLOGICAL = "METHODOLOGICAL"
    OTHER = "OTHER"


class EpistemicStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    HYPOTHESIS = "HYPOTHESIS"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    METHOD = "method"
    ALGORITHM = "algorithm"
    THEOREM = "theorem"
    MATHEMATICAL_OBJECT = "mathematical_object"
    PHYSICAL_OBJECT = "physical_object"
    DATASET = "dataset"
    SOFTWARE = "software"
    CONCEPT = "concept"
    PAPER = "paper"
    RESEARCH_FIELD = "research_field"
    OTHER = "other"


class PredicateType(str, Enum):
    USES = "USES"
    PART_OF = "PART_OF"
    DEPENDS_ON = "DEPENDS_ON"
    IMPROVES = "IMPROVES"
    CAUSES = "CAUSES"
    MEASURES = "MEASURES"
    APPLIES_TO = "APPLIES_TO"
    RELATED_TO = "RELATED_TO"
    PROPOSES = "PROPOSES"
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"


class RelationshipStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class GapType(str, Enum):
    NO_EVIDENCE = "NO_EVIDENCE"
    WEAK_EVIDENCE = "WEAK_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    INFERRED_ONLY = "INFERRED_ONLY"
    MISSING_RELATIONSHIP = "MISSING_RELATIONSHIP"
    UNRESOLVED_QUESTION = "UNRESOLVED_QUESTION"


class GraphEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    name: str
    entity_type: EntityType = EntityType.CONCEPT
    domain: str = "general"
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> GraphEntity:
        meta = {}
        if hasattr(db_obj, "metadata_json") and db_obj.metadata_json:
            try:
                meta = json.loads(db_obj.metadata_json)
            except Exception:
                meta = {}
        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            name=db_obj.name,
            entity_type=EntityType(db_obj.entity_type),
            domain=db_obj.domain,
            description=db_obj.description,
            metadata=meta,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )


class GraphEntityAlias(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    entity_id: str
    alias: str
    source_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)


class GraphClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    claim_text: str
    claim_type: ClaimType = ClaimType.FACTUAL
    epistemic_status: EpistemicStatus = EpistemicStatus.EXTRACTED
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> GraphClaim:
        meta = {}
        if hasattr(db_obj, "metadata_json") and db_obj.metadata_json:
            try:
                meta = json.loads(db_obj.metadata_json)
            except Exception:
                meta = {}
        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            claim_text=db_obj.claim_text,
            claim_type=ClaimType(db_obj.claim_type),
            epistemic_status=EpistemicStatus(db_obj.epistemic_status),
            confidence_score=db_obj.confidence_score,
            metadata=meta,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )


class GraphClaimEvidence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    claim_id: str
    chunk_id: Optional[str] = None
    source_id: Optional[str] = None
    document_id: Optional[str] = None
    supports: bool = True
    snippet: str = ""
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class GraphRelationship(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    subject_entity_id: str
    object_entity_id: str
    predicate: PredicateType = PredicateType.RELATED_TO
    status: RelationshipStatus = RelationshipStatus.EXTRACTED
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class GraphRelationshipEvidence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    relationship_id: str
    chunk_id: Optional[str] = None
    source_id: Optional[str] = None
    snippet: str = ""
    created_at: datetime = Field(default_factory=utcnow)


class GraphContradiction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    claim_a_id: str
    claim_b_id: str
    contradiction_type: str = "DIRECT"
    reasoning: str = ""
    resolved: bool = False
    created_at: datetime = Field(default_factory=utcnow)


class GraphResearchGap(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    gap_type: GapType = GapType.NO_EVIDENCE
    description: str
    severity: str = "MEDIUM"
    target_entity_id: Optional[str] = None
    target_claim_id: Optional[str] = None
    target_question_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class KnowledgeGraphSummary(BaseModel):
    project_id: str
    total_entities: int = 0
    total_claims: int = 0
    total_relationships: int = 0
    total_contradictions: int = 0
    total_gaps: int = 0
    entities: List[GraphEntity] = Field(default_factory=list)
    claims: List[GraphClaim] = Field(default_factory=list)
    relationships: List[GraphRelationship] = Field(default_factory=list)
    contradictions: List[GraphContradiction] = Field(default_factory=list)
    research_gaps: List[GraphResearchGap] = Field(default_factory=list)
