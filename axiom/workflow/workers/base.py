"""
AXIOM Workflow Engine — BaseWorker Abstract Class
==================================================
All workers implement this interface.
Workers are domain-agnostic reusable components, not one-off prompts.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Task, WorkflowContext, WorkerResult, FailureAction
from ..memory import WorkflowMemory


class BaseWorker(ABC):
    """
    Abstract base for all AXIOM workflow workers.

    A worker encapsulates:
    - A mission statement (what it does)
    - Capabilities (what domains/operations it supports)
    - An execute() method that processes a Task and returns a WorkerResult

    Workers must be:
    - Stateless between tasks (state goes into memory or artifacts)
    - Idempotent (safe to retry with the same inputs)
    - Domain-agnostic at the interface level
    """

    worker_type: str  # Unique identifier (used in task.worker_type)
    mission: str      # One-line description of purpose
    capabilities: list[str] = []  # List of capability strings
    version: str = "1.0.0"

    @abstractmethod
    async def execute(
        self,
        task: Task,
        context: WorkflowContext,
        memory: WorkflowMemory,
    ) -> WorkerResult:
        """
        Execute a task and return the result.

        Args:
            task: The task to execute (contains inputs, description, etc.)
            context: Shared workflow context (objective, domain, metadata)
            memory: Per-workflow working memory (read/write key-value)

        Returns:
            WorkerResult with success flag, outputs dict, and any artifacts
        """
        ...

    async def validate_input(self, inputs: dict) -> tuple[bool, str]:
        """
        Validate task inputs before execution.
        Returns (is_valid, error_message).
        Override to add input validation.
        """
        return True, ""

    async def on_failure(self, task: Task, error: Exception) -> FailureAction:
        """
        Determine what to do when this worker fails.
        Override to customize failure handling.
        """
        return FailureAction.RETRY

    def __repr__(self) -> str:
        return f"<Worker type={self.worker_type!r} mission={self.mission!r}>"
