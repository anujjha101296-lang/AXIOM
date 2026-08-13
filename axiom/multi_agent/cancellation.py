"""Async cancellation gateway for Phase 9 Multi-Agent Execution Engine."""

from typing import Optional
from axiom.multi_agent.models import TaskGraph, TaskState


class AsyncCancellationGateway:
    """Manages cancellation tokens and persistent cancellation state across runs."""

    def __init__(self):
        self._is_cancelled: bool = False

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    @is_cancelled.setter
    def is_cancelled(self, value: bool) -> None:
        self._is_cancelled = bool(value)

    def cancel(self) -> None:
        """Set cancellation token state to True."""
        self._is_cancelled = True

    def apply_cancellation(self, graph: TaskGraph) -> int:
        """Halt scheduling and transition all PENDING and READY nodes to CANCELLED state.

        Completed, failed, and budget-exceeded node states are preserved intact.

        Returns:
            int: Total number of nodes updated to CANCELLED.
        """
        cancelled_count = 0
        for node in graph.nodes.values():
            if node.state in {TaskState.PENDING, TaskState.READY}:
                node.transition_to(TaskState.CANCELLED, error_message="Task cancelled by cancellation token.")
                cancelled_count += 1
        return cancelled_count
