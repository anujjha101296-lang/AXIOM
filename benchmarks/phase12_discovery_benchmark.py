#!/usr/bin/env python3
"""Phase 12 Discovery Benchmark

Runs 8 deterministic discovery and automated theorem proving benchmarks:
- BM1: Polynomial-exponential series summation discovery
- BM2: Higher-order polynomial series closed form
- BM3: Cubic algebraic sum discovery
- BM4: Arithmetic-geometric progression closed form
- BM5: Quadratic polynomial sum discovery
- BM6: Cubic inequality SMT proof (x^3 + y^3 < (x+y)^3)
- BM7: Convex inequality SMT proof (2*(x^2 + y^2) >= (x+y)^2)
- BM8: Full end-to-end autonomous discovery cycle execution

Run: EMBEDDING_PROVIDER=test ENVIRONMENT=development python benchmarks/phase12_discovery_benchmark.py
"""
import json, time, sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.discovery.generator import ConjectureGenerator
from axiom.discovery.prover import AutomatedProver
from axiom.discovery.pipeline import DiscoveryPipeline
from axiom.discovery.models import ProofStatus, CandidateConjecture, FormulaType


def run_benchmarks():
    gen = ConjectureGenerator()
    prover = AutomatedProver()
    results = []

    print("=" * 65)
    print("AXIOM PHASE 12 — DISCOVERY ENGINE BENCHMARKS")
    print("=" * 65)

    sum_cands = gen.generate_summation_candidates()
    ineq_cands = gen.generate_inequality_candidates()

    # BM1..BM5: Summation series proofs
    for idx, cand in enumerate(sum_cands, 1):
        res = prover.prove_summation(cand)
        passed = (res.status == ProofStatus.PROVED)
        results.append({
            "benchmark_id": f"BM{idx}",
            "name": f"Summation: {cand.expression_str}",
            "passed": passed,
            "status": res.status.value,
            "closed_form": res.closed_form,
            "time_ms": res.verification_time_ms
        })
        status_str = "PASSED" if passed else "FAILED"
        print(f"  [{status_str}] BM{idx}: {cand.expression_str:<25} → {res.closed_form} ({res.verification_time_ms:.2f} ms)")

    # BM6..BM7: SMT inequality proofs
    for idx, cand in enumerate(ineq_cands, 6):
        res = prover.verify_inequality_smt(cand)
        passed = (res.status == ProofStatus.PROVED)
        results.append({
            "benchmark_id": f"BM{idx}",
            "name": f"SMT Inequality: {cand.expression_str}",
            "passed": passed,
            "status": res.status.value,
            "time_ms": res.verification_time_ms
        })
        status_str = "PASSED" if passed else "FAILED"
        print(f"  [{status_str}] BM{idx}: {cand.expression_str:<25} → {res.proof_method} ({res.verification_time_ms:.2f} ms)")

    # BM8: Pipeline end-to-end run
    t0 = time.time()
    pipeline = DiscoveryPipeline()
    pipe_report = pipeline.run_discovery_cycle()
    pipe_elapsed = (time.time() - t0) * 1000.0
    bm8_passed = (pipe_report["proved"] >= 7 and pipe_report["disproved"] == 0)
    results.append({
        "benchmark_id": "BM8",
        "name": "End-to-End Discovery Cycle",
        "passed": bm8_passed,
        "total_candidates": pipe_report["total_candidates"],
        "proved": pipe_report["proved"],
        "time_ms": round(pipe_elapsed, 2)
    })
    status_str = "PASSED" if bm8_passed else "FAILED"
    print(f"  [{status_str}] BM8: End-to-End Discovery Cycle    → Proved {pipe_report['proved']}/{pipe_report['total_candidates']} ({pipe_elapsed:.2f} ms)")

    total_passed = sum(1 for r in results if r["passed"])
    summary = {
        "benchmark_suite": "phase12_discovery",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_benchmarks": len(results),
        "passed_benchmarks": total_passed,
        "all_passed": total_passed == len(results),
        "benchmarks": results
    }

    out_dir = Path(__file__).parent.parent / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase12_discovery_benchmark.json"
    out_path.write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 65)
    print(f"BENCHMARK RESULT: {total_passed}/{len(results)} PASSED")
    print(f"Saved to: {out_path}")
    print("=" * 65)
    return summary


if __name__ == "__main__":
    run_benchmarks()
