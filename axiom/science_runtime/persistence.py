"""Persistence boundary for bounded scientific research runs."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .research_loop import ResearchRun


class ResearchRunStore:
    """Append-only, local-first persistence adapter for research runs."""

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
            "stage": run.stage.value,
            "payload": payload or {},
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")
        return path

    def snapshot(self, run: ResearchRun) -> Path:
        path = self.root / f"{run.run_id}.snapshot.json"
        path.write_text(json.dumps(asdict(run), sort_keys=True, default=str, indent=2), encoding="utf-8")
        return path
