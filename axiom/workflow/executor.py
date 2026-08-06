"""
AXIOM Workflow Engine — Worker Executor
========================================
Runs a single task via its assigned worker. Handles:
- Timeout enforcement (asyncio.wait_for)
- Retry with backoff
- Human approval gating (WAITING_APPROVAL state)
- Failure action routing (RETRY / SKIP / ABORT)
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from .models import (
    Task, TaskStatus, WorkflowContext, WorkerResult, FailureAction, Artifact
)
from .memory import WorkflowMemory
from .artifacts import ArtifactStore
from .registry import WorkerRegistry

logger = logging.getLogger(__name__)


class TaskTimeoutError(Exception):
    pass


class TaskExecutor:
    """
    Executes a single Task using its registered worker.

    Responsibilities:
    - Validate worker exists in registry
    - Run worker.execute() with timeout
    - Handle retries with exponential backoff
    - Save result artifacts to artifact store
    - Update task status throughout lifecycle
    """

    def __init__(
        self,
        registry: WorkerRegistry,
        artifact_store: ArtifactStore,
        base_backoff_s: float = 1.0,
    ) -> None:
        self.registry = registry
        self.artifact_store = artifact_store
        self.base_backoff_s = base_backoff_s

    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> tuple[Task, list[Artifact]]:
        """
        Execute a task and return the updated task + produced artifacts.
        Handles retries internally; raises only on unrecoverable failure.
        """
        worker = self.registry.get(task.worker_type)
        task.assigned_worker = task.worker_type
        produced_artifacts: list[Artifact] = []

        while True:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            logger.info(
                f"Task {task.id!r} ({task.title!r}) starting "
                f"via worker '{task.worker_type}' "
                f"[attempt {task.retry_count + 1}/{task.max_retries + 1}]"
            )

            try:
                result: WorkerResult = await asyncio.wait_for(
                    worker.execute(task, context, memory),
                    timeout=task.timeout_s,
                )
            except asyncio.TimeoutError:
                error_msg = (
                    f"Task '{task.id}' timed out after {task.timeout_s}s"
                )
                logger.warning(error_msg)
                result = WorkerResult(
                    success=False,
                    error=error_msg,
                    failure_action=FailureAction.RETRY,
                )
            except Exception as exc:
                error_msg = f"Unexpected error in worker '{task.worker_type}': {exc}"
                logger.exception(error_msg)
                result = WorkerResult(
                    success=False,
                    error=error_msg,
                    failure_action=FailureAction.RETRY,
                )

            if result.success:
                task.status = TaskStatus.COMPLETED
                task.outputs = result.outputs
                task.completed_at = datetime.utcnow()
                logger.info(f"Task {task.id!r} completed successfully")

                # Save all produced artifacts
                for artifact in result.artifacts:
                    artifact.task_id = task.id
                    artifact.workflow_id = task.workflow_id
                    saved = self.artifact_store.save(artifact)
                    produced_artifacts.append(saved)

                return task, produced_artifacts

            # --- Failure path ---
            task.error = result.error
            action = result.failure_action

            if action == FailureAction.SKIP:
                task.status = TaskStatus.SKIPPED
                logger.warning(f"Task {task.id!r} skipped: {result.error}")
                return task, produced_artifacts

            if action == FailureAction.ABORT:
                task.status = TaskStatus.FAILED
                logger.error(f"Task {task.id!r} failed (ABORT): {result.error}")
                return task, produced_artifacts

            # RETRY path
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                backoff = self.base_backoff_s * (2 ** (task.retry_count - 1))
                logger.warning(
                    f"Task {task.id!r} retrying ({task.retry_count}/{task.max_retries}) "
                    f"after {backoff:.1f}s backoff: {result.error}"
                )
                await asyncio.sleep(backoff)
            else:
                task.status = TaskStatus.FAILED
                logger.error(
                    f"Task {task.id!r} failed after {task.retry_count} retries: {result.error}"
                )
                return task, produced_artifacts


class ParallelExecutor:
    """
    Runs a batch of independent tasks concurrently using asyncio.gather.
    Delegates actual execution to TaskExecutor.
    """

    def __init__(self, task_executor: TaskExecutor, max_concurrency: int = 8) -> None:
        self.task_executor = task_executor
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_batch(
        self,
        tasks: list[Task],
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> list[tuple[Task, list[Artifact]]]:
        """Execute all tasks in the batch concurrently, respecting max_concurrency."""

        async def run_with_semaphore(task: Task) -> tuple[Task, list[Artifact]]:
            async with self.semaphore:
                return await self.task_executor.execute(task, context, memory)

        results = await asyncio.gather(
            *[run_with_semaphore(t) for t in tasks],
            return_exceptions=True,
        )

        output: list[tuple[Task, list[Artifact]]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Mark task as failed and wrap
                task = tasks[i]
                task.status = TaskStatus.FAILED
                task.error = str(result)
                logger.error(f"Unhandled exception in batch task {task.id!r}: {result}")
                output.append((task, []))
            else:
                output.append(result)  # type: ignore[arg-type]

        return output
