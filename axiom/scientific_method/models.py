"""Scientific Method Engine — domain models for the 10-phase research workflow."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())[:12]


class SMEPhase(str, Enum):
    """Mandatory phases — executed in order; no phase may be skipped."""

    PROBLEM_DEFINITION = "problem_definition"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    KNOWLEDGE_GRAPH_CONSTRUCTION = "knowledge_graph_construction"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    CRITICISM = "criticism"
    EXPERIMENTATION = "experimentation"
    VERIFICATION = "verification"
    REFLECTION = "reflection"
    RESEARCH_MEMORY = "research_memory"
    HUMAN_REVIEW = "human_review"


PHASE_ORDER: list[SMEPhase] = list(SMEPhase)


class SMESessionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ClaimVerificationStatus(str, Enum):
    VERIFIED = "verified"
    SUPPORTED = "supported"
    SPECULATIVE = "speculative"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class ProblemDefinition(BaseModel):
    research_question: str
    assumptions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class KnowledgeSource(BaseModel):
    source_id: str = Field(default_factory=_new_id)
    source_type: str  # literature, formal_definition, proof, counterexample, dataset, failure, conjecture
    title: str
    reference: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompetingHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=_new_id)
    statement: str
    reasoning: str
    supporting_evidence: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class CriticismReport(BaseModel):
    hypothesis_id: str
    critic_id: str = Field(default_factory=_new_id)
    contradictions: list[str] = Field(default_factory=list)
    missing_assumptions: list[str] = Field(default_factory=list)
    counterexample_candidates: list[str] = Field(default_factory=list)
    literature_conflicts: list[str] = Field(default_factory=list)
    severity: float = Field(ge=0.0, le=1.0, default=0.5)


class ExperimentDesign(BaseModel):
    experiment_id: str = Field(default_factory=_new_id)
    hypothesis_id: str
    domain_method: str  # mathematics, simulation, search, programming, data_analysis, formal_verification
    description: str
    discriminates_between: list[str] = Field(default_factory=list)
    expected_outcomes: dict[str, str] = Field(default_factory=dict)


class VerifiedClaim(BaseModel):
    claim_id: str = Field(default_factory=_new_id)
    statement: str
    status: ClaimVerificationStatus
    evidence_summary: str = ""
    evidence_mode: str = "heuristic"


class ReflectionEntry(BaseModel):
    learned: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)
    assumptions_changed: list[str] = Field(default_factory=list)
    new_questions: list[str] = Field(default_factory=list)


class MemoryRecord(BaseModel):
    record_id: str = Field(default_factory=_new_id)
    category: str  # failed_strategy, successful_strategy, insight, journal, decision
    content: str
    phase: SMEPhase | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HumanReviewPackage(BaseModel):
    research_notebook: str
    evidence_graph_summary: dict[str, Any] = Field(default_factory=dict)
    reasoning_timeline: list[dict[str, Any]] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    recommended_experiments: list[str] = Field(default_factory=list)


class PhaseResult(BaseModel):
    phase: SMEPhase
    completed: bool
    started_at: datetime = Field(default_factory=_utcnow)
    completed_at: datetime | None = None
    artifacts: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class SMESession(BaseModel):
    session_id: str = Field(default_factory=_new_id)
    objective: str
    domain: str = "research"
    status: SMESessionStatus = SMESessionStatus.PENDING
    current_phase: SMEPhase = SMEPhase.PROBLEM_DEFINITION
    phases_completed: list[SMEPhase] = Field(default_factory=list)
    workflow_id: str | None = None
    problem: ProblemDefinition | None = None
    knowledge_sources: list[KnowledgeSource] = Field(default_factory=list)
    knowledge_graph_summary: dict[str, Any] = Field(default_factory=dict)
    hypotheses: list[CompetingHypothesis] = Field(default_factory=list)
    criticisms: list[CriticismReport] = Field(default_factory=list)
    experiments: list[ExperimentDesign] = Field(default_factory=list)
    verified_claims: list[VerifiedClaim] = Field(default_factory=list)
    reflection: ReflectionEntry | None = None
    memory_records: list[MemoryRecord] = Field(default_factory=list)
    human_review: HumanReviewPackage | None = None
    phase_results: list[PhaseResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("hypotheses")
    @classmethod
    def require_multiple_hypotheses_when_present(cls, v: list[CompetingHypothesis]) -> list[CompetingHypothesis]:
        return v

    def next_phase(self) -> SMEPhase | None:
        if self.current_phase in self.phases_completed:
            idx = PHASE_ORDER.index(self.current_phase)
            if idx + 1 < len(PHASE_ORDER):
                return PHASE_ORDER[idx + 1]
            return None
        return self.current_phase

    def is_complete(self) -> bool:
        return len(self.phases_completed) == len(PHASE_ORDER)
