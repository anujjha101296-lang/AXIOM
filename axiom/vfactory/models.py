"""AXIOM Verification Factory — domain models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC
from enum import Enum
from typing import Any


def _utc_now() -> str:
    from datetime import datetime
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str = "vf") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class VerificationState(str, Enum):
    UNKNOWN = "UNKNOWN"
    UNTESTED = "UNTESTED"
    PARTIAL = "PARTIAL"
    PASSING = "PASSING"
    REGRESSION = "REGRESSION"
    BLOCKED = "BLOCKED"
    VERIFIED = "VERIFIED"


class TestLevel(int, Enum):
    """Test pyramid levels (VF §2)."""

    STATIC_ANALYSIS = 1
    UNIT = 2
    COMPONENT = 3
    API = 4
    DATABASE = 5
    SERVICE_INTEGRATION = 6
    E2E = 7
    SECURITY = 8
    PERFORMANCE = 9
    SCIENTIFIC = 10


class VerificationDomain(str, Enum):
    CODE = "code"
    API = "api"
    PRODUCT = "product"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    AI = "ai"
    AGENT = "agent"
    SCIENTIFIC = "scientific"
    RESEARCH = "research"
    OVERALL = "overall"


class VerificationRole(str, Enum):
    """Logical verification roles (VF §3) — not unlimited agents."""

    TEST_ARCHITECT = "test_architect"
    BACKEND_QA = "backend_qa"
    FRONTEND_QA = "frontend_qa"
    DATABASE_QA = "database_qa"
    AI_QA = "ai_qa"
    AGENT_QA = "agent_qa"
    SECURITY_TESTER = "security_tester"
    INFRASTRUCTURE_TESTER = "infrastructure_tester"
    PERFORMANCE_TESTER = "performance_tester"
    RESEARCH_EVALUATOR = "research_evaluator"
    SCIENTIFIC_INTEGRITY = "scientific_integrity_reviewer"
    RELEASE_ENGINEER = "release_engineer"


@dataclass
class CapabilityRecord:
    """Registered AXIOM capability (VF §1)."""

    capability_id: str
    name: str
    description: str
    domain: str
    owner: str = "platform"
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    unit_tests: list[str] = field(default_factory=list)
    integration_tests: list[str] = field(default_factory=list)
    e2e_tests: list[str] = field(default_factory=list)
    security_tests: list[str] = field(default_factory=list)
    performance_tests: list[str] = field(default_factory=list)
    research_benchmarks: list[str] = field(default_factory=list)
    known_limitations: list[str] = field(default_factory=list)
    status: VerificationState = VerificationState.UNTESTED
    last_verified: str | None = None
    last_failed: str | None = None
    verification_evidence: list[str] = field(default_factory=list)
    health_check: str | None = None
    api_prefix: str | None = None
    source_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "owner": self.owner,
            "dependencies": self.dependencies,
            "acceptance_criteria": self.acceptance_criteria,
            "unit_tests": self.unit_tests,
            "integration_tests": self.integration_tests,
            "e2e_tests": self.e2e_tests,
            "security_tests": self.security_tests,
            "performance_tests": self.performance_tests,
            "research_benchmarks": self.research_benchmarks,
            "known_limitations": self.known_limitations,
            "status": self.status.value,
            "last_verified": self.last_verified,
            "last_failed": self.last_failed,
            "verification_evidence": self.verification_evidence,
            "health_check": self.health_check,
            "api_prefix": self.api_prefix,
            "source_paths": self.source_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CapabilityRecord:
        return cls(
            capability_id=data["capability_id"],
            name=data["name"],
            description=data["description"],
            domain=data.get("domain", "research"),
            owner=data.get("owner", "platform"),
            dependencies=list(data.get("dependencies", [])),
            acceptance_criteria=list(data.get("acceptance_criteria", [])),
            unit_tests=list(data.get("unit_tests", [])),
            integration_tests=list(data.get("integration_tests", [])),
            e2e_tests=list(data.get("e2e_tests", [])),
            security_tests=list(data.get("security_tests", [])),
            performance_tests=list(data.get("performance_tests", [])),
            research_benchmarks=list(data.get("research_benchmarks", [])),
            known_limitations=list(data.get("known_limitations", [])),
            status=VerificationState(data.get("status", "UNTESTED")),
            last_verified=data.get("last_verified"),
            last_failed=data.get("last_failed"),
            verification_evidence=list(data.get("verification_evidence", [])),
            health_check=data.get("health_check"),
            api_prefix=data.get("api_prefix"),
            source_paths=list(data.get("source_paths", [])),
        )


@dataclass
class TestRunResult:
    run_id: str
    level: TestLevel
    test_name: str
    passed: bool
    duration_seconds: float
    output: str = ""
    error: str = ""
    commit: str | None = None
    environment: str = "local"
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "level": int(self.level),
            "level_name": self.level.name,
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_seconds": self.duration_seconds,
            "output": self.output[-4000:] if self.output else "",
            "error": self.error[-2000:] if self.error else "",
            "commit": self.commit,
            "environment": self.environment,
            "created_at": self.created_at,
        }


@dataclass
class JourneyResult:
    journey_id: str
    journey_name: str
    steps_completed: int
    steps_total: int
    passed: bool
    step_results: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "journey_id": self.journey_id,
            "journey_name": self.journey_name,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "passed": self.passed,
            "step_results": self.step_results,
            "created_at": self.created_at,
        }


@dataclass
class VerificationScore:
    domain: VerificationDomain
    score: float  # 0.0 - 1.0
    passing: int
    total: int
    untested: int
    regressions: int
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "score": round(self.score, 4),
            "passing": self.passing,
            "total": self.total,
            "untested": self.untested,
            "regressions": self.regressions,
            "details": self.details,
        }


@dataclass
class VerificationRun:
    """Evidence from a full verification cycle (VF §26)."""

    verification_run_id: str
    commit: str | None
    version: str
    environment: str
    configuration: dict[str, Any]
    results: list[dict[str, Any]]
    scores: list[dict[str, Any]]
    overall_passed: bool
    failures: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_run_id": self.verification_run_id,
            "commit": self.commit,
            "version": self.version,
            "environment": self.environment,
            "configuration": self.configuration,
            "results": self.results,
            "scores": self.scores,
            "overall_passed": self.overall_passed,
            "failures": self.failures,
            "created_at": self.created_at,
        }
