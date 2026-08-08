"""RVP data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class ValidationStage(IntEnum):
    """Staged validation framework (0–6)."""

    INFRASTRUCTURE = 0
    KNOWN_ANSWER = 1
    PAPER_REPRODUCTION = 2
    RESEARCH_ASSISTANT = 3
    SMALL_OPEN_PROBLEMS = 4
    LONG_RUNNING_AUTONOMOUS = 5
    PRIZE_PREPARATION = 6


STAGE_DESCRIPTIONS: dict[ValidationStage, str] = {
    ValidationStage.INFRASTRUCTURE: "Infrastructure validation — pipelines, storage, replay, scoring",
    ValidationStage.KNOWN_ANSWER: "Known-answer scientific problems — hidden ground truth",
    ValidationStage.PAPER_REPRODUCTION: "Research paper reproduction tasks",
    ValidationStage.RESEARCH_ASSISTANT: "Research assistant evaluation on realistic workflows",
    ValidationStage.SMALL_OPEN_PROBLEMS: "Small open problems with partial evidence",
    ValidationStage.LONG_RUNNING_AUTONOMOUS: "Long-running autonomous research sessions",
    ValidationStage.PRIZE_PREPARATION: "Prize-problem preparation benchmarks",
}


@dataclass
class KnownAnswerProblem:
    """Benchmark problem; hidden answer never exposed during execution."""

    id: str
    stage: int
    category: str
    title: str
    problem_statement: str
    difficulty: str
    hidden_answer: str
    answer_keywords: list[str]
    evaluation_notes: str = ""

    def public_dict(self) -> dict[str, Any]:
        """Problem payload safe to show during a run (no hidden answer)."""
        return {
            "id": self.id,
            "stage": self.stage,
            "category": self.category,
            "title": self.title,
            "problem_statement": self.problem_statement,
            "difficulty": self.difficulty,
        }


@dataclass
class ResearchCapabilityScore:
    """Unified Research Capability Score — 10 dimensions, 0.0–1.0 each."""

    problem_understanding: float = 0.0
    planning: float = 0.0
    literature_retrieval: float = 0.0
    knowledge_integration: float = 0.0
    reasoning: float = 0.0
    evidence_quality: float = 0.0
    verification: float = 0.0
    recovery_from_failure: float = 0.0
    reproducibility: float = 0.0
    human_intervention_required: float = 0.0  # lower is better; inverted in composite

    DIMENSIONS: tuple[str, ...] = (
        "problem_understanding",
        "planning",
        "literature_retrieval",
        "knowledge_integration",
        "reasoning",
        "evidence_quality",
        "verification",
        "recovery_from_failure",
        "reproducibility",
        "human_intervention_required",
    )

    def composite(self) -> float:
        """Weighted composite; human_intervention inverted (1 - value)."""
        values = [
            self.problem_understanding,
            self.planning,
            self.literature_retrieval,
            self.knowledge_integration,
            self.reasoning,
            self.evidence_quality,
            self.verification,
            self.recovery_from_failure,
            self.reproducibility,
            1.0 - self.human_intervention_required,
        ]
        return round(sum(values) / len(values), 4)

    def to_dict(self) -> dict[str, float]:
        data = {d: round(getattr(self, d), 4) for d in self.DIMENSIONS}
        data["composite"] = self.composite()
        return data


@dataclass
class DiscoveryPipelineOutput:
    """Artifacts produced by every completed research run."""

    research_report: str
    reasoning_tree: dict[str, Any]
    evidence_graph: dict[str, Any]
    hypothesis_list: list[str]
    rejected_hypotheses: list[str]
    failed_attempts: list[dict[str, Any]]
    lessons_learned: list[str]
    confidence_estimates: dict[str, float]
    future_work: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "research_report": self.research_report,
            "reasoning_tree": self.reasoning_tree,
            "evidence_graph": self.evidence_graph,
            "hypothesis_list": self.hypothesis_list,
            "rejected_hypotheses": self.rejected_hypotheses,
            "failed_attempts": self.failed_attempts,
            "lessons_learned": self.lessons_learned,
            "confidence_estimates": self.confidence_estimates,
            "future_work": self.future_work,
        }


@dataclass
class ResearchRunConfig:
    """Reproducible run configuration."""

    stage: int
    problem_ids: list[str]
    seed: int = 42
    max_attempts: int = 3
    enable_verification: bool = True
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "problem_ids": self.problem_ids,
            "seed": self.seed,
            "max_attempts": self.max_attempts,
            "enable_verification": self.enable_verification,
            "tags": self.tags,
        }


@dataclass
class ResearchRunResult:
    """Complete result of one validation run."""

    run_id: str
    config_hash: str
    timestamp: str
    stage: int
    problem_id: str
    config: dict[str, Any]
    capability_score: ResearchCapabilityScore
    answer_score: float
    passed: bool
    pipeline: DiscoveryPipelineOutput
    provenance: dict[str, Any]
    cost_ms: float
    latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "config_hash": self.config_hash,
            "timestamp": self.timestamp,
            "stage": self.stage,
            "problem_id": self.problem_id,
            "config": self.config,
            "capability_score": self.capability_score.to_dict(),
            "answer_score": self.answer_score,
            "passed": self.passed,
            "pipeline": self.pipeline.to_dict(),
            "provenance": self.provenance,
            "cost_ms": self.cost_ms,
            "latency_ms": self.latency_ms,
        }
