#!/usr/bin/env python3
"""E&R health check — evidence registry, integrity, and reproduction gate."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)

REQUIRED_DOCS = [
    ".axiom/ERL.md",
    "EVIDENCE_STATUS.md",
    "REPRODUCIBILITY_STATUS.md",
    "VERIFICATION_STATUS.md",
    "CLAIM_REGISTRY.md",
    "RESEARCH_INTEGRITY.md",
    "MILLENNIUM_READINESS.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.evidence.integrity import audit_registry
    from axiom.evidence.registry import ClaimRegistry

    print("E&R Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("E&R: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("E&R Phase 2: Registry integrity (empty DB smoke)...")
    registry = ClaimRegistry(":memory:")
    report = audit_registry(registry)
    if not report.ok:
        print("E&R: FAIL — integrity audit on empty registry")
        return 1

    print("E&R Phase 3: Automated tests...")
    result = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_evidence_registry.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return result.returncode

    out_dir = ROOT / ".reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "erl_last_report.json").write_text(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "integrity_ok": report.ok,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("E&R: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
