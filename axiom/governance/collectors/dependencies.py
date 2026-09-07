"""Dependency health monitoring."""

from __future__ import annotations

import json
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


def collect_dependencies(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="dependencies")
    pyproject = workspace / "pyproject.toml"
    ui_package = workspace / "ui" / "package.json"

    result.metrics.append(
        MetricValue("pyproject_present", int(pyproject.exists()), target=1, status="ok" if pyproject.exists() else "fail")
    )
    result.metrics.append(
        MetricValue("ui_package_present", int(ui_package.exists()), target=1, status="ok" if ui_package.exists() else "warn")
    )

    vuln_count = _run_pip_audit(workspace, result)
    result.metrics.append(
        MetricValue("python_vulnerabilities", vuln_count, unit="count", target=0, status=_status_for_count(vuln_count))
    )

    npm_high = _run_npm_audit(workspace, result)
    result.metrics.append(
        MetricValue("npm_high_vulnerabilities", npm_high, unit="count", target=0, status=_status_for_count(npm_high))
    )

    lockfiles = {
        "ui/package-lock.json": (workspace / "ui" / "package-lock.json").exists(),
        "poetry.lock": (workspace / "poetry.lock").exists(),
    }
    for name, present in lockfiles.items():
        if not present and name.startswith("ui"):
            result.findings.append(
                Finding(
                    category=FindingCategory.DEPENDENCY,
                    severity=Severity.MEDIUM,
                    title=f"Missing lockfile: {name}",
                    detail="Reproducible UI builds require a committed lockfile.",
                    recommendation=f"Run npm install in ui/ and commit {name}",
                    source=name,
                    score_impact=2.0,
                )
            )
    result.raw["lockfiles"] = lockfiles
    return result


def _status_for_count(count: int) -> str:
    if count == 0:
        return "ok"
    if count <= 2:
        return "warn"
    return "fail"


def _run_pip_audit(workspace: Path, result: CollectorResult) -> int:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip_audit", "--format=json"],
            capture_output=True,
            text=True,
            cwd=workspace,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        result.findings.append(
            Finding(
                category=FindingCategory.DEPENDENCY,
                severity=Severity.INFO,
                title="pip-audit unavailable",
                detail="Install pip-audit for automated vulnerability scanning.",
                recommendation="make security-audit",
                source="pip-audit",
            )
        )
        return 0

    if proc.returncode != 0 and not proc.stdout.strip():
        return 0

    try:
        data = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return 0

    vulns = data if isinstance(data, list) else data.get("dependencies", [])
    count = 0
    for dep in vulns[:10]:
        name = dep.get("name", "unknown")
        version = dep.get("version", "?")
        for vuln in dep.get("vulns", []):
            count += 1
            result.findings.append(
                Finding(
                    category=FindingCategory.DEPENDENCY,
                    severity=Severity.HIGH,
                    title=f"Vulnerable dependency: {name}=={version}",
                    detail=vuln.get("id", "CVE unknown"),
                    recommendation=f"Upgrade {name} to a patched version",
                    source="pip-audit",
                    score_impact=4.0,
                )
            )
    return count


def _run_npm_audit(workspace: Path, result: CollectorResult) -> int:
    ui_dir = workspace / "ui"
    if not (ui_dir / "package.json").exists():
        return 0
    try:
        proc = subprocess.run(
            ["npm", "audit", "--json"],
            capture_output=True,
            text=True,
            cwd=ui_dir,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0

    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return 0

    metadata = data.get("metadata", {}).get("vulnerabilities", {})
    high = int(metadata.get("high", 0)) + int(metadata.get("critical", 0))
    if high:
        result.findings.append(
            Finding(
                category=FindingCategory.DEPENDENCY,
                severity=Severity.HIGH,
                title=f"npm audit: {high} high/critical vulnerabilities",
                detail=str(metadata),
                recommendation="Run npm audit fix in ui/ or upgrade affected packages",
                source="npm-audit",
                score_impact=3.0,
            )
        )
    return high
