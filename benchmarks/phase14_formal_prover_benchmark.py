#!/usr/bin/env python3
"""Phase 14 Benchmark — Formal Verification & Interactive Theorem Prover Bridge.

Runs 8 deterministic benchmarks covering:
- BM1: Lean 4 natural number commutativity proof
- BM2: Lean 4 tactic script 'sorry' rejection
- BM3: Lean 4 invalid tactic syntax rejection
- BM4: Coq Gallina basic theorem verification
- BM5: Coq 'admit' incomplete proof rejection
- BM6: Isabelle/HOL lemma verification (by simp)
- BM7: Isabelle 'sorry' incomplete proof rejection
- BM8: Multi-prover unified engine routing execution

Run: EMBEDDING_PROVIDER=test ENVIRONMENT=development python benchmarks/phase14_formal_prover_benchmark.py
"""
import json, time, sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.formal_prover.models import (
    FormalTheorem,
    ProverType,
    FormalStatus,
)
from axiom.formal_prover.lean4_bridge import Lean4Bridge
from axiom.formal_prover.coq_bridge import CoqBridge
from axiom.formal_prover.isabelle_bridge import IsabelleBridge
from axiom.formal_prover.engine import FormalVerificationEngine


def run_benchmarks():
    lean4 = Lean4Bridge()
    coq = CoqBridge()
    isabelle = IsabelleBridge()
    engine = FormalVerificationEngine()
    results = []

    print("=" * 65)
    print("AXIOM PHASE 14 — FORMAL PROVER BENCHMARKS")
    print("=" * 65)

    # BM1: Lean 4 valid proof
    t0 = time.time()
    thm1 = FormalTheorem(name="lean4_add_comm", statement="∀ (a b : Nat), a + b = b + a", prover=ProverType.LEAN4)
    r1 = lean4.verify_lean4_script(thm1, "  intro a b\n  omega")
    bm1_ok = (r1.status == FormalStatus.VERIFIED)
    results.append({"benchmark_id": "BM1", "name": "Lean 4 Valid Proof", "passed": bm1_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm1_ok else 'FAILED'}] BM1: Lean 4 Valid Proof ({results[-1]['time_ms']} ms)")

    # BM2: Lean 4 sorry rejection
    t0 = time.time()
    r2 = lean4.verify_lean4_script(thm1, "  sorry")
    bm2_ok = (r2.status == FormalStatus.UNPROVED_SORRY)
    results.append({"benchmark_id": "BM2", "name": "Lean 4 Sorry Rejection", "passed": bm2_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm2_ok else 'FAILED'}] BM2: Lean 4 'sorry' Rejection ({results[-1]['time_ms']} ms)")

    # BM3: Lean 4 syntax rejection
    t0 = time.time()
    r3 = lean4.verify_lean4_script(thm1, "  invalid_tactic_foo")
    bm3_ok = (r3.status == FormalStatus.SYNTAX_ERROR)
    results.append({"benchmark_id": "BM3", "name": "Lean 4 Invalid Syntax Rejection", "passed": bm3_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm3_ok else 'FAILED'}] BM3: Lean 4 Invalid Syntax Rejection ({results[-1]['time_ms']} ms)")

    # BM4: Coq valid proof
    t0 = time.time()
    thm4 = FormalTheorem(name="coq_add_O_n", statement="forall n : nat, 0 + n = n", prover=ProverType.COQ)
    r4 = coq.verify_coq_script(thm4, "  intros n. reflexivity.")
    bm4_ok = (r4.status == FormalStatus.VERIFIED)
    results.append({"benchmark_id": "BM4", "name": "Coq Valid Proof", "passed": bm4_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm4_ok else 'FAILED'}] BM4: Coq Valid Proof ({results[-1]['time_ms']} ms)")

    # BM5: Coq admit rejection
    t0 = time.time()
    r5 = coq.verify_coq_script(thm4, "  admit.")
    bm5_ok = (r5.status == FormalStatus.UNPROVED_SORRY)
    results.append({"benchmark_id": "BM5", "name": "Coq Admit Rejection", "passed": bm5_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm5_ok else 'FAILED'}] BM5: Coq 'admit' Rejection ({results[-1]['time_ms']} ms)")

    # BM6: Isabelle valid proof
    t0 = time.time()
    thm6 = FormalTheorem(name="isabelle_add_comm", statement="((a::nat) + b = b + a)", prover=ProverType.ISABELLE)
    r6 = isabelle.verify_isabelle_script(thm6, "  by simp")
    bm6_ok = (r6.status == FormalStatus.VERIFIED)
    results.append({"benchmark_id": "BM6", "name": "Isabelle/HOL Valid Proof", "passed": bm6_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm6_ok else 'FAILED'}] BM6: Isabelle/HOL Valid Proof ({results[-1]['time_ms']} ms)")

    # BM7: Isabelle sorry rejection
    t0 = time.time()
    r7 = isabelle.verify_isabelle_script(thm6, "  sorry")
    bm7_ok = (r7.status == FormalStatus.UNPROVED_SORRY)
    results.append({"benchmark_id": "BM7", "name": "Isabelle Sorry Rejection", "passed": bm7_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm7_ok else 'FAILED'}] BM7: Isabelle 'sorry' Rejection ({results[-1]['time_ms']} ms)")

    # BM8: Unified Engine Multi-Prover Routing
    t0 = time.time()
    r8 = engine.verify_theorem(thm1, "  intro a b\n  omega")
    bm8_ok = (r8.status == FormalStatus.VERIFIED and r8.prover == ProverType.LEAN4)
    results.append({"benchmark_id": "BM8", "name": "Unified Engine Multi-Prover Routing", "passed": bm8_ok, "time_ms": round((time.time() - t0)*1000, 2)})
    print(f"  [{'PASSED' if bm8_ok else 'FAILED'}] BM8: Unified Engine Multi-Prover Routing ({results[-1]['time_ms']} ms)")

    total_passed = sum(1 for r in results if r["passed"])
    summary = {
        "benchmark_suite": "phase14_formal_prover",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_benchmarks": len(results),
        "passed_benchmarks": total_passed,
        "all_passed": total_passed == len(results),
        "benchmarks": results,
    }

    out_dir = Path(__file__).parent.parent / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase14_formal_prover_benchmark.json"
    out_path.write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 65)
    print(f"BENCHMARK RESULT: {total_passed}/{len(results)} PASSED")
    print(f"Saved to: {out_path}")
    print("=" * 65)
    return summary


if __name__ == "__main__":
    run_benchmarks()
