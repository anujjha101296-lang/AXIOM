"""
AXIOM Workflow Engine — Main Orchestrator
==========================================
WorkflowEngine coordinates the full lifecycle of a workflow:
  submit → plan → schedule → execute (parallel batches) → checkpoint → report

Integrates with:
  - axiom.core.events.bus.EventBus  (existing singleton)
  - WorkflowScheduler               (DAG-aware batch planner)
  - ParallelExecutor                (concurrent task runner)
  - ArtifactStore                   (versioned output storage)
  - CheckpointStore                 (recovery snapshots)
  - WorkflowMemory                  (per-run working memory)
  - WorkflowStore                   (SQLite run persistence)
"""
from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import (
    Workflow, WorkflowStatus, Task, TaskStatus, WorkflowContext,
    WorkflowResult, WorkflowEvent, EventType, Checkpoint,
)
from .scheduler import WorkflowScheduler, CyclicDependencyError
from .executor import TaskExecutor, ParallelExecutor
from .artifacts import ArtifactStore, get_artifact_store
from .checkpoints import CheckpointStore, get_checkpoint_store, apply_checkpoint
from .memory import MemoryManager, get_memory_manager
from .registry import WorkerRegistry, get_registry

# Use the existing AXIOM EventBus
from axiom.core.events.bus import event_bus as _global_event_bus, AxiomEvent

logger = logging.getLogger(__name__)

_DEFAULT_DB = Path(__file__).parent.parent.parent / "axiom.db"


# ─── Workflow Persistence Store ───────────────────────────────────────────────


class WorkflowStore:
    """SQLite persistence for workflow run state."""

    def __init__(self, db_path: str | Path = _DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    id           TEXT PRIMARY KEY,
                    objective    TEXT NOT NULL,
                    domain       TEXT NOT NULL DEFAULT 'general',
                    status       TEXT NOT NULL DEFAULT 'pending',
                    tasks_json   TEXT NOT NULL DEFAULT '[]',
                    context_json TEXT NOT NULL DEFAULT '{}',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    error        TEXT,
                    created_at   TEXT NOT NULL,
                    started_at   TEXT,
                    completed_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_events (
                    id          TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    task_id     TEXT,
                    event_type  TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    timestamp   TEXT NOT NULL,
                    PRIMARY KEY (id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_wf_events_workflow
                ON workflow_events (workflow_id, timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_wf_runs_status
                ON workflow_runs (status)
            """)

    def save(self, workflow: Workflow) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO workflow_runs
                    (id, objective, domain, status, tasks_json,
                     context_json, metadata_json, error,
                     created_at, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow.id,
                workflow.objective,
                workflow.domain,
                workflow.status.value,
                json.dumps([t.model_dump(mode="json") for t in workflow.tasks]),
                json.dumps(workflow.context.model_dump(mode="json")),
                json.dumps(workflow.metadata),
                workflow.error,
                workflow.created_at.isoformat(),
                workflow.started_at.isoformat() if workflow.started_at else None,
                workflow.completed_at.isoformat() if workflow.completed_at else None,
            ))

    def save_event(self, event: WorkflowEvent) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO workflow_events
                    (id, workflow_id, task_id, event_type, payload_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.workflow_id,
                event.task_id,
                event.event_type.value,
                json.dumps(event.payload),
                event.timestamp.isoformat(),
            ))

    def get(self, workflow_id: str) -> Workflow | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM workflow_runs WHERE id = ?", (workflow_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_workflow(row)

    def list(
        self,
        status: WorkflowStatus | None = None,
        limit: int = 50,
    ) -> list[Workflow]:
        with self._conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM workflow_runs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                    (status.value, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM workflow_runs ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [self._row_to_workflow(r) for r in rows]

    def get_events(self, workflow_id: str) -> list[WorkflowEvent]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM workflow_events WHERE workflow_id = ? ORDER BY timestamp ASC",
                (workflow_id,),
            ).fetchall()
        return [
            WorkflowEvent(
                id=r["id"],
                workflow_id=r["workflow_id"],
                task_id=r["task_id"],
                event_type=EventType(r["event_type"]),
                payload=json.loads(r["payload_json"]),
                timestamp=datetime.fromisoformat(r["timestamp"]),
            )
            for r in rows
        ]

    def _row_to_workflow(self, row: sqlite3.Row) -> Workflow:
        tasks_data = json.loads(row["tasks_json"])
        tasks = [Task(**t) for t in tasks_data]
        context_data = json.loads(row["context_json"])
        return Workflow(
            id=row["id"],
            objective=row["objective"],
            domain=row["domain"],
            status=WorkflowStatus(row["status"]),
            tasks=tasks,
            context=WorkflowContext(**context_data),
            metadata=json.loads(row["metadata_json"]),
            error=row["error"],
            created_at=datetime.fromisoformat(row["created_at"]),
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
        )


# ─── Workflow Engine ──────────────────────────────────────────────────────────


class WorkflowEngine:
    """
    Main orchestrator for the AXIOM Autonomous Workflow Engine.

    Lifecycle:
        engine = WorkflowEngine()
        workflow = engine.create_workflow(objective="...", domain="research")
        result   = await engine.run(workflow.id)
    """

    def __init__(
        self,
        registry: WorkerRegistry | None = None,
        artifact_store: ArtifactStore | None = None,
        checkpoint_store: CheckpointStore | None = None,
        memory_manager: MemoryManager | None = None,
        db_path: str | Path = _DEFAULT_DB,
        max_concurrency: int = 8,
    ) -> None:
        self.registry = registry or get_registry()
        self.artifact_store = artifact_store or get_artifact_store(db_path)
        self.checkpoint_store = checkpoint_store or get_checkpoint_store(db_path)
        self.memory_manager = memory_manager or get_memory_manager()
        self.store = WorkflowStore(db_path)
        self.scheduler = WorkflowScheduler()

        task_exec = TaskExecutor(self.registry, self.artifact_store)
        self.parallel_exec = ParallelExecutor(task_exec, max_concurrency)

        # Active cancellation signals
        self._cancel_signals: dict[str, asyncio.Event] = {}
        # Approval signals: {workflow_id: {task_id: asyncio.Event}}
        self._approval_signals: dict[str, dict[str, asyncio.Event]] = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def create_workflow(
        self,
        objective: str,
        domain: str = "general",
        metadata: dict[str, Any] | None = None,
    ) -> Workflow:
        """Create and persist a new workflow. Does NOT start execution."""
        context = WorkflowContext(objective=objective, domain=domain)
        workflow = Workflow(
            objective=objective,
            domain=domain,
            context=context,
            metadata=metadata or {},
        )
        self.store.save(workflow)
        self._emit(WorkflowEvent(
            workflow_id=workflow.id,
            event_type=EventType.WORKFLOW_CREATED,
            payload={"objective": objective, "domain": domain},
        ))
        logger.info(f"WorkflowEngine: created workflow {workflow.id!r}: {objective!r}")
        return workflow

    async def run(self, workflow_id: str) -> WorkflowResult:
        """
        Execute a workflow end-to-end.

        Flow:
          1. Load workflow
          2. PlannerWorker builds task DAG (if no tasks yet)
          3. Scheduler produces batches
          4. Execute batches (parallel within each)
          5. Checkpoint after every completed batch
          6. ReporterWorker generates final report
          7. Return WorkflowResult
        """
        workflow = self.store.get(workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        if workflow.is_terminal():
            raise ValueError(
                f"Workflow '{workflow_id}' is already in terminal state '{workflow.status}'"
            )

        # Set up cancel signal
        cancel_event = asyncio.Event()
        self._cancel_signals[workflow_id] = cancel_event
        self._approval_signals[workflow_id] = {}

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        self.store.save(workflow)
        self._emit(WorkflowEvent(
            workflow_id=workflow_id,
            event_type=EventType.WORKFLOW_STARTED,
            payload={"objective": workflow.objective},
        ))

        memory = await self.memory_manager.get_or_create(workflow_id)
        t_start = time.monotonic()

        try:
            result = await self._execute(workflow, memory, cancel_event)
        except asyncio.CancelledError:
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.utcnow()
            self.store.save(workflow)
            result = self._build_result(workflow, [], time.monotonic() - t_start)
        except Exception as exc:
            logger.exception(f"Workflow {workflow_id!r} failed with unhandled error")
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(exc)
            workflow.completed_at = datetime.utcnow()
            self.store.save(workflow)
            result = self._build_result(workflow, [], time.monotonic() - t_start)
        finally:
            self._cancel_signals.pop(workflow_id, None)
            self._approval_signals.pop(workflow_id, None)

        return result

    async def pause(self, workflow_id: str) -> None:
        """Pause a running workflow (completes current batch, then stops)."""
        workflow = self.store.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            self.store.save(workflow)
            logger.info(f"WorkflowEngine: paused {workflow_id!r}")

    async def resume(self, workflow_id: str) -> WorkflowResult:
        """Resume a paused workflow, replaying from the latest checkpoint."""
        workflow = self.store.get(workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        checkpoint = self.checkpoint_store.get_latest(workflow_id)
        if checkpoint:
            workflow = apply_checkpoint(workflow, checkpoint)
            logger.info(f"WorkflowEngine: resuming from checkpoint {checkpoint.id!r}")

        workflow.status = WorkflowStatus.PENDING
        self.store.save(workflow)
        return await self.run(workflow_id)

    async def cancel(self, workflow_id: str) -> None:
        """Cancel a running workflow. In-flight tasks finish; new tasks won't start."""
        ev = self._cancel_signals.get(workflow_id)
        if ev:
            ev.set()
        workflow = self.store.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.CANCELLED
            self.store.save(workflow)
        self._emit(WorkflowEvent(
            workflow_id=workflow_id,
            event_type=EventType.WORKFLOW_CANCELLED,
        ))
        logger.info(f"WorkflowEngine: cancellation requested for {workflow_id!r}")

    async def approve(self, workflow_id: str, task_id: str) -> None:
        """Unblock a task waiting for human approval."""
        signals = self._approval_signals.get(workflow_id, {})
        ev = signals.get(task_id)
        if ev:
            ev.set()
            self._emit(WorkflowEvent(
                workflow_id=workflow_id,
                task_id=task_id,
                event_type=EventType.TASK_APPROVED,
            ))

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self.store.get(workflow_id)

    def list_workflows(
        self, status: WorkflowStatus | None = None, limit: int = 50
    ) -> list[Workflow]:
        return self.store.list(status=status, limit=limit)

    def get_artifacts(self, workflow_id: str) -> list:
        return self.artifact_store.get_by_workflow(workflow_id)

    def get_events(self, workflow_id: str) -> list[WorkflowEvent]:
        return self.store.get_events(workflow_id)

    def get_checkpoints(self, workflow_id: str) -> list[Checkpoint]:
        return self.checkpoint_store.list_for_workflow(workflow_id)

    async def replay_from_checkpoint(
        self, workflow_id: str, checkpoint_id: str
    ) -> WorkflowResult:
        """Replay a workflow from a specific checkpoint."""
        workflow = self.store.get(workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        checkpoint = self.checkpoint_store.get(checkpoint_id)
        if checkpoint is None:
            raise ValueError(f"Checkpoint '{checkpoint_id}' not found")
        workflow = apply_checkpoint(workflow, checkpoint)
        workflow.status = WorkflowStatus.PENDING
        self.store.save(workflow)
        return await self.run(workflow_id)

    # ── Internal execution ────────────────────────────────────────────────────

    async def _execute(
        self,
        workflow: Workflow,
        memory,
        cancel_event: asyncio.Event,
    ) -> WorkflowResult:
        t_start = time.monotonic()
        all_artifacts = []

        # Step 1: Planning — if no tasks, run the planner
        if not workflow.tasks:
            await self._run_planning(workflow, memory)

        # Step 2: Schedule
        try:
            plan = self.scheduler.build_plan(workflow.id, workflow.tasks)
        except CyclicDependencyError as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.utcnow()
            self.store.save(workflow)
            return self._build_result(workflow, all_artifacts, time.monotonic() - t_start)

        # Step 3: Execute batches
        for batch in plan.batches:
            if cancel_event.is_set():
                workflow.status = WorkflowStatus.CANCELLED
                break

            # Handle approval gates
            approval_tasks = [t for t in batch.tasks if t.require_approval]
            for task in approval_tasks:
                await self._request_approval(workflow, task)

            # Filter out already-completed tasks (from checkpoint restore)
            runnable = [t for t in batch.tasks if t.status == TaskStatus.PENDING]
            if not runnable:
                continue

            logger.info(
                f"Executing batch {batch.batch_index}: "
                f"{[t.title for t in runnable]}"
            )

            batch_results = await self.parallel_exec.execute_batch(
                runnable, workflow.context, memory
            )

            for task, artifacts in batch_results:
                # Update task in workflow
                for i, wf_task in enumerate(workflow.tasks):
                    if wf_task.id == task.id:
                        workflow.tasks[i] = task
                        break
                all_artifacts.extend(artifacts)
                self._emit_task_event(workflow.id, task)

            # Check for deadlock
            if self.scheduler.has_unresolvable_deadlock(workflow.tasks):
                logger.error(f"Deadlock detected in workflow {workflow.id!r}")
                workflow.status = WorkflowStatus.FAILED
                workflow.error = "Unresolvable deadlock: a required upstream task failed"
                break

            # Checkpoint after each batch
            completed_ids = [t.id for t in workflow.tasks if t.status == TaskStatus.COMPLETED]
            task_outputs = {
                t.id: t.outputs
                for t in workflow.tasks
                if t.status == TaskStatus.COMPLETED
            }
            mem_snapshot = await memory.snapshot()
            checkpoint = Checkpoint(
                workflow_id=workflow.id,
                task_id=batch.tasks[-1].id,
                completed_task_ids=completed_ids,
                task_outputs=task_outputs,
                context_snapshot=mem_snapshot,
            )
            self.checkpoint_store.save(checkpoint)
            self._emit(WorkflowEvent(
                workflow_id=workflow.id,
                event_type=EventType.CHECKPOINT_SAVED,
                payload={"checkpoint_id": checkpoint.id, "completed": len(completed_ids)},
            ))

            self.store.save(workflow)

        # Step 4: Final status
        if not cancel_event.is_set() and workflow.status == WorkflowStatus.RUNNING:
            failed = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
            if failed:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = f"{len(failed)} task(s) failed"
            else:
                workflow.status = WorkflowStatus.COMPLETED

        workflow.completed_at = datetime.utcnow()
        self.store.save(workflow)
        self._emit(WorkflowEvent(
            workflow_id=workflow.id,
            event_type=(
                EventType.WORKFLOW_COMPLETED
                if workflow.status == WorkflowStatus.COMPLETED
                else EventType.WORKFLOW_FAILED
            ),
            payload={"status": workflow.status.value},
        ))

        return self._build_result(workflow, all_artifacts, time.monotonic() - t_start)

    async def _run_planning(self, workflow: Workflow, memory) -> None:
        """
        Use the PlannerWorker to decompose the objective into tasks.
        Updates workflow.tasks in place.
        """
        planner = self.registry.get("planner")
        planning_task = Task(
            workflow_id=workflow.id,
            title="Plan workflow tasks",
            description=f"Decompose objective into tasks: {workflow.objective}",
            worker_type="planner",
            inputs={
                "objective": workflow.objective,
                "domain": workflow.domain,
                "context": workflow.context.metadata,
            },
        )
        result = await planner.execute(planning_task, workflow.context, memory)
        if result.success and "tasks" in result.outputs:
            task_defs = result.outputs["tasks"]
            workflow.tasks = [
                Task(
                    workflow_id=workflow.id,
                    title=td.get("title", "Untitled"),
                    description=td.get("description", ""),
                    worker_type=td.get("worker_type", "researcher"),
                    inputs=td.get("inputs", {}),
                    depends_on=td.get("depends_on", []),
                    max_retries=td.get("max_retries", 2),
                    timeout_s=td.get("timeout_s", 300.0),
                    require_approval=td.get("require_approval", False),
                )
                for td in task_defs
            ]
            self.store.save(workflow)
            logger.info(f"Planner produced {len(workflow.tasks)} tasks")

    async def _request_approval(self, workflow: Workflow, task: Task) -> None:
        """Gate execution until human approval is received via approve()."""
        task.status = TaskStatus.WAITING_APPROVAL
        self._emit(WorkflowEvent(
            workflow_id=workflow.id,
            task_id=task.id,
            event_type=EventType.TASK_APPROVAL_REQUESTED,
            payload={"task_title": task.title},
        ))
        approval_ev = asyncio.Event()
        self._approval_signals.setdefault(workflow.id, {})[task.id] = approval_ev
        logger.info(f"Task {task.id!r} ({task.title!r}) waiting for approval")
        await approval_ev.wait()
        task.status = TaskStatus.PENDING

    def _emit(self, event: WorkflowEvent) -> None:
        """Publish a WorkflowEvent to the global AXIOM EventBus."""
        self.store.save_event(event)
        axiom_event = AxiomEvent(
            topic=f"workflow.{event.event_type.value}",
            payload={
                **event.payload,
                "workflow_id": event.workflow_id,
                "task_id": event.task_id,
            },
            source="workflow_engine",
        )
        _global_event_bus.publish_sync(axiom_event)

    def _emit_task_event(self, workflow_id: str, task: Task) -> None:
        status_to_event = {
            TaskStatus.COMPLETED: EventType.TASK_COMPLETED,
            TaskStatus.FAILED: EventType.TASK_FAILED,
            TaskStatus.SKIPPED: EventType.TASK_SKIPPED,
        }
        event_type = status_to_event.get(task.status)
        if event_type:
            self._emit(WorkflowEvent(
                workflow_id=workflow_id,
                task_id=task.id,
                event_type=event_type,
                payload={
                    "title": task.title,
                    "worker_type": task.worker_type,
                    "retry_count": task.retry_count,
                    "error": task.error,
                },
            ))

    def _build_result(
        self, workflow: Workflow, artifacts: list, duration_s: float
    ) -> WorkflowResult:
        completed = [t for t in workflow.tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
        skipped = [t for t in workflow.tasks if t.status == TaskStatus.SKIPPED]

        all_artifacts = self.artifact_store.get_by_workflow(workflow.id)
        from .models import ArtifactType
        reports = [a for a in all_artifacts if a.artifact_type == ArtifactType.REPORT]
        final_report = reports[-1] if reports else None

        return WorkflowResult(
            workflow_id=workflow.id,
            status=workflow.status,
            objective=workflow.objective,
            total_tasks=len(workflow.tasks),
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            skipped_tasks=len(skipped),
            artifacts=all_artifacts,
            final_report=final_report,
            duration_s=duration_s,
            error=workflow.error,
        )


# ─── Module-level convenience ─────────────────────────────────────────────────

_default_engine: WorkflowEngine | None = None


def get_engine(db_path: str | Path = _DEFAULT_DB) -> WorkflowEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = WorkflowEngine(db_path=db_path)
    return _default_engine
