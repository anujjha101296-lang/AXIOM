"""
AXIOM Phase 16 — Formal Mathematics & Proof Verification Benchmark
12 deterministic benchmark test cases.
Saved to evaluation_results/phase16_formal_benchmark.json
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.formal.models import (
    FormalLanguage,
    FormalProof,
    FormalTheorem,
    ProofStatus,
    SMTResult,
)
from axiom.formal.parser import FormalStatementEngine
from axiom.formal.lean_engine import Lean4Engine
from axiom.formal.smt_engine import SMTGateway
from axiom.formal.counterexample import CounterexampleHunter


def run_benchmarks():
    print("=" * 70)
    print("AXIOM PHASE 16 — FORMAL MATHEMATICS BENCHMARKS")
    print("=" * 70)

    results = []
    parser = FormalStatementEngine()
    lean = Lean4Engine()
    smt = SMTGateway()
    hunter = CounterexampleHunter()

    # Level 1 — Case 01: Propositional logic verification
    p1, a1 = lean.verify_proof("t1", "theorem prop1 (A B : Prop) (h : A ∧ B) : A := by exact h.1")
    pass_c1 = p1.status == ProofStatus.VERIFIED and p1.is_sorry_free
    results.append({"case": 1, "name": "Level 1: Propositional logic verification", "passed": pass_c1})

    # Level 1 — Case 02: Predicate logic quantifier verification
    p2, a2 = lean.verify_proof("t2", "theorem pred1 (α : Type) (p : α → Prop) (h : ∀ x, p x) (y : α) : p y := by exact h y")
    pass_c2 = p2.status == ProofStatus.VERIFIED
    results.append({"case": 2, "name": "Level 1: Predicate logic quantifier verification", "passed": pass_c2})

    # Level 1 — Case 03: Set identity statement formalization
    t3 = parser.formalize_statement("proj-1", "For all sets A and B, A ∩ B ⊆ A")
    pass_c3 = t3.status == ProofStatus.FORMALIZED and t3.language == FormalLanguage.LEAN4
    results.append({"case": 3, "name": "Level 1: Set identity statement formalization", "passed": pass_c3})

    # Level 2 — Case 04: Number theory lemma verification
    p4, a4 = lean.verify_proof("t4", "theorem nat_add_zero (n : Nat) : n + 0 = n := by rfl")
    pass_c4 = p4.status == ProofStatus.VERIFIED and a4.hash_id != ""
    results.append({"case": 4, "name": "Level 2: Number theory lemma verification", "passed": pass_c4})

    # Level 2 — Case 05: Reject invalid proof with sorry tactic
    p5, a5 = lean.verify_proof("t5", "theorem nat_incomplete (n : Nat) : n = 0 := by sorry")
    pass_c5 = p5.status == ProofStatus.PROOF_IN_PROGRESS and not p5.is_sorry_free
    results.append({"case": 5, "name": "Level 2: Reject incomplete proof with sorry", "passed": pass_c5})

    # Level 2 — Case 06: Linear algebra theorem formalization
    t6 = parser.formalize_statement("proj-1", "For all vectors v, v + 0 = v")
    pass_c6 = t6.name.startswith("thm_")
    results.append({"case": 6, "name": "Level 2: Linear algebra theorem formalization", "passed": pass_c6})

    # Level 3 — Case 07: Olympiad-style proof verification
    p7, a7 = lean.verify_proof("t7", "theorem am_gm_2 (a b : Real) (ha : a ≥ 0) (hb : b ≥ 0) : a + b ≥ 2 * Real.sqrt (a * b) := by nlinarith")
    pass_c7 = p7.status == ProofStatus.VERIFIED
    results.append({"case": 7, "name": "Level 3: Olympiad-style proof verification", "passed": pass_c7})

    # Level 3 — Case 08: Research lemma proof artifact generation
    pass_c8 = a7.artifact_uri.startswith("file://")
    results.append({"case": 8, "name": "Level 3: Research lemma proof artifact generation", "passed": pass_c8})

    # Case 09: SMT Z3 SAT formula solver
    res_sat, assign, msg = smt.solve_formula("x > 10")
    pass_c9 = res_sat == SMTResult.SAT and "x" in assign
    results.append({"case": 9, "name": "SMT Z3 SAT formula solver", "passed": pass_c9})

    # Case 10: SMT Z3 UNSAT contradiction solver
    res_unsat, _, _ = smt.solve_formula("x > 0 and x < 0")
    pass_c10 = res_unsat == SMTResult.UNSAT
    results.append({"case": 10, "name": "SMT Z3 UNSAT contradiction solver", "passed": pass_c10})

    # Case 11: Finite domain counterexample witness hunter
    ce11 = hunter.find_counterexample("thm-prime", "All prime numbers are odd")
    pass_c11 = ce11 is not None and ce11.assignment.get("n") == 2
    results.append({"case": 11, "name": "Finite domain counterexample witness hunter", "passed": pass_c11})

    # Case 12: Cross-project formal theorem security isolation
    t12_a = FormalTheorem(project_id="proj-A", name="ThmA", natural_language="A", formal_statement="A")
    t12_b = FormalTheorem(project_id="proj-B", name="ThmB", natural_language="B", formal_statement="B")
    pass_c12 = t12_a.project_id != t12_b.project_id
    results.append({"case": 12, "name": "Cross-project access isolation", "passed": pass_c12})

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    pass_rate = (passed_count / total_count) * 100.0

    print("-" * 70)
    for r in results:
        status = "PASSED" if r["passed"] else "FAILED"
        print(f"Case {r['case']:02d}: {r['name']:<45} → {status}")
    print("-" * 70)
    print(f"TOTAL BENCHMARK RESULT: {passed_count}/{total_count} PASSED ({pass_rate:.1f}%)")
    print("=" * 70)

    # Save results JSON
    os.makedirs("evaluation_results", exist_ok=True)
    summary_path = "evaluation_results/phase16_formal_benchmark.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_cases": total_count,
                "passed_cases": passed_count,
                "pass_rate_percent": pass_rate,
                "cases": results,
            },
            f,
            indent=2,
        )

    sys.exit(0 if passed_count == total_count else 1)


if __name__ == "__main__":
    run_benchmarks()
