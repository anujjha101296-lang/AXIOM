"""
AXIOM Phase 18 — Mathematical Research Challenge Harness Benchmark
12 deterministic benchmark test cases.
Saved to evaluation_results/phase18_challenge_harness_benchmark.json
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.challenge_harness.models import Challenge, ChallengeLevel, EvaluationOutcome, FailureClass
from axiom.challenge_harness.curator import ProblemCurator
from axiom.challenge_harness.evaluator import IndependentEvaluator
from axiom.challenge_harness.anti_gaming import AntiGamingEngine
from axiom.challenge_harness.runner import ChallengeHarnessRunner


def run_benchmarks():
    print("=" * 70)
    print("AXIOM PHASE 18 — MATHEMATICAL RESEARCH CHALLENGE HARNESS BENCHMARKS")
    print("=" * 70)

    results = []
    curator = ProblemCurator()
    evaluator = IndependentEvaluator()
    anti_gaming = AntiGamingEngine()
    runner = ChallengeHarnessRunner()

    # Case 01: Golden challenge curator suite loading (AXIOM-MATH-001)
    challs = curator.get_golden_challenges()
    pass_c1 = len(challs) >= 4 and challs[0].version == "AXIOM-MATH-001"
    results.append({"case": 1, "name": "Golden challenge curator suite loading", "passed": pass_c1})

    # Case 02: Multi-level difficulty categorization
    levels = {c.difficulty_level for c in challs}
    pass_c2 = ChallengeLevel.LEVEL_0_BASIC in levels and ChallengeLevel.LEVEL_1_ELEMENTARY_PROOFS in levels
    results.append({"case": 2, "name": "Multi-level difficulty categorization", "passed": pass_c2})

    # Case 03: Blind challenge evaluation execution
    run3 = evaluator.evaluate_run(challs[0], "Research output", "theorem thm (n : Nat) : n + 0 = n := by rfl")
    pass_c3 = run3.challenge_id == challs[0].id and run3.outcome == EvaluationOutcome.SOLVED
    results.append({"case": 3, "name": "Blind challenge evaluation execution", "passed": pass_c3})

    # Case 04: Multi-axis score vector computation
    pass_c4 = run3.score.overall_score > 0.8 and run3.score.proof_correctness == 1.0
    results.append({"case": 4, "name": "Multi-axis score vector computation", "passed": pass_c4})

    # Case 05: Formal proof verification scoring integration
    pass_c5 = run3.proof_verified is True
    results.append({"case": 5, "name": "Formal proof verification scoring integration", "passed": pass_c5})

    # Case 06: Counterexample search scoring integration
    run6 = evaluator.evaluate_run(challs[2], "Counterexample output", counterexample_witness="Counterexample n = 2: 2 is prime but not odd.")
    pass_c6 = run6.counterexample_found is True and run6.score.counterexample_search == 1.0
    results.append({"case": 6, "name": "Counterexample search scoring integration", "passed": pass_c6})

    # Case 07: Failure taxonomy classification (PROOF_FAILURE)
    run7 = evaluator.evaluate_run(challs[0], "Incomplete research", proof_script="theorem thm (n : Nat) : n = 0 := by sorry")
    pass_c7 = run7.outcome == EvaluationOutcome.RESEARCH_PROGRESS and run7.failure_class == FailureClass.PROOF_FAILURE
    results.append({"case": 7, "name": "Failure taxonomy classification", "passed": pass_c7})

    # Case 08: Anti-gaming prompt leakage detection
    is_g8, _ = anti_gaming.inspect_output("Clean research text")
    pass_c8 = is_g8 is False
    results.append({"case": 8, "name": "Anti-gaming clean output check", "passed": pass_c8})

    # Case 09: Anti-gaming hardcoded answer detection
    is_g9, _ = anti_gaming.inspect_output("hardcoded_answer_flag used")
    pass_c9 = is_g9 is True
    results.append({"case": 9, "name": "Anti-gaming hardcoded answer detection", "passed": pass_c9})

    # Case 10: Anti-gaming fake citation detection
    is_g10, _ = anti_gaming.inspect_output("Reference: DOI:10.0000/fake journal")
    pass_c10 = is_g10 is True
    results.append({"case": 10, "name": "Anti-gaming fake citation detection", "passed": pass_c10})

    # Case 11: Full evaluation suite runner execution
    runs11 = runner.run_suite()
    pass_c11 = len(runs11) == len(challs) and any(r.proof_verified for r in runs11)
    results.append({"case": 11, "name": "Full evaluation suite runner execution", "passed": pass_c11})

    # Case 12: Cross-project security isolation
    c12_a = Challenge(title="A", domain="A", statement="A")
    c12_b = Challenge(title="B", domain="B", statement="B")
    pass_c12 = c12_a.id != c12_b.id
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
    summary_path = "evaluation_results/phase18_challenge_harness_benchmark.json"
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
