"""Domain models for autonomous research runs."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    """Epistemic classification for research claims."""

    KNOWN = "KNOWN"
    SUPPORTED = "SUPPORTED"
    SPECULATIVE = "SPECULATIVE"
    DISPROVED = "DISPROVED"
    UNVERIFIED = "UNVERIFIED"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"


class ResearchPhase(str, Enum):
    DECOMPOSE = "decompose"
    RETRIEVE = "retrieve"
    SYNTHESIZE = "synthesize"
    IDENTIFY_GAPS = "identify_gaps"
    HYPOTHESIZE = "hypothesize"
    RANK = "rank"
    ATTEMPT = "attempt"
    CRITICIZE = "criticize"
    VERIFY = "verify"
    ANALYZE_FAILURE = "analyze_failure"
    REPLAN = "replan"
    REPORT = "report"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=_new_id)
    source: str
    content: str
    claim_status: ClaimStatus = ClaimStatus.SUPPORTED
    confidence: float = 0.7
    iteration: int = 0
    worker_role: str = ""


class ResearchClaim(BaseModel):
    id: str = Field(default_factory=_new_id)
    statement: str
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    iteration: int = 0
    provenance: str = ""


class HypothesisCandidate(BaseModel):
    id: str = Field(default_factory=_new_id)
    statement: str
    rationale: str = ""
    score: float = 0.0
    rank: int = 0
    status: ClaimStatus = ClaimStatus.SPECULATIVE
    iteration: int = 0
    rejected: bool = False
    rejection_reason: str = ""


class FailedAttemptRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    approach: str
    reason_attempted: str
    evidence_considered: list[str] = Field(default_factory=list)
    failure_reason: str
    critic_feedback: str = ""
    learned: str = ""
    reuse_conditions: str = ""
    iteration: int = 0
    fingerprint: str = ""


class ExperimentRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    description: str
    method: str = ""
    result: str = ""
    success: bool = False
    iteration: int = 0


class CriticismRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    target_id: str
    target_type: str
    criticism: str
    severity: str = "medium"
    iteration: int = 0


class ResearchRunConfig(BaseModel):
    max_iterations: int = 5
    require_approval_before_attempt: bool = False
    benchmark_id: Optional[str] = None
    project_id: Optional[str] = None
    parallel_workers: bool = True
    stop_on_supported_solution: bool = True


class ResearchState(BaseModel):
    """Structured state for a single research run."""

    run_id: str
    workflow_id: str = ""
    research_question: str
    current_phase: ResearchPhase = ResearchPhase.DECOMPOSE
    current_iteration: int = 1
    max_iterations: int = 5

    subproblems: list[str] = Field(default_factory=list)
    known_facts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    claims: list[ResearchClaim] = Field(default_factory=list)
    hypotheses: list[HypothesisCandidate] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)
    failed_attempts: list[FailedAttemptRecord] = Field(default_factory=list)
    experiments: list[ExperimentRecord] = Field(default_factory=list)
    results: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    sources: list[str] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)

    active_workers: list[str] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    final_report: str = ""
    benchmark_id: Optional[str] = None
    human_interventions: int = 0

    def add_timeline(self, phase: ResearchPhase, detail: str, worker: str = "") -> None:
        self.timeline.append({
            "phase": phase.value,
            "detail": detail,
            "worker": worker,
            "iteration": self.current_iteration,
            "timestamp": _utc_now().isoformat(),
        })

    def hypothesis_fingerprints(self) -> set[str]:
        return {h.statement.strip().lower() for h in self.hypotheses}

    def failed_approach_fingerprints(self) -> set[str]:
        return {f.fingerprint or f.approach.strip().lower() for f in self.failed_attempts}


class BenchmarkScore(BaseModel):
    benchmark_id: str
    run_id: str
    solution_correctness: float
    route_novelty: float
    evidence_quality: float
    iterations_used: int
    failed_approaches: int
    recovery_from_failure: bool
    human_interventions: int
    model_calls: int = 0
    duration_seconds: float = 0.0
    hidden_solution_match: float = 0.0
    notes: str = ""
