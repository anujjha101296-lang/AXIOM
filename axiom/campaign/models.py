"""Frontier Research Campaign Engine (FRCE) — domain models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str = "frce") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class CampaignPhase(str, Enum):
    """Explicit campaign state machine (FRCE §3)."""

    PROPOSED = "PROPOSED"
    SCOPED = "SCOPED"
    RESEARCHING = "RESEARCHING"
    HYPOTHESIS_GENERATION = "HYPOTHESIS_GENERATION"
    INVESTIGATION = "INVESTIGATION"
    VERIFICATION = "VERIFICATION"
    REVIEW = "REVIEW"
    # Terminal / pause states
    SUCCESSFUL_CONTRIBUTION = "SUCCESSFUL_CONTRIBUTION"
    PARTIAL_PROGRESS = "PARTIAL_PROGRESS"
    EXHAUSTED = "EXHAUSTED"
    BLOCKED = "BLOCKED"
    DISPROVED = "DISPROVED"
    ABANDONED = "ABANDONED"
    PAUSED = "PAUSED"


class PivotDecision(str, Enum):
    CONTINUE = "CONTINUE"
    PIVOT = "PIVOT"
    ESCALATE = "ESCALATE"
    PAUSE = "PAUSE"
    ABANDON = "ABANDON"


class ResearchRole(str, Enum):
    """Multi-agent research organization roles (FRCE §6)."""

    PRINCIPAL_INVESTIGATOR = "principal_investigator"
    LITERATURE_RESEARCHER = "literature_researcher"
    MATHEMATICIAN = "mathematician"
    COMPUTATIONAL_RESEARCHER = "computational_researcher"
    FORMALIZATION_SPECIALIST = "formalization_specialist"
    COUNTEREXAMPLE_HUNTER = "counterexample_hunter"
    SKEPTICAL_REVIEWER = "skeptical_reviewer"
    INDEPENDENT_REPLICATOR = "independent_replicator"
    RESEARCH_STRATEGIST = "research_strategist"
    RESEARCH_ARCHIVIST = "research_archivist"


class ContributionLevel(str, Enum):
    """Graduated success scale (FRCE §15) — not binary solved/failed."""

    NO_PROGRESS = "no_progress"
    USEFUL_OBSERVATION = "useful_observation"
    NEW_CONJECTURE = "new_conjecture"
    COUNTEREXAMPLE = "counterexample"
    NEW_LEMMA = "new_lemma"
    VERIFIED_LEMMA = "verified_lemma"
    PARTIAL_THEOREM = "partial_theorem"
    NEW_METHOD = "new_method"
    PUBLISHED_CONTRIBUTION = "published_contribution"
    MAJOR_BREAKTHROUGH = "major_breakthrough"
    POTENTIAL_COMPLETE_SOLUTION = "potential_complete_solution"


class LadderLevel(int, Enum):
    """Challenge ladder levels 0–9 (FRCE §14)."""

    LEVEL_0_SIMPLE_REASONING = 0
    LEVEL_1_KNOWN_ANSWER_MATH = 1
    LEVEL_2_FORMAL_REPRODUCTION = 2
    LEVEL_3_PUBLISHED_REPRODUCTION = 3
    LEVEL_4_RESEARCH_BENCHMARK = 4
    LEVEL_5_SMALL_OPEN = 5
    LEVEL_6_OPEN_SUBPROBLEM = 6
    LEVEL_7_MAJOR_OPEN = 7
    LEVEL_8_FRONTIER = 8
    LEVEL_9_MILLENNIUM = 9


class GraphNodeType(str, Enum):
    MAIN_PROBLEM = "main_problem"
    SUBPROBLEM = "subproblem"
    LEMMA = "lemma"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    PROOF_ATTEMPT = "proof_attempt"
    COUNTEREXAMPLE = "counterexample"
    EVIDENCE = "evidence"
    OPEN_QUESTION = "open_question"


class GraphNodeStatus(str, Enum):
    UNKNOWN = "unknown"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    VERIFIED = "verified"
    EXHAUSTED = "exhausted"


_VALID_TRANSITIONS: dict[CampaignPhase, set[CampaignPhase]] = {
    CampaignPhase.PROPOSED: {CampaignPhase.SCOPED, CampaignPhase.ABANDONED},
    CampaignPhase.SCOPED: {CampaignPhase.RESEARCHING, CampaignPhase.PAUSED, CampaignPhase.ABANDONED},
    CampaignPhase.RESEARCHING: {
        CampaignPhase.HYPOTHESIS_GENERATION,
        CampaignPhase.INVESTIGATION,
        CampaignPhase.PAUSED,
        CampaignPhase.ABANDONED,
    },
    CampaignPhase.HYPOTHESIS_GENERATION: {
        CampaignPhase.INVESTIGATION,
        CampaignPhase.RESEARCHING,
        CampaignPhase.PAUSED,
    },
    CampaignPhase.INVESTIGATION: {
        CampaignPhase.VERIFICATION,
        CampaignPhase.REVIEW,
        CampaignPhase.RESEARCHING,
        CampaignPhase.PAUSED,
    },
    CampaignPhase.VERIFICATION: {
        CampaignPhase.REVIEW,
        CampaignPhase.INVESTIGATION,
        CampaignPhase.PAUSED,
    },
    CampaignPhase.REVIEW: {
        CampaignPhase.RESEARCHING,
        CampaignPhase.PARTIAL_PROGRESS,
        CampaignPhase.SUCCESSFUL_CONTRIBUTION,
        CampaignPhase.EXHAUSTED,
        CampaignPhase.BLOCKED,
        CampaignPhase.DISPROVED,
        CampaignPhase.ABANDONED,
        CampaignPhase.PAUSED,
    },
    CampaignPhase.PAUSED: {CampaignPhase.RESEARCHING, CampaignPhase.ABANDONED},
}

_VALID_TRANSITIONS[CampaignPhase.PARTIAL_PROGRESS] = {CampaignPhase.RESEARCHING, CampaignPhase.PAUSED}
_VALID_TRANSITIONS[CampaignPhase.SUCCESSFUL_CONTRIBUTION] = set()
_VALID_TRANSITIONS[CampaignPhase.EXHAUSTED] = {CampaignPhase.RESEARCHING, CampaignPhase.ABANDONED}
_VALID_TRANSITIONS[CampaignPhase.BLOCKED] = {CampaignPhase.RESEARCHING, CampaignPhase.ABANDONED, CampaignPhase.PAUSED}
_VALID_TRANSITIONS[CampaignPhase.DISPROVED] = set()
_VALID_TRANSITIONS[CampaignPhase.ABANDONED] = set()


def can_transition(from_phase: CampaignPhase, to_phase: CampaignPhase) -> bool:
    return to_phase in _VALID_TRANSITIONS.get(from_phase, set())


@dataclass
class ResourceBudget:
    """Campaign resource budget (FRCE §8, §19)."""

    time_seconds: float = 3600.0
    compute_units: float = 100.0
    model_calls: int = 50
    tool_calls: int = 50
    storage_mb: float = 500.0
    human_review_slots: int = 3
    monetary_usd: float = 0.0
    exploration_fraction: float = 0.2  # reserve for exploration vs exploitation

    consumed: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_seconds": self.time_seconds,
            "compute_units": self.compute_units,
            "model_calls": self.model_calls,
            "tool_calls": self.tool_calls,
            "storage_mb": self.storage_mb,
            "human_review_slots": self.human_review_slots,
            "monetary_usd": self.monetary_usd,
            "exploration_fraction": self.exploration_fraction,
            "consumed": self.consumed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResourceBudget:
        return cls(
            time_seconds=float(data.get("time_seconds", 3600.0)),
            compute_units=float(data.get("compute_units", 100.0)),
            model_calls=int(data.get("model_calls", 50)),
            tool_calls=int(data.get("tool_calls", 50)),
            storage_mb=float(data.get("storage_mb", 500.0)),
            human_review_slots=int(data.get("human_review_slots", 3)),
            monetary_usd=float(data.get("monetary_usd", 0.0)),
            exploration_fraction=float(data.get("exploration_fraction", 0.2)),
            consumed=dict(data.get("consumed", {})),
        )

    def budget_exceeded(self) -> bool:
        c = self.consumed
        return (
            c.get("time_seconds", 0) > self.time_seconds
            or c.get("compute_units", 0) > self.compute_units
            or c.get("model_calls", 0) > self.model_calls
            or c.get("tool_calls", 0) > self.tool_calls
        )


@dataclass
class ResearchGraphNode:
    """Node in the live research graph (FRCE §5)."""

    node_id: str
    node_type: GraphNodeType
    title: str
    status: GraphNodeStatus = GraphNodeStatus.UNKNOWN
    confidence: float = 0.5
    dependencies: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    owner_role: ResearchRole | None = None
    next_action: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "title": self.title,
            "status": self.status.value,
            "confidence": self.confidence,
            "dependencies": self.dependencies,
            "evidence_ids": self.evidence_ids,
            "owner_role": self.owner_role.value if self.owner_role else None,
            "next_action": self.next_action,
            "provenance": self.provenance,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchGraphNode:
        return cls(
            node_id=data["node_id"],
            node_type=GraphNodeType(data["node_type"]),
            title=data["title"],
            status=GraphNodeStatus(data.get("status", "unknown")),
            confidence=float(data.get("confidence", 0.5)),
            dependencies=list(data.get("dependencies", [])),
            evidence_ids=list(data.get("evidence_ids", [])),
            owner_role=ResearchRole(data["owner_role"]) if data.get("owner_role") else None,
            next_action=data.get("next_action", ""),
            provenance=dict(data.get("provenance", {})),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ResearchStrategy:
    """A competing research strategy (FRCE §7)."""

    strategy_id: str
    name: str
    description: str
    probability_of_progress: float = 0.3
    estimated_cost: float = 1.0
    estimated_runtime_minutes: float = 30.0
    discrimination_score: float = 0.5
    status: str = "active"  # active, exhausted, selected, abandoned
    execution_plan: dict[str, Any] = field(default_factory=dict)
    linked_node_ids: list[str] = field(default_factory=list)
    workers_allocated: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "probability_of_progress": self.probability_of_progress,
            "estimated_cost": self.estimated_cost,
            "estimated_runtime_minutes": self.estimated_runtime_minutes,
            "discrimination_score": self.discrimination_score,
            "status": self.status,
            "execution_plan": self.execution_plan,
            "linked_node_ids": self.linked_node_ids,
            "workers_allocated": self.workers_allocated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchStrategy:
        return cls(
            strategy_id=data["strategy_id"],
            name=data["name"],
            description=data["description"],
            probability_of_progress=float(data.get("probability_of_progress", 0.3)),
            estimated_cost=float(data.get("estimated_cost", 1.0)),
            estimated_runtime_minutes=float(data.get("estimated_runtime_minutes", 30.0)),
            discrimination_score=float(data.get("discrimination_score", 0.5)),
            status=data.get("status", "active"),
            execution_plan=dict(data.get("execution_plan", {})),
            linked_node_ids=list(data.get("linked_node_ids", [])),
            workers_allocated=int(data.get("workers_allocated", 1)),
        )


@dataclass
class CampaignHypothesis:
    hypothesis_id: str
    statement: str
    confidence: float = 0.5
    status: str = "active"
    claim_id: str | None = None
    evidence_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "confidence": self.confidence,
            "status": self.status,
            "claim_id": self.claim_id,
            "evidence_ids": self.evidence_ids,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CampaignHypothesis:
        return cls(
            hypothesis_id=data["hypothesis_id"],
            statement=data["statement"],
            confidence=float(data.get("confidence", 0.5)),
            status=data.get("status", "active"),
            claim_id=data.get("claim_id"),
            evidence_ids=list(data.get("evidence_ids", [])),
            created_at=data.get("created_at", _utc_now()),
        )


@dataclass
class CampaignCheckpoint:
    """Immutable research checkpoint (FRCE §10)."""

    checkpoint_id: str
    sequence: int
    title: str
    phase: str
    snapshot: dict[str, Any]
    created_at: str = field(default_factory=_utc_now)
    immutable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "sequence": self.sequence,
            "title": self.title,
            "phase": self.phase,
            "snapshot": self.snapshot,
            "created_at": self.created_at,
            "immutable": self.immutable,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CampaignCheckpoint:
        return cls(
            checkpoint_id=data["checkpoint_id"],
            sequence=int(data["sequence"]),
            title=data["title"],
            phase=data["phase"],
            snapshot=dict(data.get("snapshot", {})),
            created_at=data.get("created_at", _utc_now()),
            immutable=bool(data.get("immutable", True)),
        )


@dataclass
class HumanGateRequest:
    """Human review gate trigger (FRCE §11)."""

    gate_id: str
    reason: str
    trigger: str
    status: str = "pending"  # pending, approved, rejected, deferred
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    resolved_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "reason": self.reason,
            "trigger": self.trigger,
            "status": self.status,
            "details": self.details,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HumanGateRequest:
        return cls(
            gate_id=data["gate_id"],
            reason=data["reason"],
            trigger=data["trigger"],
            status=data.get("status", "pending"),
            details=dict(data.get("details", {})),
            created_at=data.get("created_at", _utc_now()),
            resolved_at=data.get("resolved_at"),
        )


@dataclass
class CycleRecord:
    """One iteration of the permanent campaign loop (FRCE §17)."""

    cycle_id: str
    cycle_number: int
    started_at: str
    completed_at: str | None = None
    learned: list[str] = field(default_factory=list)
    failed_approaches: list[str] = field(default_factory=list)
    pivot_decision: PivotDecision | None = None
    contribution_level: ContributionLevel = ContributionLevel.NO_PROGRESS
    experiment_ids: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)
    proof_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "cycle_number": self.cycle_number,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "learned": self.learned,
            "failed_approaches": self.failed_approaches,
            "pivot_decision": self.pivot_decision.value if self.pivot_decision else None,
            "contribution_level": self.contribution_level.value,
            "experiment_ids": self.experiment_ids,
            "claim_ids": self.claim_ids,
            "proof_ids": self.proof_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CycleRecord:
        return cls(
            cycle_id=data["cycle_id"],
            cycle_number=int(data["cycle_number"]),
            started_at=data["started_at"],
            completed_at=data.get("completed_at"),
            learned=list(data.get("learned", [])),
            failed_approaches=list(data.get("failed_approaches", [])),
            pivot_decision=PivotDecision(data["pivot_decision"]) if data.get("pivot_decision") else None,
            contribution_level=ContributionLevel(data.get("contribution_level", "no_progress")),
            experiment_ids=list(data.get("experiment_ids", [])),
            claim_ids=list(data.get("claim_ids", [])),
            proof_ids=list(data.get("proof_ids", [])),
        )


@dataclass
class ResearchMemoryEntry:
    """Institutional memory from a campaign iteration (FRCE §12)."""

    entry_id: str
    cycle_number: int
    what_learned: str
    what_failed: str
    assumptions_changed: str
    exhausted_approaches: list[str] = field(default_factory=list)
    promising_approaches: list[str] = field(default_factory=list)
    new_questions: list[str] = field(default_factory=list)
    tools_that_worked: list[str] = field(default_factory=list)
    models_that_failed: list[str] = field(default_factory=list)
    never_repeat: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "cycle_number": self.cycle_number,
            "what_learned": self.what_learned,
            "what_failed": self.what_failed,
            "assumptions_changed": self.assumptions_changed,
            "exhausted_approaches": self.exhausted_approaches,
            "promising_approaches": self.promising_approaches,
            "new_questions": self.new_questions,
            "tools_that_worked": self.tools_that_worked,
            "models_that_failed": self.models_that_failed,
            "never_repeat": self.never_repeat,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchMemoryEntry:
        return cls(
            entry_id=data["entry_id"],
            cycle_number=int(data["cycle_number"]),
            what_learned=data.get("what_learned", ""),
            what_failed=data.get("what_failed", ""),
            assumptions_changed=data.get("assumptions_changed", ""),
            exhausted_approaches=list(data.get("exhausted_approaches", [])),
            promising_approaches=list(data.get("promising_approaches", [])),
            new_questions=list(data.get("new_questions", [])),
            tools_that_worked=list(data.get("tools_that_worked", [])),
            models_that_failed=list(data.get("models_that_failed", [])),
            never_repeat=list(data.get("never_repeat", [])),
            created_at=data.get("created_at", _utc_now()),
        )


@dataclass
class FrontierCampaign:
    """First-class long-running research campaign (FRCE §2)."""

    campaign_id: str
    name: str
    objective: str
    problem_definition: str = ""
    domain: str = "mathematics"
    difficulty: str = "unknown"
    ladder_level: LadderLevel = LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH
    success_criteria: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    phase: CampaignPhase = CampaignPhase.PROPOSED
    contribution_level: ContributionLevel = ContributionLevel.NO_PROGRESS
    budget: ResourceBudget = field(default_factory=ResourceBudget)
    research_graph: list[ResearchGraphNode] = field(default_factory=list)
    strategies: list[ResearchStrategy] = field(default_factory=list)
    hypotheses: list[CampaignHypothesis] = field(default_factory=list)
    checkpoints: list[CampaignCheckpoint] = field(default_factory=list)
    human_gates: list[HumanGateRequest] = field(default_factory=list)
    cycles: list[CycleRecord] = field(default_factory=list)
    memory: list[ResearchMemoryEntry] = field(default_factory=list)
    journal: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    failed_approaches: list[str] = field(default_factory=list)
    # Cross-loop linkage IDs
    gcp_campaign_id: str | None = None
    experiment_ids: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)
    proof_ids: list[str] = field(default_factory=list)
    routing_plan_id: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "objective": self.objective,
            "problem_definition": self.problem_definition,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "ladder_level": int(self.ladder_level),
            "success_criteria": self.success_criteria,
            "constraints": self.constraints,
            "phase": self.phase.value,
            "contribution_level": self.contribution_level.value,
            "budget": self.budget.to_dict(),
            "research_graph": [n.to_dict() for n in self.research_graph],
            "strategies": [s.to_dict() for s in self.strategies],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "human_gates": [g.to_dict() for g in self.human_gates],
            "cycles": [c.to_dict() for c in self.cycles],
            "memory": [m.to_dict() for m in self.memory],
            "journal": self.journal,
            "decisions": self.decisions,
            "failed_approaches": self.failed_approaches,
            "gcp_campaign_id": self.gcp_campaign_id,
            "experiment_ids": self.experiment_ids,
            "claim_ids": self.claim_ids,
            "proof_ids": self.proof_ids,
            "routing_plan_id": self.routing_plan_id,
            "context": self.context,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FrontierCampaign:
        return cls(
            campaign_id=data["campaign_id"],
            name=data["name"],
            objective=data["objective"],
            problem_definition=data.get("problem_definition", ""),
            domain=data.get("domain", "mathematics"),
            difficulty=data.get("difficulty", "unknown"),
            ladder_level=LadderLevel(int(data.get("ladder_level", 1))),
            success_criteria=list(data.get("success_criteria", [])),
            constraints=list(data.get("constraints", [])),
            phase=CampaignPhase(data.get("phase", "PROPOSED")),
            contribution_level=ContributionLevel(data.get("contribution_level", "no_progress")),
            budget=ResourceBudget.from_dict(data.get("budget", {})),
            research_graph=[ResearchGraphNode.from_dict(n) for n in data.get("research_graph", [])],
            strategies=[ResearchStrategy.from_dict(s) for s in data.get("strategies", [])],
            hypotheses=[CampaignHypothesis.from_dict(h) for h in data.get("hypotheses", [])],
            checkpoints=[CampaignCheckpoint.from_dict(c) for c in data.get("checkpoints", [])],
            human_gates=[HumanGateRequest.from_dict(g) for g in data.get("human_gates", [])],
            cycles=[CycleRecord.from_dict(c) for c in data.get("cycles", [])],
            memory=[ResearchMemoryEntry.from_dict(m) for m in data.get("memory", [])],
            journal=list(data.get("journal", [])),
            decisions=list(data.get("decisions", [])),
            failed_approaches=list(data.get("failed_approaches", [])),
            gcp_campaign_id=data.get("gcp_campaign_id"),
            experiment_ids=list(data.get("experiment_ids", [])),
            claim_ids=list(data.get("claim_ids", [])),
            proof_ids=list(data.get("proof_ids", [])),
            routing_plan_id=data.get("routing_plan_id"),
            context=dict(data.get("context", {})),
            created_at=data.get("created_at", _utc_now()),
            updated_at=data.get("updated_at", _utc_now()),
        )
