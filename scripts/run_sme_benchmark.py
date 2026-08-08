#!/usr/bin/env python3
"""SME compliance benchmark — measures full 10-phase cycle execution."""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axiom.scientific_method.engine import ScientificMethodEngine
from axiom.scientific_method.models import PHASE_ORDER, SMEPhase


def main() -> int:
    db_path = os.environ.get("DB_PATH", "/tmp/sme_benchmark.db")
    engine = ScientificMethodEngine(db_path)

    objectives = [
        ("Does the sum of the first n integers equal n(n+1)/2?", "mathematics"),
        ("Can graph connectivity be determined in polynomial time?", "research"),
    ]

    results = []
    for objective, domain in objectives:
        start = time.perf_counter()
        session = engine.create_session(objective=objective, domain=domain)
        completed = engine.run_full_cycle(session.session_id)
        duration_ms = (time.perf_counter() - start) * 1000

        results.append({
            "session_id": session.session_id,
            "objective": objective,
            "domain": domain,
            "phases_completed": len(completed.phases_completed),
            "phases_required": len(PHASE_ORDER),
            "hypothesis_count": len(completed.hypotheses),
            "criticism_count": len(completed.criticisms),
            "experiment_count": len(completed.experiments),
            "memory_records": len(completed.memory_records),
            "has_notebook": completed.human_review is not None,
            "duration_ms": round(duration_ms, 2),
            "compliant": completed.is_complete() and len(completed.hypotheses) >= 2,
        })

    report = {
        "benchmark": "SME_compliance",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runs": results,
        "all_compliant": all(r["compliant"] for r in results),
        "mean_duration_ms": round(sum(r["duration_ms"] for r in results) / len(results), 2),
    }

    print(json.dumps(report, indent=2))

    out_path = "sme_benchmark_results.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✓ Wrote {out_path}")

    return 0 if report["all_compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
