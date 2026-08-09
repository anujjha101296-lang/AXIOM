#!/usr/bin/env python3
"""CEL health check — verify governance artifacts and core test gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ".axiom/CEL.md",
    ".axiom/CURRENT_STATE.md",
    ".axiom/TASK_QUEUE.md",
    "TECH_DEBT.md",
    "BENCHMARK_RESULTS.md",
    "ENGINEERING_SCORECARD.md",
    "PRODUCT_SCORECARD.md",
    "docs/S0-E4_evidence_gate.md",
]


def main() -> int:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing:
        print("CEL health: FAIL — missing artifacts:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("CEL health: artifacts OK")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--ignore=tests/e2e", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("CEL health: FAIL — core tests")
        return result.returncode

    print("CEL health: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
