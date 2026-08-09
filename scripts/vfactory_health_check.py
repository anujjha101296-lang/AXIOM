#!/usr/bin/env python3
"""VFACTORY health check — Verification Factory integration gate."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "bin" / "python"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)

REQUIRED_DOCS = [
    "VERIFICATION_STATUS.md",
    "VERIFICATION_MATRIX.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.vfactory.orchestrator import VFactoryOrchestrator

    print("VFACTORY Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("VFACTORY: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("VFACTORY Phase 2: Registry bootstrap...")
    orch = VFactoryOrchestrator(":memory:")
    boot = orch.bootstrap()
    if boot["capabilities_seeded"] < 14:
        print(f"VFACTORY: FAIL — expected >=14 capabilities, got {boot['capabilities_seeded']}")
        return 1

    print("VFACTORY Phase 3: User journeys...")
    for key in ("journey_a", "journey_b", "journey_c", "journey_d"):
        jr = orch.run_journey(key)
        if not jr.passed:
            failed = [s["step"] for s in jr.step_results if not s["passed"]]
            print(f"VFACTORY: FAIL — {key}: {failed}")
            return 1
        print(f"  {key}: PASS ({jr.steps_completed}/{jr.steps_total})")

    print("VFACTORY Phase 4: Verification cycle (journeys only)...")
    vrun = orch.run_verification_cycle(run_pyramid=False, run_journeys=True)
    if not vrun.overall_passed:
        print(f"VFACTORY: FAIL — cycle failures: {vrun.failures}")
        return 1

    print("VFACTORY Phase 5: Automated tests...")
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_vfactory.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr)
        return proc.returncode

    out_dir = ROOT / ".reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "vfactory_last_report.json").write_text(
        json.dumps(
            {
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ok": True,
                "capabilities": boot["capabilities_seeded"],
                "overall_score": boot["overall_score"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("VFACTORY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
