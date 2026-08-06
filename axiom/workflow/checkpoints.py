"""
AXIOM Workflow Engine — Checkpoint & Recovery
=============================================
Save execution state snapshots so a failed workflow can be
replayed from the last successful checkpoint rather than restarting.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Checkpoint, Workflow, Task, TaskStatus

logger = logging.getLogger(__name__)

_DEFAULT_DB = Path(__file__).parent.parent.parent / "axiom.db"


class CheckpointStore:
    """Persists workflow checkpoints to SQLite for recovery."""

    def __init__(self, db_path: str | Path = _DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id                  TEXT PRIMARY KEY,
                    workflow_id         TEXT NOT NULL,
                    task_id             TEXT NOT NULL,
                    completed_task_ids  TEXT NOT NULL DEFAULT '[]',
                    task_outputs_json   TEXT NOT NULL DEFAULT '{}',
                    context_json        TEXT NOT NULL DEFAULT '{}',
                    created_at          TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoints_workflow
                ON checkpoints (workflow_id, created_at)
            """)

    def save(self, checkpoint: Checkpoint) -> Checkpoint:
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO checkpoints
                    (id, workflow_id, task_id, completed_task_ids,
                     task_outputs_json, context_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                checkpoint.id,
                checkpoint.workflow_id,
                checkpoint.task_id,
                json.dumps(checkpoint.completed_task_ids),
                json.dumps(checkpoint.task_outputs),
                json.dumps(checkpoint.context_snapshot),
                checkpoint.created_at.isoformat(),
            ))
        logger.info(f"Checkpoint saved: {checkpoint.id} (after task {checkpoint.task_id})")
        return checkpoint

    def get_latest(self, workflow_id: str) -> Checkpoint | None:
        with self._conn() as conn:
            row = conn.execute("""
                SELECT * FROM checkpoints
                WHERE workflow_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (workflow_id,)).fetchone()
        return self._row_to_checkpoint(row) if row else None

    def get(self, checkpoint_id: str) -> Checkpoint | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM checkpoints WHERE id = ?",
                (checkpoint_id,),
            ).fetchone()
        return self._row_to_checkpoint(row) if row else None

    def list_for_workflow(self, workflow_id: str) -> list[Checkpoint]:
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM checkpoints
                WHERE workflow_id = ?
                ORDER BY created_at ASC
            """, (workflow_id,)).fetchall()
        return [self._row_to_checkpoint(r) for r in rows]

    def _row_to_checkpoint(self, row: sqlite3.Row) -> Checkpoint:
        return Checkpoint(
            id=row["id"],
            workflow_id=row["workflow_id"],
            task_id=row["task_id"],
            completed_task_ids=json.loads(row["completed_task_ids"]),
            task_outputs=json.loads(row["task_outputs_json"]),
            context_snapshot=json.loads(row["context_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )


def apply_checkpoint(workflow: Workflow, checkpoint: Checkpoint) -> Workflow:
    """
    Apply a checkpoint to a workflow object, restoring task states.
    Tasks in completed_task_ids are marked COMPLETED with their saved outputs.
    All other tasks are reset to PENDING.
    Returns the modified workflow.
    """
    completed_ids = set(checkpoint.completed_task_ids)
    for task in workflow.tasks:
        if task.id in completed_ids:
            task.status = TaskStatus.COMPLETED
            task.outputs = checkpoint.task_outputs.get(task.id, {})
        else:
            task.status = TaskStatus.PENDING
            task.retry_count = 0
            task.error = None

    # Restore context working memory
    workflow.context.working_memory = checkpoint.context_snapshot.get("working_memory", {})
    logger.info(
        f"Checkpoint applied: {len(completed_ids)} tasks restored as COMPLETED, "
        f"{len(workflow.tasks) - len(completed_ids)} reset to PENDING"
    )
    return workflow


# Global singleton
_checkpoint_store: CheckpointStore | None = None


def get_checkpoint_store(db_path: str | Path | None = None) -> CheckpointStore:
    global _checkpoint_store
    if _checkpoint_store is None:
        _checkpoint_store = CheckpointStore(db_path or _DEFAULT_DB)
    return _checkpoint_store
