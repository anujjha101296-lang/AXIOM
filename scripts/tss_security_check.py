#!/usr/bin/env python3
"""TSS security check — inventory, scan, audit, and report generation."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "SECURITY_STATUS.md",
    "THREAT_MODEL.md",
    "DEPENDENCY_SECURITY.md",
    "AGENT_SECURITY.md",
    "INFRA_SECURITY.md",
    "INCIDENTS.md",
    "SECURITY_SCORECARD.md",
    "SECURITY_INCIDENT_RUNBOOK.md",
    ".axiom/TSS.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.config import settings
    from axiom.security.production_guard import audit_security_config
    from axiom.security.secret_scan import scan_repository_for_secrets

    print("TSS Phase 1: Security inventory...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("TSS: FAIL — missing security documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("TSS Phase 3: Secret scan...")
    secrets = scan_repository_for_secrets(ROOT)
    if secrets:
        print(f"TSS: WARNING — {len(secrets)} potential secret pattern(s):")
        for match in secrets[:10]:
            print(f"  {match.path}:{match.line} [{match.kind}]")
        if len(secrets) > 10:
            print(f"  ... and {len(secrets) - 10} more")

    print("TSS Phase 4: Configuration audit...")
    findings = audit_security_config(settings)
    critical = [f for f in findings if f.severity == "critical"]
    high = [f for f in findings if f.severity == "high"]

    report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "environment": settings.environment,
        "secret_matches": len(secrets),
        "findings": [asdict(f) for f in findings],
    }
    out_dir = ROOT / ".reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tss_last_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("TSS Phase 8: Core tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_tss_security.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return result.returncode

    if critical:
        print("TSS: FAIL — critical configuration findings")
        return 1

    if high or secrets:
        print(f"TSS: PASS with warnings ({len(high)} high, {len(secrets)} secret patterns)")
        return 0

    print("TSS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
