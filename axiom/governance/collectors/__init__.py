"""Collector registry."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from axiom.governance.collectors.architecture import collect_architecture
from axiom.governance.collectors.benchmarks import collect_benchmarks
from axiom.governance.collectors.code_quality import collect_code_quality
from axiom.governance.collectors.debt import collect_debt
from axiom.governance.collectors.dependencies import collect_dependencies
from axiom.governance.collectors.documentation import collect_documentation
from axiom.governance.collectors.performance import collect_performance
from axiom.governance.collectors.security import collect_security
from axiom.governance.collectors.testing import collect_testing
from axiom.governance.models import CollectorResult

COLLECTORS: dict[str, Callable[[Path], CollectorResult]] = {
    "technical_debt": collect_debt,
    "dependencies": collect_dependencies,
    "code_quality": collect_code_quality,
    "architecture": collect_architecture,
    "performance": collect_performance,
    "security": collect_security,
    "documentation": collect_documentation,
    "testing": collect_testing,
    "benchmarks": collect_benchmarks,
}


def run_all_collectors(workspace: Path) -> dict[str, CollectorResult]:
    return {name: fn(workspace) for name, fn in COLLECTORS.items()}
