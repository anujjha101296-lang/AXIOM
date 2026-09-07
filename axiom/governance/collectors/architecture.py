"""Architecture consistency checking."""

from __future__ import annotations

import re
from pathlib import Path

from axiom.governance.models import (
    CollectorResult,
    Finding,
    FindingCategory,
    MetricValue,
    Severity,
)

REQUIRED_DOCS = (
    "ARCHITECTURE.md",
    "ENGINEERING.md",
    "VISION.md",
    ".axiom/CONSTITUTION.md",
)

ADR_DIR = "ARCHITECTURE_DECISION_RECORDS"


def collect_architecture(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="architecture")
    main_py = workspace / "axiom" / "services" / "api_gateway" / "main.py"
    routes_dir = workspace / "axiom" / "services" / "api_gateway" / "routes"

    mounted = _count_mounted_routers(main_py) if main_py.exists() else 0
    route_files = list(routes_dir.glob("*.py")) if routes_dir.exists() else []
    route_modules = [f for f in route_files if f.name != "__init__.py"]

    result.metrics.append(MetricValue("mounted_routers", mounted, unit="count"))
    result.metrics.append(MetricValue("route_modules", len(route_modules), unit="count"))

    unmounted = len(route_modules) - mounted
    if unmounted > 0:
        result.findings.append(
            Finding(
                category=FindingCategory.ARCHITECTURE,
                severity=Severity.MEDIUM,
                title=f"{unmounted} route module(s) may be unmounted",
                detail="Route files exist but may not be included in main.py",
                recommendation="Audit axiom/services/api_gateway/main.py router includes",
                source="main.py",
                score_impact=2.0,
            )
        )

    adr_count = len(list((workspace / ADR_DIR).glob("*.md"))) if (workspace / ADR_DIR).exists() else 0
    result.metrics.append(
        MetricValue("architecture_decision_records", adr_count, target=3, status="ok" if adr_count >= 3 else "warn")
    )
    if adr_count < 3:
        result.findings.append(
            Finding(
                category=FindingCategory.ARCHITECTURE,
                severity=Severity.MEDIUM,
                title="Insufficient ADR coverage",
                detail=f"Only {adr_count} ADRs found in {ADR_DIR}/",
                recommendation="Record major decisions as ADRs before implementation",
                source=ADR_DIR,
                score_impact=2.0,
            )
        )

    for doc in REQUIRED_DOCS:
        if not (workspace / doc).exists():
            result.findings.append(
                Finding(
                    category=FindingCategory.ARCHITECTURE,
                    severity=Severity.HIGH,
                    title=f"Missing architecture doc: {doc}",
                    detail="Contract documents are required for consistency checks.",
                    recommendation=f"Create or restore {doc}",
                    source=doc,
                    score_impact=4.0,
                )
            )

    layer_violations = _check_layer_imports(workspace)
    result.metrics.append(
        MetricValue("layer_violations", layer_violations, target=0, status="ok" if layer_violations == 0 else "warn")
    )
    if layer_violations:
        result.findings.append(
            Finding(
                category=FindingCategory.ARCHITECTURE,
                severity=Severity.MEDIUM,
                title="Potential layer violations in core modules",
                detail=f"{layer_violations} core files import from services layer",
                recommendation="Keep domain logic in axiom/core; services should orchestrate only",
                source="import-analysis",
                score_impact=2.5,
            )
        )

    result.raw["mounted_routers"] = mounted
    result.raw["route_modules"] = [f.name for f in route_modules]
    return result


def _count_mounted_routers(main_py: Path) -> int:
    text = main_py.read_text(encoding="utf-8")
    return len(re.findall(r"app\.include_router\(", text))


def _check_layer_imports(workspace: Path) -> int:
    violations = 0
    core_dir = workspace / "axiom" / "core"
    if not core_dir.exists():
        return 0
    for path in core_dir.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "from axiom.services" in text or "import axiom.services" in text:
            violations += 1
    return violations
