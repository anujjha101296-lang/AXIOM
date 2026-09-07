"""Test coverage reporting."""

from __future__ import annotations

import json
import os
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

CACHE_PATH = ".axiom/governance/last_coverage.json"
UNTESTED_MODULES = ("axiom/workflow/",)


def collect_testing(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="testing")
    collected = _count_collected_tests(workspace)
    coverage_pct = _resolve_coverage(workspace)

    result.metrics.append(MetricValue("tests_collected", collected, unit="count"))
    result.metrics.append(
        MetricValue(
            "line_coverage_pct",
            round(coverage_pct, 1),
            unit="%",
            target=70,
            status="ok" if coverage_pct >= 70 else ("warn" if coverage_pct >= 50 else "fail"),
        )
    )

    if coverage_pct < 70 and coverage_pct > 0:
        result.findings.append(
            Finding(
                category=FindingCategory.TESTING,
                severity=Severity.MEDIUM,
                title=f"Coverage below 70% gate ({coverage_pct:.1f}%)",
                detail="CI requires --cov-fail-under=70 for core tests.",
                recommendation="Add tests for untested modules; run make test-coverage",
                source="pytest-cov",
                score_impact=4.0,
            )
        )
    elif coverage_pct == 0:
        result.findings.append(
            Finding(
                category=FindingCategory.TESTING,
                severity=Severity.INFO,
                title="Coverage not measured this cycle",
                detail="Run make test-coverage or set AXIOM_GOVERNANCE_FULL=1 for live measurement.",
                recommendation="make test-coverage",
                source="pytest-cov",
            )
        )

    e2e_collected = _count_e2e_tests(workspace)
    result.metrics.append(MetricValue("e2e_tests", e2e_collected, unit="count"))
    if e2e_collected > 0:
        result.findings.append(
            Finding(
                category=FindingCategory.TESTING,
                severity=Severity.HIGH,
                title="E2E test gap: MDE API surface",
                detail=f"{e2e_collected} e2e tests exist; ~26 documented failures on main",
                recommendation="Mount MDE routes or mark e2e as xfail with honest tracking",
                source="tests/e2e",
                score_impact=5.0,
            )
        )

    for mod in UNTESTED_MODULES:
        mod_path = workspace / mod
        if mod_path.exists():
            result.findings.append(
                Finding(
                    category=FindingCategory.TESTING,
                    severity=Severity.MEDIUM,
                    title=f"No dedicated tests for {mod}",
                    detail="Workflow engine is mounted in production without core tests.",
                    recommendation="Add tests/test_workflow_engine.py",
                    source=mod,
                    score_impact=3.0,
                )
            )

    ci_workflow = workspace / ".github" / "workflows" / "ci.yml"
    result.metrics.append(
        MetricValue("ci_workflow", int(ci_workflow.exists()), target=1, status="ok" if ci_workflow.exists() else "fail")
    )

    result.raw["coverage_pct"] = coverage_pct
    result.raw["tests_collected"] = collected
    return result


def _count_collected_tests(workspace: Path) -> int:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--ignore=tests/e2e", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=workspace,
            env={**os.environ, "PYTHONPATH": str(workspace)},
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return 0

    for line in (proc.stdout + proc.stderr).splitlines():
        if " tests collected" in line or " test collected" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part.isdigit() and i + 1 < len(parts) and parts[i + 1] == "tests":
                    return int(part)
                if part.isdigit() and i + 1 < len(parts) and parts[i + 1] == "test":
                    return int(part)
    return 0


def _resolve_coverage(workspace: Path) -> float:
    cache = workspace / CACHE_PATH
    if os.environ.get("AXIOM_GOVERNANCE_FULL") == "1":
        pct = _run_live_coverage(workspace)
        if pct > 0:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps({"line_coverage_pct": pct}) + "\n")
        return pct

    if cache.exists():
        try:
            return float(json.loads(cache.read_text()).get("line_coverage_pct", 0))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    return _estimate_coverage(workspace)


def _run_live_coverage(workspace: Path) -> float:
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--ignore=tests/e2e",
                "-q",
                "--cov=axiom",
                "--cov-report=term-missing:skip-covered",
                "--cov-fail-under=0",
            ],
            capture_output=True,
            text=True,
            cwd=workspace,
            env={**os.environ, "PYTHONPATH": str(workspace)},
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return 0.0

    for line in proc.stdout.splitlines():
        if "TOTAL" in line and "%" in line:
            for part in line.split():
                if part.endswith("%"):
                    try:
                        return float(part.rstrip("%"))
                    except ValueError:
                        pass
    return 0.0


def _estimate_coverage(workspace: Path) -> float:
    """Heuristic when live coverage has not been run."""
    test_files = len(list((workspace / "tests").rglob("test_*.py")))
    py_files = len(list((workspace / "axiom").rglob("*.py")))
    if py_files == 0:
        return 0.0
    ratio = test_files / py_files
    return min(85.0, max(45.0, ratio * 120))


def _count_e2e_tests(workspace: Path) -> int:
    e2e_dir = workspace / "tests" / "e2e"
    if not e2e_dir.exists():
        return 0
    count = 0
    for path in e2e_dir.rglob("test_*.py"):
        try:
            text = path.read_text(encoding="utf-8")
            count += text.count("def test_")
        except OSError:
            continue
    return count
