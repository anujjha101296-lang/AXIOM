"""
axiom.control_plane.worker
==========================
Worker Engine.
Manages background worker nodes, idempotency keys, and long-horizon task execution.
"""
from __future__ import annotations

import socket
from typing import Dict, Optional, Tuple

from axiom.control_plane.models import WorkerNode, WorkerStatus


class WorkerEngine:
    """Manages background research worker nodes."""

    def __init__(self):
        self._workers: Dict[str, WorkerNode] = {}

    def register_worker(self, worker_id: Optional[str] = None) -> WorkerNode:
        """Register worker node in available pool."""
        hostname = socket.gethostname()
        node = WorkerNode(id=worker_id or f"worker-{hostname}", hostname=hostname, status=WorkerStatus.AVAILABLE)
        self._workers[node.id] = node
        return node

    def assign_task(self, worker_id: str, task_id: str) -> Tuple[bool, str]:
        """Assign task to worker node."""
        worker = self._workers.get(worker_id)
        if not worker:
            return False, f"Worker {worker_id} not registered"
        if worker.status != WorkerStatus.AVAILABLE:
            return False, f"Worker {worker_id} is in status {worker.status.value}"

        worker.status = WorkerStatus.BUSY
        worker.current_task_id = task_id
        return True, "Task assigned"

    def complete_task(self, worker_id: str) -> Tuple[bool, str]:
        """Mark task complete and return worker to available pool."""
        worker = self._workers.get(worker_id)
        if not worker:
            return False, f"Worker {worker_id} not registered"

        worker.status = WorkerStatus.AVAILABLE
        worker.current_task_id = None
        return True, "Task completed"
