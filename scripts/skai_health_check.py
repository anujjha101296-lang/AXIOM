#!/usr/bin/env python3
"""SKAI health check — knowledge acquisition and intelligence loop."""

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
    ".axiom/SKAI.md",
    "KNOWLEDGE_ACQUISITION.md",
    "KNOWLEDGE_GRAPH_SPEC.md",
    "SOURCE_QUALITY.md",
    "KNOWLEDGE_SYNTHESIS.md",
    "KNOWLEDGE_BENCHMARKS.md",
]

SAMPLE_LATEX = r"""
\begin{theorem}[Test Theorem]
For all $n$, $n + 0 = n$.
\end{theorem}
"""


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.skai import SkaiOrchestrator

    print("SKAI Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("SKAI: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("SKAI Phase 2: Acquisition smoke...")
    orch = SkaiOrchestrator(":memory:")
    result = orch.acquire_from_text(
        "Health Check Paper",
        SAMPLE_LATEX,
        research_question="Test arithmetic identity",
        is_latex=True,
        bridge_to_egs=True,
        bridge_to_er=True,
    )
    if not result.entities:
        print("SKAI: FAIL — no entities extracted")
        return 1

    print("SKAI Phase 3: Synthesis smoke...")
    synthesis = orch.synthesize_knowledge("Test arithmetic identity")
    if "retrieval" not in synthesis:
        print("SKAI: FAIL — synthesis incomplete")
        return 1

    print("SKAI Phase 4: Automated tests...")
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_skai_knowledge.py", "-q"],
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
    (out_dir / "skai_last_report.json").write_text(
        json.dumps(
            {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "ok": True},
            indent=2,
        ),
        encoding="utf-8",
    )

    print("SKAI: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
