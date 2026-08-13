"""
AXIOM Phase 8 — Evaluation Domain Model

Defines the core data structures for the scientific evaluation and 
benchmarking platform. All models are pure-Python dataclasses with
JSON serialization — no database dependency.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class BenchmarkStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class RegressionStatus(str, Enum):
    IMPROVED = "IMPROVED"
    UNCHANGED = "UNCHANGED"
    REGRESSED = "REGRESSED"
    INCONCLUSIVE = "INCONCLUSIVE"
    NO_BASELINE = "NO_BASELINE"


class CapabilityStatus(str, Enum):
    MEASURED = "MEASURED"
    PARTIALLY_MEASURED = "PARTIALLY_MEASURED"
    UNMEASURED = "UNMEASURED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


@dataclass
class Metric:
    """A single measured metric with a name, value, and optional threshold."""
    name: str
    value: float
    unit: str = ""
    threshold: Optional[float] = None
    passed: Optional[bool] = None

    def __post_init__(self):
        if self.threshold is not None:
            self.passed = self.value >= self.threshold

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BenchmarkCase:
    """A single benchmark test case with its inputs and expected outputs."""
    case_id: str
    name: str
    description: str
    inputs: dict = field(default_factory=dict)
    expected_outputs: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BenchmarkResult:
    """Result of running a single benchmark case."""
    case_id: str
    status: BenchmarkStatus
    metrics: list[Metric] = field(default_factory=list)
    actual_outputs: dict = field(default_factory=dict)
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class BenchmarkSuite:
    """A named collection of benchmark cases with aggregate metrics."""
    suite_id: str
    name: str
    description: str
    cases: list[BenchmarkCase] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "suite_id": self.suite_id,
            "name": self.name,
            "description": self.description,
            "cases": [c.to_dict() for c in self.cases],
        }


@dataclass
class EvaluationResult:
    """Aggregate result of running a full benchmark suite."""
    suite_id: str
    suite_name: str
    results: list[BenchmarkResult] = field(default_factory=list)
    aggregate_metrics: list[Metric] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def total_cases(self) -> int:
        return len(self.results)

    @property
    def passed_cases(self) -> int:
        return sum(1 for r in self.results if r.status == BenchmarkStatus.PASSED)

    @property
    def failed_cases(self) -> int:
        return sum(1 for r in self.results if r.status == BenchmarkStatus.FAILED)

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases

    def to_dict(self) -> dict:
        return {
            "suite_id": self.suite_id,
            "suite_name": self.suite_name,
            "results": [r.to_dict() for r in self.results],
            "aggregate_metrics": [m.to_dict() for m in self.aggregate_metrics],
            "duration_seconds": self.duration_seconds,
            "summary": {
                "total_cases": self.total_cases,
                "passed_cases": self.passed_cases,
                "failed_cases": self.failed_cases,
                "pass_rate": self.pass_rate,
            },
        }


@dataclass
class EvaluationRun:
    """
    A complete evaluation run capturing all benchmark results, metadata,
    and enough information to reproduce the run.
    """
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    git_commit: str = "unknown"
    git_branch: str = "unknown"
    application_version: str = "phase8"
    python_version: str = ""
    benchmark_version: str = "1.0"
    configuration: dict = field(default_factory=dict)
    suite_results: list[EvaluationResult] = field(default_factory=list)

    @property
    def overall_pass_rate(self) -> float:
        if not self.suite_results:
            return 0.0
        total = sum(r.total_cases for r in self.suite_results)
        passed = sum(r.passed_cases for r in self.suite_results)
        return passed / total if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "git_commit": self.git_commit,
            "git_branch": self.git_branch,
            "application_version": self.application_version,
            "python_version": self.python_version,
            "benchmark_version": self.benchmark_version,
            "configuration": self.configuration,
            "suite_results": [r.to_dict() for r in self.suite_results],
            "summary": {
                "total_suites": len(self.suite_results),
                "overall_pass_rate": self.overall_pass_rate,
            },
        }

    def save(self, path: str) -> None:
        """Persist this run to a JSON file."""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "EvaluationRun":
        """Load a previously saved run from JSON."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        run = cls(
            run_id=data["run_id"],
            timestamp=data["timestamp"],
            git_commit=data.get("git_commit", "unknown"),
            git_branch=data.get("git_branch", "unknown"),
            application_version=data.get("application_version", "unknown"),
            python_version=data.get("python_version", ""),
            benchmark_version=data.get("benchmark_version", "1.0"),
            configuration=data.get("configuration", {}),
        )
        return run


@dataclass
class CapabilityClaim:
    """
    A structured capability record linking a capability to its measurement.
    Every claim must be backed by an actual benchmark run.
    """
    capability_id: str
    name: str
    description: str
    status: CapabilityStatus
    evidence_run_id: Optional[str] = None
    evidence_suite_id: Optional[str] = None
    measured_metric: Optional[str] = None
    measured_value: Optional[float] = None
    git_commit: str = "unknown"
    limitations: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class RegressionComparison:
    """Result of comparing a current run against a baseline."""
    current_run_id: str
    baseline_run_id: Optional[str]
    status: RegressionStatus
    suite_comparisons: list[dict] = field(default_factory=list)
    regression_tolerance: float = 0.05  # 5% tolerance

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d
