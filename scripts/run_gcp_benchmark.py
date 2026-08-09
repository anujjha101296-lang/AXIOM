#!/usr/bin/env python3
"""GCP compliance benchmark — validates tier 0 campaign execution."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axiom.grand_challenge import GrandChallengeEngine, program_manifest
from axiom.grand_challenge.models import ChallengeTier


def main() -> int:
    db_path = os.environ.get("DB_PATH", "/tmp/gcp_benchmark.db")
    engine = GrandChallengeEngine(db_path)
    manifest = program_manifest()

    start = time.perf_counter()
    campaign = engine.create_campaign(
        name="GCP Tier 0 Compliance Benchmark",
        description="Automated validation of toy reasoning campaign pipeline",
        tier=ChallengeTier.TIER_0_TOY,
    )
    engine.activate_campaign(campaign.campaign_id)
    completed = engine.run_tier_batch(campaign.campaign_id)
    engine.checkpoint(campaign.campaign_id)
    duration_ms = (time.perf_counter() - start) * 1000

    passed_experiments = sum(1 for e in completed.experiments if e.passed)
    readiness = engine.evaluate_readiness(campaign.campaign_id)

    report = {
        "benchmark": "GCP_compliance",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "program_tiers": len(manifest["tiers"]),
        "program_challenges": manifest["total_challenges"],
        "campaign_id": campaign.campaign_id,
        "experiments_run": len(completed.experiments),
        "experiments_passed": passed_experiments,
        "evidence_records": len(completed.evidence),
        "checkpoints": len(completed.checkpoints),
        "progress_fraction": completed.progress_fraction(),
        "readiness_blockers": readiness["blockers"],
        "duration_ms": round(duration_ms, 2),
        "compliant": passed_experiments >= 2 and len(completed.evidence) >= 2,
    }

    print(json.dumps(report, indent=2))
    with open("gcp_benchmark_results.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✓ Wrote gcp_benchmark_results.json")
    return 0 if report["compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
