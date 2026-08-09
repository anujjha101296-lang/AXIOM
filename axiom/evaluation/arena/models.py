"""Research Benchmark Arena — first-class models.

Conservative: scores are measured; higher tiers require gate evidence.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def _utc_now() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ArenaCategory(str, Enum):
    REASONING = "REASONING"
    RESEARCH = "RESEARCH"
    MATHEMATICS = "MATHEMATICS"
    FORMAL_MATHEMATICS = "FORMAL_MATHEMATICS"
    SCIENCE = "SCIENCE"
    EXPERIMENTATION = "EXPERIMENTATION"
    CODING = "CODING"
    REPRODUCTION = "REPRODUCTION"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    KNOWLEDGE = "KNOWLEDGE"
    AGENT_ORCHESTRATION = "AGENT_ORCHESTRATION"
    SECURITY = "SECURITY"
    LONG_HORIZON = "LONG_HORIZON"
    SCIENTIFIC_HONESTY = "SCIENTIFIC_HONESTY"
    TOOL_SELECTION = "TOOL_SELECTION"
    MEMORY = "MEMORY"
    ADVERSARIAL = "ADVERSARIAL"


class ArenaTier(int, Enum):
    T0_BASIC_REASONING = 0
    T1_KNOWN_ANSWER = 1
    T2_DIFFICULT_REASONING = 2
    T3_MATHEMATICAL = 3
    T4_FORMAL_PROVING = 4
    T5_REPRODUCTION = 5
    T6_ADVERSARIAL = 6
    T7_SMALL_OPEN = 7
    T8_OPEN_SUBPROBLEM = 8
    T9_FRONTIER = 9
    T10_MILLENNIUM = 10


class TaskType(str, Enum):
    KNOWN_ANSWER = "KNOWN_ANSWER"
    ADVERSARIAL = "ADVERSARIAL"
    FALSE_DISCOVERY = "FALSE_DISCOVERY"
    REPRODUCTION = "REPRODUCTION"
    MATHEMATICS = "MATHEMATICS"
    FORMAL = "FORMAL"
    RESEARCH_AGENT = "RESEARCH_AGENT"
    MULTI_AGENT = "MULTI_AGENT"
    LONG_HORIZON = "LONG_HORIZON"
    TOOL = "TOOL"
    MEMORY = "MEMORY"
    HONESTY = "HONESTY"
    SECURITY = "SECURITY"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"


class ArenaCaseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    HELD_OUT = "HELD_OUT"


@dataclass
class ArenaBenchmark:
    """Public catalog entry — never includes ground-truth answers."""

    benchmark_id: str
    title: str
    domain: str
    difficulty: str
    task_type: TaskType
    category: ArenaCategory
    tier: int
    question: str
    inputs: dict[str, Any] = field(default_factory=dict)
    allowed_tools: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    time_budget_seconds: float = 30.0
    compute_budget: str = "cpu_light"
    scoring_method: str = "deterministic_grader"
    version: str = "1"
    dataset_version: str = "arena_v1"
    status: ArenaCaseStatus = ArenaCaseStatus.ACTIVE
    # Evaluation criteria labels only (no answers)
    evaluation_labels: list[str] = field(default_factory=list)

    def public_dict(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "title": self.title,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "task_type": self.task_type.value,
            "category": self.category.value,
            "tier": self.tier,
            "question": self.question,
            "inputs": {k: v for k, v in self.inputs.items() if not str(k).startswith("_")},
            "allowed_tools": self.allowed_tools,
            "required_evidence": self.required_evidence,
            "time_budget_seconds": self.time_budget_seconds,
            "compute_budget": self.compute_budget,
            "scoring_method": self.scoring_method,
            "version": self.version,
            "dataset_version": self.dataset_version,
            "status": self.status.value,
            "evaluation_labels": self.evaluation_labels,
            # Explicit: answers not included
            "ground_truth_exposed": False,
        }


@dataclass
class CaseResult:
    benchmark_id: str
    score: float
    passed: bool
    time_ms: float
    notes: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "score": self.score,
            "passed": self.passed,
            "time_ms": self.time_ms,
            "notes": self.notes,
            "metrics": self.metrics,
            "error": self.error,
        }


@dataclass
class DimensionScores:
    """Multidimensional score — not reduced to one unexplained number."""

    correctness: float = 0.0
    evidence: float = 0.0
    citation: float = 0.0
    reasoning: float = 0.0
    research_depth: float = 0.0
    research_breadth: float = 0.0
    novelty_assessment: float = 0.0
    counterexample_detection: float = 0.0
    reproduction: float = 0.0
    formal_verification: float = 0.0
    scientific_honesty: float = 0.0
    reliability: float = 0.0
    cost: float = 0.0
    latency: float = 0.0
    security: float = 0.0
    long_horizon: float = 0.0
    false_discovery_rate: float = 0.0
    false_confidence_rate: float = 0.0
    hallucination_rate: float = 0.0
    unsupported_claim_rate: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {k: float(v) for k, v in self.__dict__.items()}


@dataclass
class ArenaRun:
    run_id: str
    dataset_version: str
    git_commit: str
    axiom_version: str
    environment: str
    configuration: dict[str, Any]
    started_at: str
    ended_at: str = ""
    results: list[CaseResult] = field(default_factory=list)
    dimension_scores: DimensionScores = field(default_factory=DimensionScores)
    readiness: dict[str, Any] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    weaknesses: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    is_baseline: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "dataset_version": self.dataset_version,
            "git_commit": self.git_commit,
            "axiom_version": self.axiom_version,
            "environment": self.environment,
            "configuration": self.configuration,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "results": [r.to_dict() for r in self.results],
            "dimension_scores": self.dimension_scores.to_dict(),
            "readiness": self.readiness,
            "failures": self.failures,
            "weaknesses": self.weaknesses,
            "notes": self.notes,
            "is_baseline": self.is_baseline,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "mean_score": (
                    round(sum(r.score for r in self.results) / len(self.results), 4)
                    if self.results
                    else 0.0
                ),
            },
        }


__all__ = [
    "ArenaBenchmark",
    "ArenaCaseStatus",
    "ArenaCategory",
    "ArenaRun",
    "ArenaTier",
    "CaseResult",
    "DimensionScores",
    "TaskType",
    "_new_id",
    "_utc_now",
]
