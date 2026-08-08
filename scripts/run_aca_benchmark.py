#!/usr/bin/env python3
"""ACA compliance benchmark — verifies all 9 cognitive layers execute."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axiom.cognitive import CognitiveArchitecture, architecture_manifest
from axiom.cognitive.model_provider import HeuristicModelProvider, register_provider


def main() -> int:
    db_path = os.environ.get("DB_PATH", "/tmp/aca_benchmark.db")
    register_provider(HeuristicModelProvider())
    engine = CognitiveArchitecture(db_path, model_provider_id="heuristic")
    manifest = architecture_manifest()

    objectives = [
        ("Prove or disprove: sum of first n integers equals n(n+1)/2", "mathematics"),
        ("Survey literature on graph neural networks for molecules", "research"),
    ]

    results = []
    for objective, domain in objectives:
        start = time.perf_counter()
        cycle = engine.create_cycle(objective=objective, domain=domain, model_provider="heuristic")
        completed = engine.run_full_cycle(cycle.cycle_id)
        duration_ms = (time.perf_counter() - start) * 1000

        layer_subsystems = {
            lo.layer.value: lo.subsystem
            for lo in completed.layer_outputs
        }

        results.append({
            "cycle_id": cycle.cycle_id,
            "objective": objective,
            "domain": domain,
            "model_provider": completed.model_provider,
            "layers_completed": len(completed.layers_completed),
            "layers_required": len(manifest["layers"]),
            "layer_subsystems": layer_subsystems,
            "duration_ms": round(duration_ms, 2),
            "compliant": completed.is_complete(),
        })

    report = {
        "benchmark": "ACA_compliance",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "architecture_layers": len(manifest["layers"]),
        "architecture_pillars": len(manifest["pillars"]),
        "runs": results,
        "all_compliant": all(r["compliant"] for r in results),
        "mean_duration_ms": round(sum(r["duration_ms"] for r in results) / len(results), 2),
    }

    print(json.dumps(report, indent=2))
    with open("aca_benchmark_results.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n✓ Wrote aca_benchmark_results.json")
    return 0 if report["all_compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
