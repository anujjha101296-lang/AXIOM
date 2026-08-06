"""
AXIOM Workflow Engine — Dependency-Aware Parallel Scheduler
============================================================
Accepts a list of Tasks with depends_on[] edges and returns
an ordered list of TaskBatches — tasks that can run concurrently
within each batch, ordered such that all dependencies are satisfied.

Algorithm: Kahn's topological sort adapted for batch parallelism.
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque

from .models import Task, TaskBatch, SchedulePlan, TaskStatus

logger = logging.getLogger(__name__)


class CyclicDependencyError(Exception):
    """Raised when a circular dependency is detected in the task DAG."""
    pass


class MissingDependencyError(Exception):
    """Raised when a task depends_on a task ID that doesn't exist."""
    pass


class WorkflowScheduler:
    """
    Dependency-aware batch scheduler using Kahn's algorithm.

    Given a list of Tasks (possibly with depends_on references),
    produces a SchedulePlan — an ordered list of TaskBatches where
    tasks within each batch have no dependencies on each other and
    can be run in parallel safely.
    """

    def build_plan(self, workflow_id: str, tasks: list[Task]) -> SchedulePlan:
        """
        Build an execution schedule from a task list.

        Raises:
            CyclicDependencyError: if the dependency graph has cycles
            MissingDependencyError: if depends_on references unknown task IDs
        """
        if not tasks:
            return SchedulePlan(workflow_id=workflow_id, batches=[], total_tasks=0, max_parallelism=0)

        task_map = {t.id: t for t in tasks}

        # Validate all dependencies exist
        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id not in task_map:
                    raise MissingDependencyError(
                        f"Task '{task.id}' ({task.title!r}) depends on unknown task '{dep_id}'"
                    )

        # Build in-degree and adjacency structures
        in_degree: dict[str, int] = {t.id: 0 for t in tasks}
        dependents: dict[str, list[str]] = defaultdict(list)  # dep_id -> list[task_id]

        for task in tasks:
            for dep_id in task.depends_on:
                in_degree[task.id] += 1
                dependents[dep_id].append(task.id)

        # Kahn's algorithm — build batches
        batches: list[TaskBatch] = []
        queue: deque[str] = deque(
            task_id for task_id, deg in in_degree.items() if deg == 0
        )
        processed = 0

        while queue:
            # All tasks in current queue are ready at the same time → one batch
            batch_ids = list(queue)
            queue.clear()

            batch_tasks = [task_map[tid] for tid in batch_ids]
            batches.append(TaskBatch(batch_index=len(batches), tasks=batch_tasks))
            processed += len(batch_ids)

            # Reduce in-degree for downstream tasks
            for task_id in batch_ids:
                for dependent_id in dependents[task_id]:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)

        if processed != len(tasks):
            # Not all tasks were processed → cycle detected
            remaining = [tid for tid, deg in in_degree.items() if deg > 0]
            raise CyclicDependencyError(
                f"Circular dependency detected in task graph. "
                f"Stuck tasks: {remaining}"
            )

        max_parallelism = max((len(b.tasks) for b in batches), default=0)
        logger.info(
            f"Scheduler: {len(tasks)} tasks → {len(batches)} batches, "
            f"max parallelism={max_parallelism}"
        )

        return SchedulePlan(
            workflow_id=workflow_id,
            batches=batches,
            total_tasks=len(tasks),
            max_parallelism=max_parallelism,
        )

    def get_ready_tasks(self, tasks: list[Task]) -> list[Task]:
        """
        Return tasks that are currently ready to execute:
        - Status is PENDING
        - All depends_on tasks are COMPLETED
        """
        completed_ids = {t.id for t in tasks if t.status == TaskStatus.COMPLETED}
        return [
            t for t in tasks
            if t.status == TaskStatus.PENDING
            and all(dep in completed_ids for dep in t.depends_on)
        ]

    def has_unresolvable_deadlock(self, tasks: list[Task]) -> bool:
        """
        Check if any non-terminal tasks are blocked by failed tasks.
        Returns True if a deadlock is detected that cannot be resolved.
        """
        failed_ids = {t.id for t in tasks if t.status == TaskStatus.FAILED}
        if not failed_ids:
            return False

        active_statuses = {TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.RETRYING}
        for task in tasks:
            if task.status in active_statuses:
                if any(dep in failed_ids for dep in task.depends_on):
                    return True
        return False
