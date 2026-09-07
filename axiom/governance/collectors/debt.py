"""Technical debt tracking — scans markers and documented blockers."""

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

MARKER_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|DEPRECATED)\b", re.IGNORECASE)
DEBT_DOC_FILES = (
    "MVP_READINESS.md",
    "MASTER_PROGRESS.md",
    "ENGINEERING_SCORECARD.md",
    ".axiom/TASK_QUEUE.md",
    ".axiom/CURRENT_STATE.md",
)

KNOWN_DEBT_ITEMS = [
    ("No per-user data isolation", "critical", "MVP_READINESS.md P0"),
    ("MDE API surface gap (26 e2e failures)", "high", "MASTER_PROGRESS.md"),
    ("Workflow engine has no core tests", "medium", "MASTER_PROGRESS.md"),
    ("Mock LLM default for Q&A/summaries", "medium", "MVP_READINESS.md"),
    ("Shared SQLite store (no tenancy)", "critical", "MVP_READINESS.md"),
    ("UI Dockerfile missing", "medium", "ENGINEERING_SCORECARD.md"),
    ("Grafana provisioning incomplete", "low", "ENGINEERING_SCORECARD.md"),
]

SCAN_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".md"}
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "htmlcov",
    ".next",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def collect_debt(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="technical_debt")
    marker_hits: list[tuple[str, int, str]] = []

    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if MARKER_PATTERN.search(line):
                rel = str(path.relative_to(workspace))
                marker_hits.append((rel, i, line.strip()[:120]))

    result.metrics.append(
        MetricValue("inline_debt_markers", len(marker_hits), unit="count", status="warn" if marker_hits else "ok")
    )
    result.metrics.append(
        MetricValue("documented_debt_items", len(KNOWN_DEBT_ITEMS), unit="count", status="warn")
    )

    for rel, line_no, snippet in marker_hits[:15]:
        result.findings.append(
            Finding(
                category=FindingCategory.DEBT,
                severity=Severity.LOW,
                title=f"Debt marker in {rel}:{line_no}",
                detail=snippet,
                recommendation="Resolve or track in TECH_DEBT_BOARD.md",
                source=rel,
                score_impact=0.2,
            )
        )

    for title, severity_str, source in KNOWN_DEBT_ITEMS:
        sev = Severity(severity_str)
        result.findings.append(
            Finding(
                category=FindingCategory.DEBT,
                severity=sev,
                title=title,
                detail=f"Documented in {source}",
                recommendation=_debt_recommendation(title),
                source=source,
                score_impact={"critical": 8.0, "high": 5.0, "medium": 3.0, "low": 1.0}[severity_str],
            )
        )

    for doc in DEBT_DOC_FILES:
        doc_path = workspace / doc
        if doc_path.exists():
            result.raw[doc] = True
        else:
            result.findings.append(
                Finding(
                    category=FindingCategory.DEBT,
                    severity=Severity.MEDIUM,
                    title=f"Missing debt reference doc: {doc}",
                    detail="Governance cannot cross-check documented blockers.",
                    recommendation=f"Restore or create {doc}",
                    source="governance",
                    score_impact=2.0,
                )
            )

    result.raw["marker_hits"] = len(marker_hits)
    return result


def _debt_recommendation(title: str) -> str:
    mapping = {
        "No per-user data isolation": "Add user_id scoping to research store queries and migrations.",
        "MDE API surface gap (26 e2e failures)": "Mount remaining MDE routes or narrow e2e scope with honest docs.",
        "Workflow engine has no core tests": "Add unit tests for workflow engine state transitions.",
        "Mock LLM default for Q&A/summaries": "Document mock default; add integration path for production LLM.",
        "Shared SQLite store (no tenancy)": "Partition research data by authenticated user_id.",
        "UI Dockerfile missing": "Add ui/Dockerfile and wire docker-compose service.",
        "Grafana provisioning incomplete": "Add provisioning configs under monitoring/.",
    }
    return mapping.get(title, "Schedule remediation in next engineering cycle.")
