"""
axiom.long_horizon.loop
======================
Bounded Long-Horizon Research Loop.
Coordinates problem decomposition, approach memory validation, step execution, and milestone creation.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from axiom.long_horizon.critic import ResearchCriticEngine
from axiom.long_horizon.decomposition import ProblemDecompositionEngine
from axiom.long_horizon.memory import ApproachMemoryEngine
from axiom.long_horizon.models import (
    ApproachMemory,
    ApproachStatus,
    CriticRecommendation,
    ResearchAttempt,
    ResearchMilestone,
    ResearchProblem,
    ResearchSubproblem,
    ResearchTask,
    TaskState,
)


class LongHorizonResearchLoop:
    """Orchestrates long-horizon research cycles with strict step/budget bounds."""

    def __init__(self):
        self.decomposer = ProblemDecompositionEngine()
        self.memory_engine = ApproachMemoryEngine()
        self.critic = ResearchCriticEngine()

    def execute_task_step(
        self,
        problem: ResearchProblem,
        subproblem: ResearchSubproblem,
        task: ResearchTask,
        method: str,
        approach_description: str,
        memories: List[ApproachMemory],
    ) -> Dict[str, Any]:
        """
        Execute a single research task step with duplicate attempt detection.
        """
        # Step 1: Duplicate attempt check
        is_dup, matching_mem = self.memory_engine.check_duplicate_attempt(memories, method, approach_description)
        if is_dup and matching_mem:
            return {
                "executed": False,
                "reason": "DUPLICATE_FAILED_APPROACH",
                "message": f"Duplicate approach rejected. Prior failure recorded: '{matching_mem.summary}'.",
                "matching_memory": matching_mem,
            }

        # Step 2: Increment budget step
        task.current_step += 1
        if task.current_step >= task.budget_steps:
            task.state = TaskState.COMPLETED

        # Step 3: Record attempt
        attempt = ResearchAttempt(
            task_id=task.id,
            approach_description=approach_description,
            method=method,
            result_summary=f"Executed step {task.current_step}/{task.budget_steps} for task '{task.name}'.",
            status=ApproachStatus.COMPLETED if task.state == TaskState.COMPLETED else ApproachStatus.PROMISING,
        )

        app_hash = self.memory_engine.compute_approach_hash(method, approach_description)
        new_memory = ApproachMemory(
            problem_id=problem.id,
            approach_hash=app_hash,
            summary=f"[{method}] {approach_description}",
            status=attempt.status,
        )

        return {
            "executed": True,
            "attempt": attempt,
            "memory": new_memory,
            "task": task,
        }
