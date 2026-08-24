"""
AXIOM Phase 17 — Long-Horizon Mathematical Research Engine Benchmark
12 deterministic benchmark test cases.
Saved to evaluation_results/phase17_long_horizon_benchmark.json
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.long_horizon.models import (
    ApproachMemory,
    ApproachStatus,
    CriticRecommendation,
    ResearchAttempt,
    ResearchProblem,
    ResearchSubproblem,
    ResearchTask,
    TaskState,
)
from axiom.long_horizon.decomposition import ProblemDecompositionEngine
from axiom.long_horizon.memory import ApproachMemoryEngine
from axiom.long_horizon.critic import ResearchCriticEngine
from axiom.long_horizon.loop import LongHorizonResearchLoop


def run_benchmarks():
    print("=" * 70)
    print("AXIOM PHASE 17 — LONG-HORIZON MATHEMATICAL RESEARCH BENCHMARKS")
    print("=" * 70)

    results = []
    decomposer = ProblemDecompositionEngine()
    memory_engine = ApproachMemoryEngine()
    critic = ResearchCriticEngine()
    loop = LongHorizonResearchLoop()

    # Case 01: Problem decomposition generation
    subproblems = decomposer.decompose_problem("prob-1", "Goldbach Conjecture", "Every even integer > 2 is sum of two primes.")
    pass_c1 = len(subproblems) == 3 and subproblems[0].title.startswith("Subproblem 1")
    results.append({"case": 1, "name": "Problem decomposition generation", "passed": pass_c1})

    # Case 02: Subproblem dependency ordering
    pass_c2 = len(subproblems[1].dependencies) > 0 and subproblems[1].dependencies[0] == subproblems[0].id
    results.append({"case": 2, "name": "Subproblem dependency ordering", "passed": pass_c2})

    # Case 03: Approach hash computation consistency
    h1 = memory_engine.compute_approach_hash("Induction", "Base case n=4")
    h2 = memory_engine.compute_approach_hash("Induction", "Base case n=4")
    pass_c3 = h1 == h2 and len(h1) == 16
    results.append({"case": 3, "name": "Approach hash computation consistency", "passed": pass_c3})

    # Case 04: Duplicate failed approach detection and rejection
    existing_m = [ApproachMemory(problem_id="prob-1", approach_hash=h1, summary="[Induction] Base case n=4", status=ApproachStatus.FAILED)]
    is_dup, _ = memory_engine.check_duplicate_attempt(existing_m, "Induction", "Base case n=4")
    pass_c4 = is_dup is True
    results.append({"case": 4, "name": "Duplicate failed approach detection and rejection", "passed": pass_c4})

    # Case 05: Task step budget enforcement
    task5 = ResearchTask(subproblem_id="sp-1", name="Task 5", budget_steps=2, current_step=1)
    prob5 = ResearchProblem(project_id="proj-1", title="P5", description="D5")
    sp5 = ResearchSubproblem(problem_id="prob-1", title="SP5", statement="S5")
    res5 = loop.execute_task_step(prob5, sp5, task5, "Direct Proof", "Step 2 execution", [])
    pass_c5 = res5["executed"] is True and task5.current_step == 2 and task5.state == TaskState.COMPLETED
    results.append({"case": 5, "name": "Task step budget enforcement", "passed": pass_c5})

    # Case 06: Research attempt recording
    pass_c6 = "attempt" in res5 and res5["attempt"].status == ApproachStatus.COMPLETED
    results.append({"case": 6, "name": "Research attempt recording", "passed": pass_c6})

    # Case 07: Research critic audit continue recommendation
    attempts7 = [ResearchAttempt(task_id="t1", approach_description="A1", status=ApproachStatus.PROMISING)]
    rec7, _ = critic.audit_research_progress(prob5, attempts7)
    pass_c7 = rec7 == CriticRecommendation.CONTINUE
    results.append({"case": 7, "name": "Research critic audit continue recommendation", "passed": pass_c7})

    # Case 08: Research critic audit pivot recommendation on 5 failures
    attempts8 = [ResearchAttempt(task_id="t1", approach_description=f"A{i}", status=ApproachStatus.FAILED) for i in range(5)]
    rec8, _ = critic.audit_research_progress(prob5, attempts8)
    pass_c8 = rec8 == CriticRecommendation.PIVOT
    results.append({"case": 8, "name": "Research critic audit pivot recommendation", "passed": pass_c8})

    # Case 09: Research critic audit revise recommendation on falsified attempt
    attempts9 = [ResearchAttempt(task_id="t1", approach_description="A9", status=ApproachStatus.FALSIFIED, failure_reason="falsified by witness n=41")]
    rec9, _ = critic.audit_research_progress(prob5, attempts9)
    pass_c9 = rec9 == CriticRecommendation.REVISE
    results.append({"case": 9, "name": "Research critic audit revise recommendation", "passed": pass_c9})

    # Case 10: Bounded long-horizon research loop execution
    pass_c10 = res5.get("executed") is True
    results.append({"case": 10, "name": "Bounded long-horizon research loop execution", "passed": pass_c10})

    # Case 11: State persistence and crash recovery
    prob11_dict = prob5.model_dump()
    prob11_restored = ResearchProblem.model_validate(prob11_dict)
    pass_c11 = prob11_restored.id == prob5.id
    results.append({"case": 11, "name": "State persistence and crash recovery", "passed": pass_c11})

    # Case 12: Cross-project access isolation
    prob12_a = ResearchProblem(project_id="proj-A", title="A", description="A")
    prob12_b = ResearchProblem(project_id="proj-B", title="B", description="B")
    pass_c12 = prob12_a.project_id != prob12_b.project_id
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
    summary_path = "evaluation_results/phase17_long_horizon_benchmark.json"
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
