"""
AXIOM Workflow Engine — Worker Registry
========================================
Pluggable registry of workers. Workers are discovered by worker_type string.
No hardcoding — new workers are registered at import time.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .workers.base import BaseWorker

logger = logging.getLogger(__name__)


class WorkerRegistry:
    """
    Registry that maps worker_type strings to BaseWorker instances.

    Register a worker:
        registry = WorkerRegistry()
        registry.register(MyWorker())

    Resolve a worker:
        worker = registry.get("planner")
    """

    def __init__(self) -> None:
        self._workers: dict[str, "BaseWorker"] = {}

    def register(self, worker: "BaseWorker") -> None:
        wtype = worker.worker_type
        if wtype in self._workers:
            logger.warning(f"WorkerRegistry: overwriting existing worker '{wtype}'")
        self._workers[wtype] = worker
        logger.info(f"WorkerRegistry: registered '{wtype}' — {worker.mission}")

    def get(self, worker_type: str) -> "BaseWorker":
        worker = self._workers.get(worker_type)
        if worker is None:
            available = list(self._workers.keys())
            raise KeyError(
                f"No worker registered for type '{worker_type}'. "
                f"Available: {available}"
            )
        return worker

    def list_all(self) -> list[dict]:
        return [
            {
                "worker_type": w.worker_type,
                "mission": w.mission,
                "capabilities": w.capabilities,
                "version": getattr(w, "version", "1.0.0"),
            }
            for w in self._workers.values()
        ]

    def has(self, worker_type: str) -> bool:
        return worker_type in self._workers

    def __len__(self) -> int:
        return len(self._workers)


def build_default_registry() -> WorkerRegistry:
    """Build and return a registry pre-loaded with all built-in workers."""
    from .workers.planner import PlannerWorker
    from .workers.researcher import ResearchWorker
    from .workers.reviewer import ReviewerWorker
    from .workers.merger import MergerWorker
    from .workers.reporter import ReporterWorker

    registry = WorkerRegistry()
    registry.register(PlannerWorker())
    registry.register(ResearchWorker())
    registry.register(ReviewerWorker())
    registry.register(MergerWorker())
    registry.register(ReporterWorker())
    return registry


# Global singleton
_default_registry: WorkerRegistry | None = None


def get_registry() -> WorkerRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = build_default_registry()
    return _default_registry
