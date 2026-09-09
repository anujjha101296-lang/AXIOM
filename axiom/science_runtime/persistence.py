"""Persistence boundary for bounded scientific research runs.

The runtime owns the scientific state machine; this module owns durable event
serialization.  It intentionally uses the existing SQLAlchemy session factory
so SQLite remains a zero-cost development backend and PostgreSQL can be used
without changing the research protocol.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import ResearchRun


class ResearchRunStore:
    """Durable JSONL store for replayable research runs.

    JSONL is deliberately the first persistence adapter: append-only events are
    easy to inspect, diff, archive, and migrate into PostgreSQL later.
    """

    def __init__(self, root: str | Path = "data/research_runs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def append(self, run: ResearchRun, event_type: str, payload: dict[str, Any] | None = None) -> Path:
        path = self.root / f"{run.run_id}.jsonl"
        event = {
            "schema_version": "axiom.research.event.v1",
            "event_id": f"{run.run_id}:{len(run.transitions)}:{event_type}",
            "run_id": run.run_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": getattr(run.state, "value", run.state),
            "payload": payload or {},
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")
        return path

    def snapshot(self, run: ResearchRun) -> Path:
        path = self.root / f"{run.run_id}.snapshot.json"
        path.write_text(json.dumps(asdict(run), sort_keys=True, default=str, indent=2), encoding="utf-8")
        return path
