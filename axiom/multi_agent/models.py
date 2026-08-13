"""Data models for AXIOM Phase 9 Controlled Multi-Agent System."""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field, model_validator


class TaskState(str, Enum):
    """Lifecycle states for a task in the TaskGraph."""

    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


class AgentRole(str, Enum):
    """Specialist agent roles within the multi-agent system."""

    ORCHESTRATOR = "ORCHESTRATOR"
    RESEARCHER = "RESEARCHER"
    ANALYST = "ANALYST"
    CRITIC = "CRITIC"
    VERIFIER = "VERIFIER"
    SYNTHESIS = "SYNTHESIS"


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal TaskState transition is attempted on a TaskNode."""

    pass


class AgentBudget(BaseModel):
    """Resource budget and usage tracker for an agent task execution."""

    max_steps: int = Field(default=10, description="Maximum execution steps allowed")
    max_tool_calls: int = Field(default=20, description="Maximum tool calls allowed")
    max_runtime_seconds: float = Field(default=300.0, description="Maximum runtime allowed in seconds")
    step_count: int = Field(default=0, description="Number of steps executed so far")
    tool_call_count: int = Field(default=0, description="Number of tool calls executed so far")
    runtime_seconds: float = Field(default=0.0, description="Runtime accumulated in seconds")

    @model_validator(mode="before")
    @classmethod
    def _alias_used_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "steps_used" in data and "step_count" not in data:
                data["step_count"] = data["steps_used"]
            if "tool_calls_used" in data and "tool_call_count" not in data:
                data["tool_call_count"] = data["tool_calls_used"]
            if "runtime_used" in data and "runtime_seconds" not in data:
                data["runtime_seconds"] = data["runtime_used"]
        return data

    @property
    def steps_used(self) -> int:
        return self.step_count

    @steps_used.setter
    def steps_used(self, value: int) -> None:
        self.step_count = value

    @property
    def tool_calls_used(self) -> int:
        return self.tool_call_count

    @tool_calls_used.setter
    def tool_calls_used(self, value: int) -> None:
        self.tool_call_count = value

    @property
    def runtime_used(self) -> float:
        return self.runtime_seconds

    @runtime_used.setter
    def runtime_used(self, value: float) -> None:
        self.runtime_seconds = value

    def is_exceeded(self) -> bool:
        """Check if any budget threshold has been reached or exceeded."""
        return (
            (self.max_steps <= 0 or self.step_count >= self.max_steps)
            or (self.max_tool_calls > 0 and self.tool_call_count >= self.max_tool_calls)
            or (self.max_runtime_seconds > 0 and self.runtime_seconds >= self.max_runtime_seconds)
        )


# Explicit allowed transitions between states
VALID_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.PENDING: {TaskState.READY, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.READY: {TaskState.RUNNING, TaskState.CANCELLED, TaskState.BLOCKED, TaskState.BUDGET_EXCEEDED},
    TaskState.RUNNING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED, TaskState.BUDGET_EXCEEDED},
    TaskState.BLOCKED: set(),
    TaskState.COMPLETED: set(),
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
    TaskState.BUDGET_EXCEEDED: set(),
}


class TaskNode(BaseModel):
    """Node in the TaskGraph representing a single subtask assigned to a specialist agent."""

    task_id: str = Field(..., description="Unique identifier for the task node")
    agent_role: AgentRole = Field(..., description="Specialist agent role responsible for this task")
    description: str = Field(..., description="Human-readable description of the subtask")
    depends_on: List[str] = Field(default_factory=list, description="IDs of task nodes this task depends upon")
    state: TaskState = Field(default=TaskState.PENDING, description="Current lifecycle state of the task")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and payloads")
    output_artifact_id: Optional[str] = Field(default=None, description="ID of generated artifact if completed")
    budget: AgentBudget = Field(default_factory=AgentBudget, description="Budget allocated to this task")
    error_message: Optional[str] = Field(default=None, description="Error message if task failed or was blocked")

    def transition_to(self, new_state: TaskState, error_message: Optional[str] = None) -> TaskState:
        """Validate and apply a state transition for this node.

        Raises:
            InvalidStateTransitionError: If the transition from current state to new_state is invalid.
        """
        if isinstance(new_state, str):
            new_state = TaskState(new_state)

        if new_state == self.state:
            if error_message is not None:
                self.error_message = error_message
            return self.state

        allowed_next = VALID_TRANSITIONS.get(self.state, set())
        if new_state not in allowed_next:
            raise InvalidStateTransitionError(
                f"Cannot transition task '{self.task_id}' from state '{self.state.value}' to '{new_state.value}'"
            )

        self.state = new_state
        if error_message is not None:
            self.error_message = error_message
        return self.state


def transition_node_state(node: TaskNode, new_state: TaskState, error_message: Optional[str] = None) -> TaskState:
    """Helper function to transition node state."""
    return node.transition_to(new_state, error_message=error_message)


class TaskGraph(BaseModel):
    """Container representing a DAG of task nodes."""

    nodes: Dict[str, TaskNode] = Field(default_factory=dict, description="Map of task_id to TaskNode")

    def add_node(self, node: TaskNode) -> None:
        """Add a TaskNode to the graph.

        Raises:
            ValueError: If a node with the same task_id already exists in the graph.
        """
        if node.task_id in self.nodes:
            raise ValueError(f"Task node with ID '{node.task_id}' already exists in TaskGraph.")
        self.nodes[node.task_id] = node

    def get_node(self, task_id: str) -> Optional[TaskNode]:
        """Retrieve a TaskNode by task_id."""
        return self.nodes.get(task_id)

    def is_acyclic(self) -> bool:
        """Return True if graph contains no cycles."""
        from axiom.multi_agent.graph import topological_sort, TaskGraphCycleError
        try:
            topological_sort(self)
            return True
        except (TaskGraphCycleError, ValueError):
            return False

