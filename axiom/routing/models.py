"""Scientific Intelligence & Model Routing (SIMR) — domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResearchDomain(str, Enum):
    MATHEMATICS = "mathematics"
    COMPUTER_SCIENCE = "computer_science"
    PHYSICS = "physics"
    HARDWARE = "hardware"
    GENERAL_SCIENCE = "general_science"
    LITERATURE = "literature"
    UNKNOWN = "unknown"


class ProblemDifficulty(str, Enum):
    TRIVIAL = "trivial"
    MODERATE = "moderate"
    HARD = "hard"
    FRONTIER = "frontier"


class VerificationRequirement(str, Enum):
    NONE = "none"
    REPRODUCTION = "reproduction"
    INDEPENDENT = "independent"
    FORMAL = "formal"
    HUMAN_REVIEW = "human_review"


class StrategyType(str, Enum):
    LITERATURE_FIRST = "literature_first"
    FORMAL_MATHEMATICS = "formal_mathematics"
    COMPUTATIONAL_EXPLORATION = "computational_exploration"
    ANALOGY = "analogy"
    COUNTEREXAMPLE_SEARCH = "counterexample_search"
    HYBRID = "hybrid"
    SINGLE_MODEL = "single_model"
    MULTI_MODEL = "multi_model"
    ENSEMBLE = "ensemble"


class SourceReliability(str, Enum):
    PRIMARY_PAPER = "primary_paper"
    PEER_REVIEWED = "peer_reviewed"
    OFFICIAL_DATASET = "official_dataset"
    OFFICIAL_DOCS = "official_docs"
    VERIFIED_DATABASE = "verified_database"
    REPOSITORY = "repository"
    WEB = "web"
    UNVERIFIED = "unverified"


@dataclass
class ModelSpec:
    model_id: str
    name: str
    provider: str
    version: str
    capabilities: list[str] = field(default_factory=list)
    context_window: int = 8192
    modalities: list[str] = field(default_factory=lambda: ["text"])
    tool_support: bool = False
    structured_output: bool = False
    cost_per_1k_tokens: float = 0.0
    latency_ms_p50: int = 500
    limitations: list[str] = field(default_factory=list)
    reliability_score: float = 0.5
    benchmark_scores: dict[str, float] = field(default_factory=dict)
    availability: str = "available"
    license_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider": self.provider,
            "version": self.version,
            "capabilities": self.capabilities,
            "context_window": self.context_window,
            "modalities": self.modalities,
            "tool_support": self.tool_support,
            "structured_output": self.structured_output,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "latency_ms_p50": self.latency_ms_p50,
            "limitations": self.limitations,
            "reliability_score": self.reliability_score,
            "benchmark_scores": self.benchmark_scores,
            "availability": self.availability,
            "license_notes": self.license_notes,
        }


@dataclass
class ToolSpec:
    tool_id: str
    name: str
    category: str
    capabilities: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    risk_class: str = "READ_ONLY"
    cost_estimate: float = 0.0
    latency_ms_p50: int = 100
    reliability_score: float = 0.5
    verification_level: str = "unverified"
    security_level: str = "standard"
    module_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "category": self.category,
            "capabilities": self.capabilities,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "risk_class": self.risk_class,
            "cost_estimate": self.cost_estimate,
            "latency_ms_p50": self.latency_ms_p50,
            "reliability_score": self.reliability_score,
            "verification_level": self.verification_level,
            "security_level": self.security_level,
            "module_path": self.module_path,
        }


@dataclass
class ProblemProfile:
    problem_id: str
    statement: str
    domain: ResearchDomain = ResearchDomain.UNKNOWN
    difficulty: ProblemDifficulty = ProblemDifficulty.MODERATE
    required_capabilities: list[str] = field(default_factory=list)
    verification_requirement: VerificationRequirement = VerificationRequirement.NONE
    requires_literature: bool = False
    requires_formal: bool = False
    requires_experiment: bool = False
    expected_runtime_minutes: int = 30
    uncertainty: float = 0.5
    safety_risk: str = "low"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "statement": self.statement,
            "domain": self.domain.value,
            "difficulty": self.difficulty.value,
            "required_capabilities": self.required_capabilities,
            "verification_requirement": self.verification_requirement.value,
            "requires_literature": self.requires_literature,
            "requires_formal": self.requires_formal,
            "requires_experiment": self.requires_experiment,
            "expected_runtime_minutes": self.expected_runtime_minutes,
            "uncertainty": self.uncertainty,
            "safety_risk": self.safety_risk,
            "metadata": self.metadata,
        }


@dataclass
class ResearchStrategy:
    strategy_id: str
    strategy_type: StrategyType
    description: str
    models: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    verifiers: list[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_minutes: int = 30
    confidence: float = 0.5
    novelty_potential: float = 0.3

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type.value,
            "description": self.description,
            "models": self.models,
            "tools": self.tools,
            "verifiers": self.verifiers,
            "estimated_cost": self.estimated_cost,
            "estimated_minutes": self.estimated_minutes,
            "confidence": self.confidence,
            "novelty_potential": self.novelty_potential,
        }


@dataclass
class RoutingDecision:
    decision_id: str
    problem_id: str
    created_at: str
    profile: dict[str, Any]
    selected_model: str
    selected_tools: list[str]
    selected_strategy: str
    rationale: str
    verification_plan: list[str] = field(default_factory=list)
    fallback_model: str | None = None
    cost_estimate: float = 0.0
    requires_human_review: bool = False
    model_version: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "problem_id": self.problem_id,
            "created_at": self.created_at,
            "profile": self.profile,
            "selected_model": self.selected_model,
            "selected_tools": self.selected_tools,
            "selected_strategy": self.selected_strategy,
            "rationale": self.rationale,
            "verification_plan": self.verification_plan,
            "fallback_model": self.fallback_model,
            "cost_estimate": self.cost_estimate,
            "requires_human_review": self.requires_human_review,
            "model_version": self.model_version,
            "metadata": self.metadata,
        }


@dataclass
class ModelFailureRecord:
    failure_id: str
    model_id: str
    failure_type: str
    description: str
    created_at: str
    problem_domain: str = "unknown"
    capability: str | None = None
    severity: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "model_id": self.model_id,
            "failure_type": self.failure_type,
            "description": self.description,
            "created_at": self.created_at,
            "problem_domain": self.problem_domain,
            "capability": self.capability,
            "severity": self.severity,
        }


@dataclass
class KnowledgeConflict:
    conflict_id: str
    source_a: str
    source_b: str
    claim_a: str
    claim_b: str
    created_at: str
    resolution_status: str = "open"
    confidence_a: float = 0.5
    confidence_b: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "source_a": self.source_a,
            "source_b": self.source_b,
            "claim_a": self.claim_a,
            "claim_b": self.claim_b,
            "created_at": self.created_at,
            "resolution_status": self.resolution_status,
            "confidence_a": self.confidence_a,
            "confidence_b": self.confidence_b,
            "metadata": self.metadata,
        }


@dataclass
class ResearchExecutionPlan:
    problem_id: str
    profile: dict[str, Any]
    capability_requirements: list[str]
    strategies: list[dict[str, Any]]
    selected_strategy: dict[str, Any]
    model_graph: dict[str, Any]
    execution_steps: list[dict[str, Any]]
    verification_plan: list[str]
    cost_estimate: float
    requires_human_review: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "profile": self.profile,
            "capability_requirements": self.capability_requirements,
            "strategies": self.strategies,
            "selected_strategy": self.selected_strategy,
            "model_graph": self.model_graph,
            "execution_steps": self.execution_steps,
            "verification_plan": self.verification_plan,
            "cost_estimate": self.cost_estimate,
            "requires_human_review": self.requires_human_review,
        }
