#!/usr/bin/env python3
"""FRCE health check — Frontier Research Campaign Engine integration gate."""

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
    ".axiom/FRCE.md",
    "FRONTIER_CAMPAIGN_ENGINE.md",
    "CAMPAIGN_ORCHESTRATION.md",
    "RESEARCH_CAMPAIGN_SPEC.md",
    "RESEARCH_MEMORY.md",
    "CAMPAIGN_BENCHMARKS.md",
]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from axiom.campaign import FrontierCampaignEngine, LadderLevel

    print("FRCE Phase 1: Governance artifacts...")
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    if missing:
        print("FRCE: FAIL — missing documents:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print("FRCE Phase 2: Campaign lifecycle smoke...")
    engine = FrontierCampaignEngine(":memory:")
    campaign = engine.create_campaign(
        name="FRCE Health Check",
        objective="Verify campaign engine integrates all loops",
        problem_definition="Scope, plan, and run one research cycle.",
        ladder_level=LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH,
    )
    engine.scope(campaign.campaign_id)
    engine.plan(campaign.campaign_id)
    result = engine.run_cycle(campaign.campaign_id)
    if result.get("cycle_number") != 1:
        print(f"FRCE: FAIL — cycle result: {result}")
        return 1

    print("FRCE Phase 3: Dashboard smoke...")
    dash = engine.dashboard(campaign.campaign_id)
    if "loops_integrated" not in engine.manifest() and "next_compute" not in dash:
        print("FRCE: FAIL — dashboard incomplete")
        return 1

    print("FRCE Phase 4: Automated tests...")
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/test_frce_campaign.py", "-q"],
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
    (out_dir / "frce_last_report.json").write_text(
        json.dumps(
            {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "ok": True},
            indent=2,
        ),
        encoding="utf-8",
    )

    print("FRCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
