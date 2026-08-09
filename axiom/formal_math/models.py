"""Formal Mathematics & Theorem-Proving Loop (FMTP) — domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProverSystem(str, Enum):
    LEAN4 = "lean4"
    COQ = "coq"
    ISABELLE = "isabelle"
    SMT = "smt"
    SYMPY = "sympy"


class ProofCompilationStatus(str, Enum):
    COMPILES = "COMPILES"
    DOES_NOT_COMPILE = "DOES_NOT_COMPILE"
    PARTIALLY_FORMALIZED = "PARTIALLY_FORMALIZED"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    TIMEOUT = "TIMEOUT"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    UNKNOWN = "UNKNOWN"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"


class FormalizationStatus(str, Enum):
    SUCCESS = "successfully_formalized"
    PARTIAL = "partially_formalized"
    AMBIGUOUS = "ambiguous"
    FAILED = "failed_formalization"
    UNVERIFIED = "unverified"


class ConjectureStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"


class TrustLayer(str, Enum):
    AXIOM = "axiom"
    TRUSTED_KERNEL = "trusted_kernel"
    FORMAL_LIBRARY = "formal_library"
    AUTOMATION = "automation"
    TACTIC = "tactic"
    GENERATED_CODE = "generated_code"
    LLM_OUTPUT = "llm_output"
    HUMAN_ASSERTION = "human_assertion"


class BenchmarkLevel(int, Enum):
    LEVEL_0 = 0  # Basic formalization
    LEVEL_1 = 1  # Elementary theorem proving
    LEVEL_2 = 2  # Competition mathematics
    LEVEL_3 = 3  # Graduate mathematics
    LEVEL_4 = 4  # Published theorem reproduction
    LEVEL_5 = 5  # Difficult formalization
    LEVEL_6 = 6  # Research-level theorem proving
    LEVEL_7 = 7  # Open mathematical problems


@dataclass
class ProverSpec:
    prover_id: str
    name: str
    version: str
    language: str
    libraries: list[str] = field(default_factory=list)
    tactics: list[str] = field(default_factory=list)
    automation: list[str] = field(default_factory=list)
    supported_domains: list[str] = field(default_factory=list)
    installed: bool = False
    limitations: list[str] = field(default_factory=list)
    verification_status: str = "available"

    def to_dict(self) -> dict[str, Any]:
        return {
            "prover_id": self.prover_id,
            "name": self.name,
            "version": self.version,
            "language": self.language,
            "libraries": self.libraries,
            "tactics": self.tactics,
            "automation": self.automation,
            "supported_domains": self.supported_domains,
            "installed": self.installed,
            "limitations": self.limitations,
            "verification_status": self.verification_status,
        }


@dataclass
class MathEntity:
    entity_id: str
    entity_type: str  # definition, theorem, lemma, conjecture, etc.
    name: str
    statement: str
    created_at: str
    formal_spec: str | None = None
    prover: str | None = None
    library_version: str | None = None
    dependencies: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    domain: str = "unknown"
    notation: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "statement": self.statement,
            "created_at": self.created_at,
            "formal_spec": self.formal_spec,
            "prover": self.prover,
            "library_version": self.library_version,
            "dependencies": self.dependencies,
            "assumptions": self.assumptions,
            "domain": self.domain,
            "notation": self.notation,
            "metadata": self.metadata,
        }


@dataclass
class ProofArtifact:
    proof_id: str
    theorem_id: str
    version: int
    created_at: str
    prover: str
    prover_version: str
    formal_statement: str
    source_code: str
    compilation_status: ProofCompilationStatus
    verification_output: str = ""
    dependencies: list[str] = field(default_factory=list)
    library_versions: dict[str, str] = field(default_factory=dict)
    model_provenance: dict[str, Any] = field(default_factory=dict)
    campaign_id: str | None = None
    trust_layers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "theorem_id": self.theorem_id,
            "version": self.version,
            "created_at": self.created_at,
            "prover": self.prover,
            "prover_version": self.prover_version,
            "formal_statement": self.formal_statement,
            "source_code": self.source_code,
            "compilation_status": self.compilation_status.value,
            "verification_output": self.verification_output,
            "dependencies": self.dependencies,
            "library_versions": self.library_versions,
            "model_provenance": self.model_provenance,
            "campaign_id": self.campaign_id,
            "trust_layers": self.trust_layers,
        }


@dataclass
class FormalizationResult:
    result_id: str
    informal_statement: str
    structured_statement: str
    formal_spec: str | None
    status: FormalizationStatus
    prover: str
    ambiguities: list[str] = field(default_factory=list)
    proof_artifact_id: str | None = None
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "informal_statement": self.informal_statement,
            "structured_statement": self.structured_statement,
            "formal_spec": self.formal_spec,
            "status": self.status.value,
            "prover": self.prover,
            "ambiguities": self.ambiguities,
            "proof_artifact_id": self.proof_artifact_id,
            "created_at": self.created_at,
        }


@dataclass
class CounterexampleRecord:
    counterexample_id: str
    claim: str
    counterexample: dict[str, Any]
    method: str
    parameters: dict[str, Any]
    verified: bool
    created_at: str
    campaign_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "counterexample_id": self.counterexample_id,
            "claim": self.claim,
            "counterexample": self.counterexample,
            "method": self.method,
            "parameters": self.parameters,
            "verified": self.verified,
            "created_at": self.created_at,
            "campaign_id": self.campaign_id,
        }


@dataclass
class ProofFailureRecord:
    failure_id: str
    theorem_id: str
    approach: str
    prover_output: str
    goal_state: str
    attempted_tactic: str
    created_at: str
    learned: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "theorem_id": self.theorem_id,
            "approach": self.approach,
            "prover_output": self.prover_output,
            "goal_state": self.goal_state,
            "attempted_tactic": self.attempted_tactic,
            "created_at": self.created_at,
            "learned": self.learned,
        }
