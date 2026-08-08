#!/usr/bin/env python3
"""Research Kernel compliance benchmark — verifies all 10 stages across 3 domains."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axiom.research_kernel import ResearchKernel, kernel_manifest
from axiom.research_kernel.models import STAGE_ORDER


def main() -> int:
    db_path = os.environ.get("DB_PATH", "/tmp/kernel_benchmark.db")
    engine = ResearchKernel(db_path)
    manifest = kernel_manifest()

    objectives = [
        ("Prove sum(1..n) = n(n+1)/2 for all positive integers n", "mathematics"),
        ("Design an O(n log n) sorting algorithm with correctness proof", "computer_science"),
        ("Design a 4-bit adder meeting 500 MHz timing at 28nm", "vlsi_hardware"),
    ]

    results = []
    for objective, plugin_id in objectives:
        start = time.perf_counter()
        run = engine.create_run(objective=objective, plugin_id=plugin_id)
        completed = engine.run_full_cycle(run.run_id)
        duration_ms = (time.perf_counter() - start) * 1000

        stage_subsystems = {
            so.stage.value: so.subsystem
            for so in completed.stage_outputs
        }
        benchmarks = completed.benchmark_results
        passed = sum(1 for b in benchmarks if b.get("passed"))

        results.append({
            "run_id": run.run_id,
            "objective": objective,
            "plugin_id": plugin_id,
            "domain": completed.domain,
            "stages_completed": len(completed.stages_completed),
            "stages_required": len(STAGE_ORDER),
            "stage_subsystems": stage_subsystems,
            "benchmark_count": len(benchmarks),
            "benchmarks_passed": passed,
            "has_report": completed.report is not None,
            "aca_cycle_id": completed.aca_cycle_id,
            "sme_session_id": completed.sme_session_id,
            "duration_ms": round(duration_ms, 2),
            "compliant": (
                completed.is_complete()
                and passed == len(benchmarks)
                and completed.report is not None
            ),
        })

    report = {
        "benchmark": "ResearchKernel_compliance",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kernel_stages": len(STAGE_ORDER),
        "kernel_plugins": len(manifest["plugins"]),
        "runs": results,
        "all_compliant": all(r["compliant"] for r in results),
        "mean_duration_ms": round(sum(r["duration_ms"] for r in results) / len(results), 2),
    }

    print(json.dumps(report, indent=2))
    with open("kernel_benchmark_results.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✓ Wrote kernel_benchmark_results.json")
    return 0 if report["all_compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
