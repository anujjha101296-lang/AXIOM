#!/usr/bin/env python3
"""Phase 15 Benchmark — Full System Integration & Regression Suite.

Executes and verifies pass rates across all system phases:
- Phase 11: Document Intelligence & Vector Retrieval (8/8)
- Phase 12: Autonomous Mathematical Discovery & SMT Prover (8/8)
- Phase 13: 13-Stage Research Workflow Pipeline (8/8)
- Phase 14: Interactive Theorem Prover Bridge (8/8)
- Phase 15: Self-Improvement & System Regression Guard (3/3)

Run: EMBEDDING_PROVIDER=test ENVIRONMENT=development python benchmarks/phase15_system_benchmark.py
"""
import json, time, sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.self_improvement.loop import SelfImprovementLoop
from axiom.self_improvement.models import RegressionStatus


def run_benchmarks():
    t0 = time.time()
    print("=" * 70)
    print("AXIOM PHASE 15 — FULL SYSTEM INTEGRATION & REGRESSION BENCHMARKS")
    print("=" * 70)

    loop = SelfImprovementLoop()
    report = loop.run_cycle(baseline_pass_rate=1.0)

    print(f"\nBaseline Pass Rate : {report.baseline_pass_rate * 100:.1f}%")
    print(f"Current Pass Rate  : {report.current_pass_rate * 100:.1f}%")
    print(f"Regression Status  : {report.regression_status.value}")
    print("\nPhase Benchmark Summaries:")
    print("-" * 70)

    for p in report.phase_summaries:
        print(f"  Phase {p.phase_number:2d}: {p.phase_name:<50} → {p.benchmarks_passed}/{p.benchmarks_total} Passed ({p.pass_rate*100:.0f}%)")

    total_benchmarks = sum(p.benchmarks_total for p in report.phase_summaries)
    total_passed = sum(p.benchmarks_passed for p in report.phase_summaries)
    elapsed = (time.time() - t0) * 1000.0

    summary = {
        "benchmark_suite": "phase15_system_integration",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_benchmarks": total_benchmarks,
        "total_passed": total_passed,
        "overall_pass_rate": report.current_pass_rate,
        "regression_status": report.regression_status.value,
        "execution_time_ms": round(elapsed, 2),
        "phase_summaries": [p.model_dump() for p in report.phase_summaries],
    }

    out_dir = Path(__file__).parent.parent / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase15_system_benchmark.json"
    out_path.write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 70)
    print(f"FINAL SYSTEM BENCHMARK RESULT: {total_passed}/{total_benchmarks} PASSED (Pass Rate: {report.current_pass_rate*100:.1f}%)")
    print(f"Saved to: {out_path}")
    print("=" * 70)
    return summary


if __name__ == "__main__":
    run_benchmarks()
