"""Multi-tier budget controller and error definitions for AXIOM Phase 9."""

import time
from typing import Optional
from axiom.multi_agent.models import TaskNode, TaskState, AgentBudget


class BudgetExceededError(Exception):
    """Raised when run-level, task-level, or agent-level resource limits are exceeded."""

    pass


class MultiTierBudgetController:
    """Controller enforcing resource budgets across Run, Task, and Agent levels."""

    def __init__(
        self,
        max_steps: int = 10,
        max_tool_calls: int = 15,
        max_runtime_seconds: float = 120.0,
    ):
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.max_runtime_seconds = max_runtime_seconds
        self.steps_used = 0
        self.tool_calls_used = 0
        self.start_time = time.time()

    @property
    def step_count(self) -> int:
        return self.steps_used

    @property
    def tool_call_count(self) -> int:
        return self.tool_calls_used

    @property
    def runtime_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def runtime_used(self) -> float:
        return self.runtime_seconds

    def record_step(self, count: int = 1) -> None:
        """Record execution step(s) and enforce run-level step limits."""
        self.steps_used += count
        if self.max_steps > 0 and self.steps_used > self.max_steps:
            raise BudgetExceededError(
                f"Run step budget exceeded ({self.steps_used} > {self.max_steps})."
            )
        self.check_time()

    def record_tool_call(self, count: int = 1) -> None:
        """Record tool call(s) and enforce run-level tool call limits."""
        self.tool_calls_used += count
        if self.max_tool_calls > 0 and self.tool_calls_used > self.max_tool_calls:
            raise BudgetExceededError(
                f"Run tool call budget exceeded ({self.tool_calls_used} > {self.max_tool_calls})."
            )
        self.check_time()

    def check_time(self) -> None:
        """Evaluate accumulated runtime against maximum allowed limit."""
        elapsed = time.time() - self.start_time
        if self.max_runtime_seconds > 0 and elapsed >= self.max_runtime_seconds:
            raise BudgetExceededError(
                f"Run runtime budget exceeded ({elapsed:.2f}s >= {self.max_runtime_seconds}s)."
            )

    def is_exceeded(self) -> bool:
        """Check if any run-level budget limit has been reached or exceeded."""
        elapsed = time.time() - self.start_time
        return (
            (self.max_steps > 0 and self.steps_used >= self.max_steps)
            or (self.max_tool_calls > 0 and self.tool_calls_used >= self.max_tool_calls)
            or (self.max_runtime_seconds > 0 and elapsed >= self.max_runtime_seconds)
        )

    def check_node_budget(self, node: TaskNode) -> None:
        """Check if node's task-level budget is exceeded, updating node state if breached."""
        if node.budget.is_exceeded():
            node.transition_to(TaskState.BUDGET_EXCEEDED, error_message="Task step limit reached.")
            raise BudgetExceededError(f"Task '{node.task_id}' step limit reached.")
