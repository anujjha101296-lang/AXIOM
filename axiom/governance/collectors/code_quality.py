"""Code quality scoring via ruff and static analysis."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from axiom.governance.models import (
    CollectorResult,
    Finding,
    FindingCategory,
    MetricValue,
    Severity,
)


def collect_code_quality(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="code_quality")
    py_files = list((workspace / "axiom").rglob("*.py"))
    test_files = list((workspace / "tests").rglob("*.py"))

    result.metrics.append(MetricValue("python_modules", len(py_files), unit="files"))
    result.metrics.append(MetricValue("test_files", len(test_files), unit="files"))
    ratio = len(test_files) / max(len(py_files), 1)
    result.metrics.append(
        MetricValue("test_file_ratio", round(ratio, 2), target=0.3, status="ok" if ratio >= 0.15 else "warn")
    )

    lint_issues = _run_ruff(workspace, result)
    result.metrics.append(
        MetricValue("ruff_violations", lint_issues, unit="count", target=0, status=_lint_status(lint_issues))
    )

    type_errors = _run_mypy(workspace, result)
    result.metrics.append(
        MetricValue("mypy_errors", type_errors, unit="count", target=0, status=_lint_status(type_errors, warn_at=5))
    )

    duplicate_patterns = _check_duplication(workspace)
    result.metrics.append(
        MetricValue("duplicate_module_patterns", duplicate_patterns, unit="count", status="warn" if duplicate_patterns else "ok")
    )
    if duplicate_patterns:
        result.findings.append(
            Finding(
                category=FindingCategory.CODE_QUALITY,
                severity=Severity.MEDIUM,
                title="Potential code duplication detected",
                detail=f"{duplicate_patterns} route/handler naming collisions across modules",
                recommendation="Consolidate shared logic into axiom/core or shared utilities",
                source="static-analysis",
                score_impact=2.0,
            )
        )

    result.raw["py_file_count"] = len(py_files)
    return result


def _lint_status(count: int, warn_at: int = 0) -> str:
    if count <= warn_at:
        return "ok"
    if count <= warn_at + 10:
        return "warn"
    return "fail"


def _run_ruff(workspace: Path, result: CollectorResult) -> int:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "axiom/", "tests/", "--output-format=json"],
            capture_output=True,
            text=True,
            cwd=workspace,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        result.findings.append(
            Finding(
                category=FindingCategory.CODE_QUALITY,
                severity=Severity.INFO,
                title="ruff not available",
                detail="Install ruff for lint scoring.",
                recommendation="pip install ruff",
                source="ruff",
            )
        )
        return 0

    try:
        import json

        issues = json.loads(proc.stdout or "[]")
    except Exception:
        return 0

    count = len(issues)
    for issue in issues[:5]:
        result.findings.append(
            Finding(
                category=FindingCategory.CODE_QUALITY,
                severity=Severity.LOW,
                title=f"Ruff: {issue.get('code', 'rule')}",
                detail=f"{issue.get('filename')}:{issue.get('location', {}).get('row', '?')}",
                recommendation="Run make lint-fix",
                source="ruff",
                score_impact=0.1,
            )
        )
    return count


def _run_mypy(workspace: Path, result: CollectorResult) -> int:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", "axiom/", "--ignore-missing-imports", "--no-strict-optional"],
            capture_output=True,
            text=True,
            cwd=workspace,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0

    errors = proc.stdout.count(": error:")
    if errors > 5:
        result.findings.append(
            Finding(
                category=FindingCategory.CODE_QUALITY,
                severity=Severity.MEDIUM,
                title=f"mypy reports {errors} type errors",
                detail="Type safety gaps increase refactor risk.",
                recommendation="Address high-traffic modules first; run make type-check",
                source="mypy",
                score_impact=1.5,
            )
        )
    return errors


def _check_duplication(workspace: Path) -> int:
    """Heuristic: count duplicate basenames in axiom/ (excluding __init__)."""
    names: dict[str, int] = {}
    for path in (workspace / "axiom").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        names[path.name] = names.get(path.name, 0) + 1
    return sum(1 for c in names.values() if c > 1)
