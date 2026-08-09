"""Scientific Experimentation & Compute Loop (SEC) — domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExperimentStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ANALYZED = "ANALYZED"
    VERIFIED = "VERIFIED"
    ARCHIVED = "ARCHIVED"


class ExperimentReproductionStatus(str, Enum):
    EXACT_REPRODUCTION = "EXACT_REPRODUCTION"
    APPROXIMATE_REPRODUCTION = "APPROXIMATE_REPRODUCTION"
    PARTIAL_REPRODUCTION = "PARTIAL_REPRODUCTION"
    FAILED_REPRODUCTION = "FAILED_REPRODUCTION"
    UNABLE_TO_REPRODUCE = "UNABLE_TO_REPRODUCE"


class EvidenceClass(str, Enum):
    COMPUTATIONAL_EVIDENCE = "computational_evidence"
    STATISTICAL_EVIDENCE = "statistical_evidence"
    NUMERICAL_EVIDENCE = "numerical_evidence"
    SYMBOLIC_EVIDENCE = "symbolic_evidence"
    NOT_SCIENTIFIC_FACT = "not_scientific_fact"
    NOT_MATHEMATICAL_PROOF = "not_mathematical_proof"


class ComputeEnvironmentType(str, Enum):
    PYTHON = "python"
    SCIENTIFIC_PYTHON = "scientific_python"
    NUMERICAL = "numerical"
    SYMBOLIC = "symbolic"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    COMPILED = "compiled"
    GPU = "gpu"
    VLSI = "vlsi"


class SearchStrategy(str, Enum):
    GRID = "grid"
    RANDOM = "random"
    BAYESIAN = "bayesian"
    EVOLUTIONARY = "evolutionary"
    ADAPTIVE = "adaptive"


_VALID_TRANSITIONS: dict[ExperimentStatus, set[ExperimentStatus]] = {
    ExperimentStatus.DRAFT: {ExperimentStatus.VALIDATED, ExperimentStatus.CANCELLED},
    ExperimentStatus.VALIDATED: {ExperimentStatus.QUEUED, ExperimentStatus.DRAFT, ExperimentStatus.CANCELLED},
    ExperimentStatus.QUEUED: {ExperimentStatus.RUNNING, ExperimentStatus.CANCELLED},
    ExperimentStatus.RUNNING: {ExperimentStatus.COMPLETED, ExperimentStatus.FAILED, ExperimentStatus.CANCELLED},
    ExperimentStatus.COMPLETED: {ExperimentStatus.ANALYZED, ExperimentStatus.ARCHIVED},
    ExperimentStatus.FAILED: {ExperimentStatus.ANALYZED, ExperimentStatus.QUEUED, ExperimentStatus.ARCHIVED},
    ExperimentStatus.CANCELLED: {ExperimentStatus.ARCHIVED, ExperimentStatus.DRAFT},
    ExperimentStatus.ANALYZED: {ExperimentStatus.VERIFIED, ExperimentStatus.ARCHIVED, ExperimentStatus.QUEUED},
    ExperimentStatus.VERIFIED: {ExperimentStatus.ARCHIVED},
    ExperimentStatus.ARCHIVED: set(),
}


def can_transition(from_status: ExperimentStatus, to_status: ExperimentStatus) -> bool:
    return to_status in _VALID_TRANSITIONS.get(from_status, set())


@dataclass
class ResourceBudget:
    cpu_seconds: float = 60.0
    memory_mb: int = 512
    disk_mb: int = 100
    timeout_seconds: float = 30.0
    network_allowed: bool = False
    gpu_seconds: float = 0.0
    monetary_usd: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "cpu_seconds": self.cpu_seconds,
            "memory_mb": self.memory_mb,
            "disk_mb": self.disk_mb,
            "timeout_seconds": self.timeout_seconds,
            "network_allowed": self.network_allowed,
            "gpu_seconds": self.gpu_seconds,
            "monetary_usd": self.monetary_usd,
        }


@dataclass
class ExperimentSpec:
    research_question: str
    hypothesis: str
    objective: str
    variables: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Any] = field(default_factory=dict)
    procedure: str = ""
    expected_observation: str = ""
    environment_type: ComputeEnvironmentType = ComputeEnvironmentType.PYTHON
    resource_budget: ResourceBudget = field(default_factory=ResourceBudget)
    evaluation_metrics: list[str] = field(default_factory=list)
    stopping_conditions: dict[str, Any] = field(default_factory=dict)
    reproduction_instructions: str = ""
    random_seed: int | None = None
    code: str | None = None
    tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "research_question": self.research_question,
            "hypothesis": self.hypothesis,
            "objective": self.objective,
            "variables": self.variables,
            "inputs": self.inputs,
            "procedure": self.procedure,
            "expected_observation": self.expected_observation,
            "environment_type": self.environment_type.value,
            "resource_budget": self.resource_budget.to_dict(),
            "evaluation_metrics": self.evaluation_metrics,
            "stopping_conditions": self.stopping_conditions,
            "reproduction_instructions": self.reproduction_instructions,
            "random_seed": self.random_seed,
            "code": self.code,
            "tools": self.tools,
        }


@dataclass
class Experiment:
    experiment_id: str
    status: ExperimentStatus
    version: int
    created_at: str
    updated_at: str
    spec: dict[str, Any]
    campaign_id: str | None = None
    claim_id: str | None = None
    hypothesis_id: str | None = None
    owner_id: str | None = None
    environment: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    verification_status: str = "pending"
    evidence_class: str = EvidenceClass.COMPUTATIONAL_EVIDENCE.value
    provenance: dict[str, Any] = field(default_factory=dict)
    failure: dict[str, Any] | None = None
    checkpoint: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "spec": self.spec,
            "campaign_id": self.campaign_id,
            "claim_id": self.claim_id,
            "hypothesis_id": self.hypothesis_id,
            "owner_id": self.owner_id,
            "environment": self.environment,
            "results": self.results,
            "artifacts": self.artifacts,
            "verification_status": self.verification_status,
            "evidence_class": self.evidence_class,
            "provenance": self.provenance,
            "failure": self.failure,
            "checkpoint": self.checkpoint,
        }


@dataclass
class DatasetRecord:
    dataset_id: str
    name: str
    version: str
    source: str
    created_at: str
    license: str = "unknown"
    content_hash: str | None = None
    schema: dict[str, Any] = field(default_factory=dict)
    preprocessing: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "version": self.version,
            "source": self.source,
            "created_at": self.created_at,
            "license": self.license,
            "content_hash": self.content_hash,
            "schema": self.schema,
            "preprocessing": self.preprocessing,
            "limitations": self.limitations,
            "provenance": self.provenance,
        }


@dataclass
class ExperimentFailure:
    failure_id: str
    experiment_id: str
    failure_type: str
    error: str
    created_at: str
    configuration: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    root_cause: str = ""
    lessons: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "experiment_id": self.experiment_id,
            "failure_type": self.failure_type,
            "error": self.error,
            "created_at": self.created_at,
            "configuration": self.configuration,
            "environment": self.environment,
            "root_cause": self.root_cause,
            "lessons": self.lessons,
        }
