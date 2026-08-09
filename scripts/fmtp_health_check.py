#!/usr/bin/env python3
"""FMTP health check — formal math registry, pipelines, and verification gate."""

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
    ".axiom/FMTP.md",
    "FORMAL_MATH_STATUS.md",
    "THEOREM_PROVING_STATUS.md",
    "FORMAL_BENCHMARKS.md",
    "PROOF_LIBRARY_STATUS.md",
    "MATHEMATICAL_CAPABILITY.md",
    "MILLENNIUM_READINESS.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.formal_math.formalization import formalize_informal
    from axiom.formal_math.prover_registry import list_provers
    from axiom.formal_math.millennium_gate import evaluate_millennium_readiness

    print("FMTP Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("FMTP: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("FMTP Phase 2: Prover registry smoke...")
    if len(list_provers()) < 3:
        print("FMTP: FAIL — insufficient provers registered")
        return 1

    print("FMTP Phase 3: Formalization pipeline...")
    result = formalize_informal("Prove n + 0 = n for all natural numbers n")
    if not result.formal_spec:
        print("FMTP: FAIL — formalization produced no spec")
        return 1

    print("FMTP Phase 4: Millennium gate sanity...")
    readiness = evaluate_millennium_readiness()
    if readiness.ready:
        print("FMTP: FAIL — millennium gate should not be ready by default")
        return 1

    print("FMTP Phase 5: Automated tests...")
    result_proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_formal_math.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result_proc.stdout)
    if result_proc.returncode != 0:
        print(result_proc.stderr)
        return result_proc.returncode

    out_dir = ROOT / ".reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "fmtp_last_report.json").write_text(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "prover_count": len(list_provers()),
                "millennium_ready": readiness.ready,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("FMTP: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
