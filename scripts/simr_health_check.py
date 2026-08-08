#!/usr/bin/env python3
"""SIMR health check — model/tool registries, routing, and compiler gate."""

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
    ".axiom/SIMR.md",
    "MODEL_REGISTRY.md",
    "TOOL_REGISTRY.md",
    "CAPABILITY_GRAPH.md",
    "MODEL_BENCHMARKS.md",
    "ROUTING_POLICY.md",
    "MODEL_FAILURE_MEMORY.md",
    "RESEARCH_STRATEGIES.md",
    "COST_INTELLIGENCE.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.routing.compiler import compile_research_plan
    from axiom.routing.model_registry import list_models
    from axiom.routing.selector import route_task
    from axiom.routing.tool_registry import list_tools

    print("SIMR Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("SIMR: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("SIMR Phase 2: Registry smoke...")
    if len(list_models()) < 1:
        print("SIMR: FAIL — no models registered")
        return 1
    if len(list_tools()) < 5:
        print("SIMR: FAIL — insufficient tools registered")
        return 1

    print("SIMR Phase 3: Routing determinism...")
    d1 = route_task("Test routing determinism for SIMR health check")
    d2 = route_task("Test routing determinism for SIMR health check")
    if d1.selected_model != d2.selected_model:
        print("SIMR: FAIL — routing model selection not deterministic")
        return 1
    if d1.metadata.get("strategy_type") != d2.metadata.get("strategy_type"):
        print("SIMR: FAIL — routing strategy selection not deterministic")
        return 1

    plan = compile_research_plan("Verify a mathematical lemma")
    if not plan.execution_steps:
        print("SIMR: FAIL — compiler produced empty plan")
        return 1

    print("SIMR Phase 4: Automated tests...")
    result = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_simr_routing.py", "-q"],
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
    (out_dir / "simr_last_report.json").write_text(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model_count": len(list_models()),
                "tool_count": len(list_tools()),
                "sample_model": d1.selected_model,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("SIMR: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
