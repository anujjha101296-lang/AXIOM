#!/usr/bin/env python3
"""SEC health check — experiment kernel, sandbox, and integrity gate."""

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
    ".axiom/SEC.md",
    "EXPERIMENT_ENGINE.md",
    "COMPUTE_RUNTIME.md",
    "EXPERIMENT_SPEC.md",
    "REPRODUCTION_GUIDE.md",
    "EXPERIMENT_SECURITY.md",
    "COMPUTE_BENCHMARKS.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.experiment.sandbox import execute_sandboxed
    from axiom.experiment.models import ResourceBudget
    from axiom.experiment.store import ExperimentStore
    from axiom.experiment.executor import execute_experiment
    from axiom.experiment.models import ExperimentSpec

    print("SEC Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("SEC: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("SEC Phase 2: Sandbox smoke...")
    result = execute_sandboxed("print('sec_ok')", budget=ResourceBudget(timeout_seconds=5.0))
    if not result.success:
        print("SEC: FAIL — sandbox execution failed")
        return 1

    print("SEC Phase 3: Experiment lifecycle...")
    store = ExperimentStore(":memory:")
    spec = ExperimentSpec(
        research_question="Health check",
        hypothesis="Sandbox works",
        objective="Verify SEC loop",
        code="print('lifecycle_ok')",
    )
    exp = store.create_experiment(spec)
    run = execute_experiment(store, exp.experiment_id)
    if run["status"] != "COMPLETED":
        print(f"SEC: FAIL — lifecycle run: {run}")
        return 1

    print("SEC Phase 4: Automated tests...")
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_experiment_sec.py", "-q"],
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
    (out_dir / "sec_last_report.json").write_text(
        json.dumps(
            {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "ok": True},
            indent=2,
        ),
        encoding="utf-8",
    )

    print("SEC: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
