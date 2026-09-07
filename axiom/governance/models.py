"""Data models for engineering governance snapshots and findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(StrEnum):
    DEBT = "debt"
    DEPENDENCY = "dependency"
    CODE_QUALITY = "code_quality"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    BENCHMARK = "benchmark"


@dataclass
class Finding:
    category: FindingCategory
    severity: Severity
    title: str
    detail: str
    recommendation: str
    source: str = ""
    score_impact: float = 0.0  # negative points to health score (0-10)


@dataclass
class MetricValue:
    name: str
    value: float | int | str
    unit: str = ""
    target: float | None = None
    status: str = "ok"  # ok | warn | fail


@dataclass
class CollectorResult:
    name: str
    metrics: list[MetricValue] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthScores:
    engineering_health: float = 0.0
    product_health: float = 0.0
    research_capability: float = 0.0
    technical_debt: float = 0.0  # higher = more debt (inverse health)
    security: float = 0.0
    performance: float = 0.0
    developer_experience: float = 0.0
    repository_maturity: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "engineering_health": round(self.engineering_health, 1),
            "product_health": round(self.product_health, 1),
            "research_capability": round(self.research_capability, 1),
            "technical_debt": round(self.technical_debt, 1),
            "security": round(self.security, 1),
            "performance": round(self.performance, 1),
            "developer_experience": round(self.developer_experience, 1),
            "repository_maturity": round(self.repository_maturity, 1),
        }


@dataclass
class CouncilRecommendation:
    role: str
    domain: str
    priority: int
    recommendation: str
    rationale: str


@dataclass
class GovernanceSnapshot:
    timestamp: str
    workspace_root: str
    collectors: dict[str, CollectorResult] = field(default_factory=dict)
    scores: HealthScores = field(default_factory=HealthScores)
    council: list[CouncilRecommendation] = field(default_factory=list)
    priorities: list[tuple[int, str, str]] = field(default_factory=list)
    top_initiative: str = ""
    top_initiative_rationale: str = ""

    @property
    def all_findings(self) -> list[Finding]:
        findings: list[Finding] = []
        for result in self.collectors.values():
            findings.extend(result.findings)
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        return sorted(findings, key=lambda f: severity_order.get(f.severity, 5))
