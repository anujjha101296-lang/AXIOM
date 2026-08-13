"""Budget Controller and Limit Enforcement for Controlled Research Agent."""

from datetime import datetime, timezone
from typing import Any, Optional, Tuple
from pydantic import BaseModel, Field


class BudgetExceededError(Exception):
    """Raised when research agent execution exceeds configured budget limits."""

    pass


class BudgetLimits(BaseModel):
    """Configurable budget limits for a ResearchSession execution."""

    max_steps: int = Field(default=10, ge=1, description="Maximum execution steps allowed")
    max_tool_calls: int = Field(default=15, ge=0, description="Maximum tool calls allowed")
    max_runtime_seconds: float = Field(
        default=120.0, ge=1.0, description="Maximum runtime duration in seconds"
    )

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    @classmethod
    def from_session(cls, session: Any) -> "BudgetLimits":
        """Construct BudgetLimits instance from ResearchSession attributes."""
        return cls(
            max_steps=getattr(session, "max_steps", 10),
            max_tool_calls=getattr(session, "max_tool_calls", 15),
            max_runtime_seconds=float(getattr(session, "max_runtime_seconds", 120.0)),
        )


class BudgetTracker:
    """Tracks step counts, tool call counts, and runtime duration against budget limits."""

    def __init__(
        self,
        max_steps: int = 10,
        max_tool_calls: int = 15,
        max_runtime_seconds: float = 120.0,
        step_count: int = 0,
        tool_call_count: int = 0,
        start_time: Optional[datetime] = None,
        limits: Optional[BudgetLimits] = None,
    ):
        if limits:
            self.max_steps = limits.max_steps
            self.max_tool_calls = limits.max_tool_calls
            self.max_runtime_seconds = limits.max_runtime_seconds
        else:
            self.max_steps = max_steps
            self.max_tool_calls = max_tool_calls
            self.max_runtime_seconds = float(max_runtime_seconds)

        self.step_count = step_count
        self.tool_call_count = tool_call_count
        self.start_time = start_time or datetime.now(timezone.utc)

    @classmethod
    def from_session(cls, session: Any) -> "BudgetTracker":
        """Construct BudgetTracker instance from a ResearchSession model."""
        created_at = getattr(session, "created_at", None)
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return cls(
            max_steps=getattr(session, "max_steps", 10),
            max_tool_calls=getattr(session, "max_tool_calls", 15),
            max_runtime_seconds=float(getattr(session, "max_runtime_seconds", 120.0)),
            step_count=getattr(session, "step_count", 0),
            tool_call_count=getattr(session, "tool_call_count", 0),
            start_time=created_at,
        )

    def increment_step(self, count: int = 1) -> int:
        """Increment current step count."""
        self.step_count += count
        return self.step_count

    def increment_tool_call(self, count: int = 1) -> int:
        """Increment current tool call count."""
        self.tool_call_count += count
        return self.tool_call_count

    @property
    def elapsed_seconds(self) -> float:
        """Calculate elapsed execution time in seconds."""
        now = datetime.now(timezone.utc)
        start = self.start_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        return max(0.0, (now - start).total_seconds())

    def is_budget_exceeded(self) -> Tuple[bool, Optional[str]]:
        """Check if any budget limit (max_steps, max_tool_calls, max_runtime_seconds) is exceeded.

        Returns:
            Tuple[bool, Optional[str]]: (is_exceeded, exhaustion_reason)
        """
        if self.step_count >= self.max_steps:
            reason = (
                f"MAX_STEPS exceeded: Step limit exceeded: "
                f"step_count ({self.step_count}) >= max_steps ({self.max_steps})"
            )
            return True, reason

        if self.tool_call_count >= self.max_tool_calls:
            reason = (
                f"MAX_TOOL_CALLS exceeded: Tool call limit exceeded: "
                f"tool_call_count ({self.tool_call_count}) >= max_tool_calls ({self.max_tool_calls})"
            )
            return True, reason

        if self.elapsed_seconds >= self.max_runtime_seconds:
            reason = (
                f"MAX_RUNTIME_SECONDS exceeded: Runtime limit exceeded: "
                f"runtime_seconds ({self.elapsed_seconds:.1f}s) >= max_runtime_seconds ({self.max_runtime_seconds}s)"
            )
            return True, reason

        return False, None

    def sync_to_session(self, session: Any) -> None:
        """Sync budget counters to ResearchSession model instance."""
        if hasattr(session, "step_count"):
            session.step_count = self.step_count
        if hasattr(session, "tool_call_count"):
            session.tool_call_count = self.tool_call_count


def check_budget_exceeded(
    session: Any, limits: Optional[BudgetLimits] = None
) -> Optional[str]:
    """Check if research session has exceeded max_steps, max_tool_calls, or max_runtime_seconds.

    Args:
        session: ResearchSession instance (or object with session attributes).
        limits: Optional BudgetLimits override. If None, limits are derived from session.

    Returns:
        Optional[str]: Error message string describing exceeded budget limit, or None if within budget.
    """
    tracker = BudgetTracker.from_session(session)
    if limits:
        tracker.max_steps = limits.max_steps
        tracker.max_tool_calls = limits.max_tool_calls
        tracker.max_runtime_seconds = limits.max_runtime_seconds

    exceeded, reason = tracker.is_budget_exceeded()
    return reason if exceeded else None


def enforce_budget(session: Any, limits: Optional[BudgetLimits] = None) -> None:
    """Check budget and raise BudgetExceededError if limits are exceeded."""
    reason = check_budget_exceeded(session, limits=limits)
    if reason:
        raise BudgetExceededError(reason)

