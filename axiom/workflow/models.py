"""
AXIOM Workflow Engine — Domain Model
=====================================
All core domain objects for the Autonomous Workflow Engine.
Fully domain-agnostic: no math, no papers, no Lean 4.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─── Enumerations ────────────────────────────────────────────────────────────


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    WAITING_APPROVAL = "waiting_approval"
    CANCELLED = "cancelled"


class ArtifactType(str, Enum):
    RESEARCH_NOTE = "research_note"
    ARCH_DECISION = "arch_decision"
    CODE_PATCH = "code_patch"
    KNOWLEDGE_OBJECT = "knowledge_object"
    PROOF_ATTEMPT = "proof_attempt"
    BENCHMARK = "benchmark"
    REVIEW = "review"
    EXPERIMENT = "experiment"
    ISSUE = "issue"
    REPORT = "report"
    PLAN = "plan"
    SUMMARY = "summary"


class FailureAction(str, Enum):
    RETRY = "retry"
    SKIP = "skip"
    ABORT = "abort"


class EventType(str, Enum):
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_SKIPPED = "task.skipped"
    TASK_RETRYING = "task.retrying"
    TASK_APPROVAL_REQUESTED = "task.approval_requested"
    TASK_APPROVED = "task.approved"
    ARTIFACT_CREATED = "artifact.created"
    ARTIFACT_UPDATED = "artifact.updated"
    CHECKPOINT_SAVED = "checkpoint.saved"
    WORKER_REGISTERED = "worker.registered"


# ─── Core Domain Models ───────────────────────────────────────────────────────


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.utcnow()


class Task(BaseModel):
    """A unit of work within a workflow, executed by a specific worker."""

    id: str = Field(default_factory=_new_id)
    workflow_id: str = ""
    title: str
    description: str = ""
    worker_type: str  # Must match a registered worker's worker_type
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)  # List of task IDs
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 2
    timeout_s: float = 300.0  # 5 minutes default
    require_approval: bool = False
    assigned_worker: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerCapability(BaseModel):
    """Describes a single capability of a worker."""

    name: str
    description: str
    input_keys: list[str] = Field(default_factory=list)
    output_keys: list[str] = Field(default_factory=list)


class WorkerSpec(BaseModel):
    """Declarative specification of a worker — what it does, needs, and produces."""

    worker_type: str
    mission: str
    description: str = ""
    capabilities: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)   # JSON Schema
    output_schema: dict[str, Any] = Field(default_factory=dict)  # JSON Schema
    memory_access: bool = False   # Can read/write workflow working memory
    tool_access: list[str] = Field(default_factory=list)  # Tool names available
    success_criteria: list[str] = Field(default_factory=list)
    failure_criteria: list[str] = Field(default_factory=list)
    version: str = "1.0.0"


class WorkflowContext(BaseModel):
    """Shared context passed to every worker during execution."""

    objective: str
    domain: str = "general"  # e.g. "research", "math", "engineering"
    metadata: dict[str, Any] = Field(default_factory=dict)
    working_memory: dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    """A versioned, typed output produced by a worker."""

    id: str = Field(default_factory=_new_id)
    task_id: str
    workflow_id: str
    artifact_type: ArtifactType
    version: int = 1
    title: str = ""
    content: dict[str, Any] = Field(default_factory=dict)  # Structured content
    text_content: str = ""  # Human-readable content
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Checkpoint(BaseModel):
    """Snapshot of workflow execution state for recovery."""

    id: str = Field(default_factory=_new_id)
    workflow_id: str
    task_id: str  # Task that just completed, triggering this checkpoint
    completed_task_ids: list[str] = Field(default_factory=list)
    task_outputs: dict[str, dict[str, Any]] = Field(default_factory=dict)  # task_id -> outputs
    context_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


class WorkflowEvent(BaseModel):
    """Immutable event in the workflow event log."""

    id: str = Field(default_factory=_new_id)
    workflow_id: str
    task_id: str | None = None
    event_type: EventType
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class Workflow(BaseModel):
    """The top-level workflow object — an objective decomposed into a task DAG."""

    id: str = Field(default_factory=_new_id)
    objective: str
    domain: str = "general"
    tasks: list[Task] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    context: WorkflowContext = Field(default_factory=lambda: WorkflowContext(objective=""))
    checkpoints: list[Checkpoint] = Field(default_factory=list)
    events: list[WorkflowEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None

    def get_task(self, task_id: str) -> Task | None:
        return next((t for t in self.tasks if t.id == task_id), None)

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        return [t for t in self.tasks if t.status == status]

    def is_terminal(self) -> bool:
        return self.status in (
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        )


# ─── Result Objects ───────────────────────────────────────────────────────────


class WorkerResult(BaseModel):
    """The result returned by a worker after executing a task."""

    success: bool
    outputs: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[Artifact] = Field(default_factory=list)
    error: str | None = None
    failure_action: FailureAction = FailureAction.RETRY
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowResult(BaseModel):
    """Final result returned by the WorkflowEngine after a run completes."""

    workflow_id: str
    status: WorkflowStatus
    objective: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    skipped_tasks: int
    artifacts: list[Artifact] = Field(default_factory=list)
    final_report: Artifact | None = None
    duration_s: float = 0.0
    error: str | None = None


# ─── Scheduling Structures ────────────────────────────────────────────────────


class TaskBatch(BaseModel):
    """A batch of tasks that can be executed in parallel."""

    batch_index: int
    tasks: list[Task]


class SchedulePlan(BaseModel):
    """Complete execution schedule: ordered batches of parallel tasks."""

    workflow_id: str
    batches: list[TaskBatch]
    total_tasks: int
    max_parallelism: int  # Max tasks in any single batch
