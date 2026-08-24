"""
axiom.hypothesis.models
=======================
Pydantic Domain Models for Phase 14 Hypothesis & Scientific Reasoning Engine.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def generate_uuid() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    SUPPORTED = "SUPPORTED"
    WEAKLY_SUPPORTED = "WEAKLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    FALSIFIED = "FALSIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    RETIRED = "RETIRED"


class CritiqueStatus(str, Enum):
    VALID = "VALID"
    NEEDS_REVISION = "NEEDS_REVISION"
    UNFALSIFIABLE = "UNFALSIFIABLE"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ReasoningType(str, Enum):
    DEDUCTION = "DEDUCTION"
    INDUCTION = "INDUCTION"
    ABDUCTION = "ABDUCTION"
    HEURISTIC_INFERENCE = "HEURISTIC_INFERENCE"


class HypothesisEvidence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    hypothesis_id: str
    claim_id: Optional[str] = None
    chunk_id: Optional[str] = None
    source_id: Optional[str] = None
    supports: bool = True
    snippet: str = ""
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> HypothesisEvidence:
        return cls(
            id=db_obj.id,
            hypothesis_id=db_obj.hypothesis_id,
            claim_id=db_obj.claim_id,
            chunk_id=db_obj.chunk_id,
            source_id=db_obj.source_id,
            supports=db_obj.supports,
            snippet=db_obj.snippet,
            created_at=db_obj.created_at,
        )


class HypothesisPrediction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    hypothesis_id: str
    prediction_text: str
    expected_observation: str
    conditions: str = ""
    measurement: str = ""
    falsifying_observation: str = ""
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> HypothesisPrediction:
        return cls(
            id=db_obj.id,
            hypothesis_id=db_obj.hypothesis_id,
            prediction_text=db_obj.prediction_text,
            expected_observation=db_obj.expected_observation,
            conditions=db_obj.conditions,
            measurement=db_obj.measurement,
            falsifying_observation=db_obj.falsifying_observation,
            created_at=db_obj.created_at,
        )


class HypothesisCritique(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    hypothesis_id: str
    status: CritiqueStatus = CritiqueStatus.VALID
    critique_text: str
    unsupported_assumptions: List[str] = Field(default_factory=list)
    scope_errors: List[str] = Field(default_factory=list)
    is_falsifiable: bool = True
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> HypothesisCritique:
        unsupported = []
        scope_errs = []
        if hasattr(db_obj, "unsupported_assumptions_json") and db_obj.unsupported_assumptions_json:
            try:
                unsupported = json.loads(db_obj.unsupported_assumptions_json)
            except Exception:
                unsupported = []
        if hasattr(db_obj, "scope_errors_json") and db_obj.scope_errors_json:
            try:
                scope_errs = json.loads(db_obj.scope_errors_json)
            except Exception:
                scope_errs = []
        return cls(
            id=db_obj.id,
            hypothesis_id=db_obj.hypothesis_id,
            status=CritiqueStatus(db_obj.status),
            critique_text=db_obj.critique_text,
            unsupported_assumptions=unsupported,
            scope_errors=scope_errs,
            is_falsifiable=db_obj.is_falsifiable,
            created_at=db_obj.created_at,
        )


class HypothesisRevision(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    hypothesis_id: str
    revision_index: int = 1
    previous_claim: str
    new_claim: str
    reason: str
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> HypothesisRevision:
        return cls(
            id=db_obj.id,
            hypothesis_id=db_obj.hypothesis_id,
            revision_index=db_obj.revision_index,
            previous_claim=db_obj.previous_claim,
            new_claim=db_obj.new_claim,
            reason=db_obj.reason,
            created_at=db_obj.created_at,
        )


class VerificationPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    hypothesis_id: str
    project_id: str
    question: str
    hypothesis_summary: str
    required_evidence: List[str] = Field(default_factory=list)
    predictions: List[str] = Field(default_factory=list)
    method: str = "literature_research"
    data_sources: List[str] = Field(default_factory=list)
    success_criteria: str = ""
    failure_criteria: str = ""
    limitations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> VerificationPlan:
        def _parse_list(val: Any) -> List[str]:
            if not val:
                return []
            try:
                return json.loads(val)
            except Exception:
                return []

        return cls(
            id=db_obj.id,
            hypothesis_id=db_obj.hypothesis_id,
            project_id=db_obj.project_id,
            question=db_obj.question,
            hypothesis_summary=db_obj.hypothesis_summary,
            required_evidence=_parse_list(getattr(db_obj, "required_evidence_json", None)),
            predictions=_parse_list(getattr(db_obj, "predictions_json", None)),
            method=db_obj.method,
            data_sources=_parse_list(getattr(db_obj, "data_sources_json", None)),
            success_criteria=db_obj.success_criteria,
            failure_criteria=db_obj.failure_criteria,
            limitations=_parse_list(getattr(db_obj, "limitations_json", None)),
            created_at=db_obj.created_at,
        )


class Hypothesis(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    session_id: Optional[str] = None
    question_id: Optional[str] = None
    gap_id: Optional[str] = None
    claim: str
    motivation: str = ""
    assumptions: List[str] = Field(default_factory=list)
    verification_strategy: str = ""
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence_score: float = 0.5
    rationale: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    # Sub-objects
    evidences: List[HypothesisEvidence] = Field(default_factory=list)
    predictions: List[HypothesisPrediction] = Field(default_factory=list)
    critiques: List[HypothesisCritique] = Field(default_factory=list)
    revisions: List[HypothesisRevision] = Field(default_factory=list)
    verification_plan: Optional[VerificationPlan] = None

    @classmethod
    def from_db(cls, db_obj: Any) -> Hypothesis:
        assumptions = []
        meta = {}
        if hasattr(db_obj, "assumptions_json") and db_obj.assumptions_json:
            try:
                assumptions = json.loads(db_obj.assumptions_json)
            except Exception:
                assumptions = []
        if hasattr(db_obj, "metadata_json") and db_obj.metadata_json:
            try:
                meta = json.loads(db_obj.metadata_json)
            except Exception:
                meta = {}

        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            session_id=db_obj.session_id,
            question_id=db_obj.question_id,
            gap_id=db_obj.gap_id,
            claim=db_obj.claim,
            motivation=db_obj.motivation,
            assumptions=assumptions,
            verification_strategy=db_obj.verification_strategy,
            status=HypothesisStatus(db_obj.status),
            confidence_score=db_obj.confidence_score,
            rationale=db_obj.rationale,
            metadata=meta,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )


class HypothesisSummary(BaseModel):
    project_id: str
    total_hypotheses: int = 0
    hypotheses: List[Hypothesis] = Field(default_factory=list)
