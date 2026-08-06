"""
AXIOM Workflow Engine — Working Memory
========================================
Per-workflow working memory layer that caches active research context
across task executions without requiring a restart.

Separated from long-term SQLite epistemic store.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class WorkflowMemory:
    """
    In-memory key-value store scoped to a single workflow execution.

    Stores:
    - Active hypotheses
    - Failed attempts
    - Open questions
    - Intermediate results
    - Accumulated knowledge from completed tasks
    """

    def __init__(self, workflow_id: str) -> None:
        self.workflow_id = workflow_id
        self._store: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []  # Append-only change log
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: Any, source_task_id: str = "") -> None:
        """Set a value in working memory."""
        async with self._lock:
            old_value = self._store.get(key)
            self._store[key] = value
            self._history.append({
                "op": "set",
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "source_task_id": source_task_id,
                "timestamp": datetime.utcnow().isoformat(),
            })
            logger.debug(f"Memory[{self.workflow_id}] SET {key}")

    async def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from working memory."""
        async with self._lock:
            return self._store.get(key, default)

    async def append(self, key: str, value: Any, source_task_id: str = "") -> None:
        """Append a value to a list stored at key. Creates the list if missing."""
        async with self._lock:
            existing = self._store.get(key, [])
            if not isinstance(existing, list):
                existing = [existing]
            existing.append(value)
            self._store[key] = existing
            self._history.append({
                "op": "append",
                "key": key,
                "appended_value": value,
                "source_task_id": source_task_id,
                "timestamp": datetime.utcnow().isoformat(),
            })

    async def delete(self, key: str) -> None:
        async with self._lock:
            if key in self._store:
                del self._store[key]

    async def all(self) -> dict[str, Any]:
        """Return a snapshot of the entire memory store."""
        async with self._lock:
            return dict(self._store)

    async def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot for checkpointing."""
        async with self._lock:
            return {
                "workflow_id": self.workflow_id,
                "store": dict(self._store),
                "history_length": len(self._history),
            }

    async def restore(self, snapshot: dict[str, Any]) -> None:
        """Restore memory from a checkpoint snapshot."""
        async with self._lock:
            self._store = dict(snapshot.get("store", {}))
            logger.info(f"Memory[{self.workflow_id}] restored {len(self._store)} keys")

    # ── Semantic helpers ────────────────────────────────────────────────────

    async def add_hypothesis(self, hypothesis: str, source_task_id: str = "") -> None:
        await self.append("hypotheses", hypothesis, source_task_id)

    async def get_hypotheses(self) -> list[str]:
        return await self.get("hypotheses", [])

    async def add_failed_attempt(self, attempt: dict[str, Any], source_task_id: str = "") -> None:
        await self.append("failed_attempts", attempt, source_task_id)

    async def get_failed_attempts(self) -> list[dict[str, Any]]:
        return await self.get("failed_attempts", [])

    async def add_open_question(self, question: str, source_task_id: str = "") -> None:
        await self.append("open_questions", question, source_task_id)

    async def get_open_questions(self) -> list[str]:
        return await self.get("open_questions", [])

    async def accumulate_knowledge(self, key: str, knowledge: Any, source_task_id: str = "") -> None:
        """Merge knowledge from completed tasks into an accumulator."""
        await self.append(f"knowledge:{key}", knowledge, source_task_id)

    async def get_accumulated_knowledge(self, key: str) -> list[Any]:
        return await self.get(f"knowledge:{key}", [])


class MemoryManager:
    """
    Manages WorkflowMemory instances per workflow.
    Thread-safe for concurrent workflow executions.
    """

    def __init__(self) -> None:
        self._memories: dict[str, WorkflowMemory] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(self, workflow_id: str) -> WorkflowMemory:
        async with self._lock:
            if workflow_id not in self._memories:
                self._memories[workflow_id] = WorkflowMemory(workflow_id)
            return self._memories[workflow_id]

    async def destroy(self, workflow_id: str) -> None:
        async with self._lock:
            self._memories.pop(workflow_id, None)

    async def list_active(self) -> list[str]:
        async with self._lock:
            return list(self._memories.keys())


# Global singleton memory manager
_memory_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
