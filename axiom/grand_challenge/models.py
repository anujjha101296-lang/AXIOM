"""AXIOM Grand Challenge Program — domain models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())[:12]


class ChallengeTier(int, Enum):
    """Six permanent challenge tiers — educational to frontier."""

    TIER_0_TOY = 0
    TIER_1_KNOWN_ANSWER = 1
    TIER_2_PAPER_REPRODUCTION = 2
    TIER_3_SMALL_OPEN = 3
    TIER_4_DOMAIN_GRAND = 4
    TIER_5_FRONTIER = 5


TIER_DESCRIPTIONS: dict[ChallengeTier, str] = {
    ChallengeTier.TIER_0_TOY: "Toy reasoning problems — infrastructure and pipeline validation",
    ChallengeTier.TIER_1_KNOWN_ANSWER: "Known-answer theorem and proof tasks — hidden ground truth",
    ChallengeTier.TIER_2_PAPER_REPRODUCTION: "Research paper reproduction — methodology replication",
    ChallengeTier.TIER_3_SMALL_OPEN: "Small open research questions — bounded novelty",
    ChallengeTier.TIER_4_DOMAIN_GRAND: "Domain grand challenges — multi-year scientific campaigns",
    ChallengeTier.TIER_5_FRONTIER: "Frontier open problems — capability tests, not prize claims",
}


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ExperimentStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceTier(str, Enum):
    """How evidence was produced — never conflated with formal proof."""

    MEASURED = "measured"
    SIMULATED = "simulated"
    HEURISTIC = "heuristic"
    BASELINE = "baseline"
    UNAVAILABLE = "unavailable"


class ChallengeDefinition(BaseModel):
    """Full specification for a single challenge."""

    challenge_id: str
    tier: ChallengeTier
    title: str
    objective: str
    domain: str
    difficulty: str
    required_capabilities: list[str]
    required_tools: list[str]
    verification_method: str
    success_criteria: list[str]
    failure_criteria: list[str]
    benchmark_metrics: list[str]
    human_review_process: str
    benchmark_refs: list[str] = Field(default_factory=list)
    evidence_tier: EvidenceTier = EvidenceTier.BASELINE
    notes: str = ""


class HypothesisRecord(BaseModel):
    hypothesis_id: str = Field(default_factory=_new_id)
    statement: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    status: str = "active"  # active, supported, refuted, inconclusive
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utcnow)


class ExperimentRecord(BaseModel):
    experiment_id: str = Field(default_factory=_new_id)
    challenge_id: str
    title: str
    status: ExperimentStatus = ExperimentStatus.PLANNED
    hypothesis_id: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    evidence_tier: EvidenceTier = EvidenceTier.UNAVAILABLE
    score: float | None = None
    passed: bool | None = None
    notes: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None


class EvidenceRecord(BaseModel):
    evidence_id: str = Field(default_factory=_new_id)
    source: str
    evidence_type: str
    content: str
    evidence_tier: EvidenceTier
    experiment_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utcnow)


class JournalEntry(BaseModel):
    entry_id: str = Field(default_factory=_new_id)
    title: str
    content: str
    phase: str = "observation"
    experiment_id: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)


class CampaignCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=_new_id)
    tier: ChallengeTier
    challenges_completed: list[str] = Field(default_factory=list)
    experiments_completed: int = 0
    evidence_count: int = 0
    context_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utcnow)


class Campaign(BaseModel):
    """Long-running scientific campaign across one or more challenge tiers."""

    campaign_id: str = Field(default_factory=_new_id)
    name: str
    description: str = ""
    current_tier: ChallengeTier = ChallengeTier.TIER_0_TOY
    target_tier: ChallengeTier = ChallengeTier.TIER_1_KNOWN_ANSWER
    status: CampaignStatus = CampaignStatus.DRAFT
    challenge_ids: list[str] = Field(default_factory=list)
    challenges_completed: list[str] = Field(default_factory=list)
    hypotheses: list[HypothesisRecord] = Field(default_factory=list)
    experiments: list[ExperimentRecord] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    journal: list[JournalEntry] = Field(default_factory=list)
    checkpoints: list[CampaignCheckpoint] = Field(default_factory=list)
    workflow_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def progress_fraction(self) -> float:
        if not self.challenge_ids:
            return 0.0
        return len(self.challenges_completed) / len(self.challenge_ids)
