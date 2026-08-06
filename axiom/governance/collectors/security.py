"""Security scanning and posture checks."""

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

SECRET_PATTERNS = [
    (re.compile(r'JWT_SECRET_KEY\s*=\s*["\']dev-secret'), "Default JWT secret in config"),
    (re.compile(r'api_token\s*=\s*["\']test_token'), "Hardcoded test API token"),
    (re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.I), "Hardcoded password string"),
]

SECURITY_DOCS = ("docs/SECURITY.md", ".github/workflows/security.yml")


def collect_security(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="security")
    workflow = workspace / ".github" / "workflows" / "security.yml"
    dependabot = workspace / ".github" / "dependabot.yml"

    result.metrics.append(
        MetricValue("security_workflow", int(workflow.exists()), target=1, status="ok" if workflow.exists() else "fail")
    )
    result.metrics.append(
        MetricValue("dependabot_config", int(dependabot.exists()), target=1, status="ok" if dependabot.exists() else "warn")
    )

    if not workflow.exists():
        result.findings.append(
            Finding(
                category=FindingCategory.SECURITY,
                severity=Severity.HIGH,
                title="No security CI workflow",
                detail="Automated dependency audits are not scheduled.",
                recommendation="Add .github/workflows/security.yml with pip-audit and npm audit",
                source=".github/workflows",
                score_impact=5.0,
            )
        )

    secret_hits = _scan_secrets(workspace)
    result.metrics.append(
        MetricValue("secret_pattern_hits", secret_hits, target=0, status="ok" if secret_hits == 0 else "warn")
    )

    settings_py = workspace / "axiom" / "config" / "settings.py"
    if settings_py.exists():
        text = settings_py.read_text(encoding="utf-8", errors="ignore")
        if (
            "production" in text.lower()
            and "jwt_secret" in text.lower()
            and "fail" not in text.lower()
            and "raise" not in text.lower()
        ):
            result.findings.append(
                Finding(
                    category=FindingCategory.SECURITY,
                    severity=Severity.HIGH,
                    title="No production JWT secret enforcement",
                    detail="Startup should fail when default JWT secret is used in production.",
                    recommendation="Add environment check in settings startup validation",
                    source="axiom/config/settings.py",
                    score_impact=6.0,
                )
            )

    for doc in SECURITY_DOCS:
        if not (workspace / doc).exists():
            result.findings.append(
                Finding(
                    category=FindingCategory.SECURITY,
                    severity=Severity.MEDIUM,
                    title=f"Missing security doc: {doc}",
                    detail="Security posture should be documented for contributors.",
                    recommendation=f"Create {doc} with threat model and audit cadence",
                    source=doc,
                    score_impact=2.0,
                )
            )

    result.findings.append(
        Finding(
            category=FindingCategory.SECURITY,
            severity=Severity.CRITICAL,
            title="No per-user data isolation",
            detail="All authenticated users share the same research data store.",
            recommendation="Scope all research queries by user_id before any external pilot",
            source="MVP_READINESS.md",
            score_impact=10.0,
        )
    )

    return result


def _scan_secrets(workspace: Path) -> int:
    hits = 0
    scan_paths = [
        workspace / "axiom" / "config",
        workspace / ".env.example",
    ]
    for base in scan_paths:
        if base.is_file():
            files = [base]
        elif base.is_dir():
            files = list(base.rglob("*.py")) + list(base.rglob("*.env*"))
        else:
            continue
        for path in files:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern, _ in SECRET_PATTERNS:
                if pattern.search(text):
                    hits += 1
    return hits
