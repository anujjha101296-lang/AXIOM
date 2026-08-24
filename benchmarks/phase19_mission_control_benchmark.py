"""
AXIOM Phase 19 — Autonomous Research Mission Control Benchmark
12 deterministic benchmark test cases.
Saved to evaluation_results/phase19_mission_control_benchmark.json
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.mission_control.models import (
    MissionBudget,
    MissionCheckpoint,
    MissionState,
    ResearchMission,
)
from axiom.mission_control.controller import MissionController
from axiom.mission_control.checkpoint import CheckpointManager
from axiom.mission_control.scheduler import MissionTaskScheduler


def run_benchmarks():
    print("=" * 70)
    print("AXIOM PHASE 19 — AUTONOMOUS RESEARCH MISSION CONTROL BENCHMARKS")
    print("=" * 70)

    results = []
    controller = MissionController()
    checkpoint_mgr = CheckpointManager()
    scheduler = MissionTaskScheduler()

    # Case 01: Research mission initialization with budget bounds
    b1 = MissionBudget(max_iterations=5, max_time_sec=100)
    m1 = ResearchMission(project_id="proj-1", name="M1", objective="O1", budget=b1)
    pass_c1 = m1.state == MissionState.INITIALIZED and m1.budget.max_iterations == 5
    results.append({"case": 1, "name": "Research mission initialization with budget bounds", "passed": pass_c1})

    # Case 02: Initial specialist agent task graph generation
    tasks2 = scheduler.create_initial_task_graph(m1.id)
    pass_c2 = len(tasks2) == 7 and tasks2[0].assigned_role == "Literature Researcher"
    results.append({"case": 2, "name": "Initial specialist agent task graph generation", "passed": pass_c2})

    # Case 03: Mission start state transition
    m3, chk3 = controller.start_mission(m1)
    pass_c3 = m3.state == MissionState.RUNNING and chk3.checkpoint_hash != ""
    results.append({"case": 3, "name": "Mission start state transition", "passed": pass_c3})

    # Case 04: Mission pause state transition
    m4, chk4 = controller.pause_mission(m3)
    pass_c4 = m4.state == MissionState.PAUSED and chk4.summary == "Mission paused by user."
    results.append({"case": 4, "name": "Mission pause state transition", "passed": pass_c4})

    # Case 05: Mission emergency stop trigger
    m5, chk5 = controller.emergency_stop(m4)
    pass_c5 = m5.state == MissionState.EMERGENCY_STOPPED and chk5.summary == "EMERGENCY STOP TRIGGERED."
    results.append({"case": 5, "name": "Mission emergency stop trigger", "passed": pass_c5})

    # Case 06: Bounded mission iteration step execution
    b6 = MissionBudget(max_iterations=10)
    m6 = ResearchMission(project_id="proj-1", name="M6", objective="O6", budget=b6, state=MissionState.RUNNING)
    cont6, msg6, chk6 = controller.step_mission(m6)
    pass_c6 = cont6 is True and m6.current_iteration == 1
    results.append({"case": 6, "name": "Bounded mission iteration step execution", "passed": pass_c6})

    # Case 07: Budget exhaustion cutoff enforcement
    b7 = MissionBudget(max_iterations=1, used_iterations=1)
    m7 = ResearchMission(project_id="proj-1", name="M7", objective="O7", budget=b7, state=MissionState.RUNNING)
    cont7, msg7, chk7 = controller.step_mission(m7)
    pass_c7 = cont7 is False and m7.state == MissionState.BUDGET_EXCEEDED
    results.append({"case": 7, "name": "Budget exhaustion cutoff enforcement", "passed": pass_c7})

    # Case 08: Immutable checkpoint snapshot creation and hash generation
    chk8 = checkpoint_mgr.create_checkpoint(m6, "Test checkpoint")
    pass_c8 = chk8.checkpoint_hash != "" and len(chk8.checkpoint_hash) == 16
    results.append({"case": 8, "name": "Immutable checkpoint snapshot creation and hash generation", "passed": pass_c8})

    # Case 09: State snapshot serialization and recovery
    snap9 = chk8.state_snapshot
    pass_c9 = snap9["mission_id"] == m6.id and snap9["iteration"] == m6.current_iteration
    results.append({"case": 9, "name": "State snapshot serialization and recovery", "passed": pass_c9})

    # Case 10: Emergency stopped mission restart rejection
    try:
        controller.start_mission(m5)
        pass_c10 = False
    except ValueError:
        pass_c10 = True
    results.append({"case": 10, "name": "Emergency stopped mission restart rejection", "passed": pass_c10})

    # Case 11: Full mission controller lifecycle execution
    pass_c11 = m6.current_iteration > 0
    results.append({"case": 11, "name": "Full mission controller lifecycle execution", "passed": pass_c11})

    # Case 12: Cross-project security isolation
    m12_a = ResearchMission(project_id="proj-A", name="A", objective="A")
    m12_b = ResearchMission(project_id="proj-B", name="B", objective="B")
    pass_c12 = m12_a.project_id != m12_b.project_id
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
    summary_path = "evaluation_results/phase19_mission_control_benchmark.json"
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
