"""Persistence boundary for bounded scientific research runs."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .research_loop import ResearchRun, Transition


class ResearchRunStore:
    """Append-only, local-first persistence adapter for research runs."""

    def __init__(self, root: str | Path = "data/research_runs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        run: ResearchRun,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> Path:
        path = self.root / f"{run.run_id}.jsonl"
        sequence = self._next_sequence(path)
        event = {
            "schema_version": "axiom.research.event.v1",
            "event_id": f"{run.run_id}:{sequence}",
            "sequence": sequence,
            "run_id": run.run_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": run.stage.value,
            "payload": payload or {},
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")
        return path

    def record_transition(self, run: ResearchRun, transition: Transition) -> Path:
        """Persist one lifecycle transition immediately after it occurs."""
        return self.append(
            run,
            transition.action.upper(),
            {"detail": transition.detail, "transition_stage": transition.stage},
        )

    @staticmethod
    def _next_sequence(path: Path) -> int:
        if not path.exists():
            return 1
        sequence = 0
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    try:
                        sequence = max(sequence, int(json.loads(line).get("sequence", 0)))
                    except (ValueError, TypeError, json.JSONDecodeError):
                        continue
        return sequence + 1

    def read_events(self, run_id: str, after_sequence: int = 0) -> list[dict[str, Any]]:
        path = self.root / f"{run_id}.jsonl"
        if not path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if int(event.get("sequence", 0)) > after_sequence:
                events.append(event)
        return events

    def snapshot(self, run: ResearchRun) -> Path:
        path = self.root / f"{run.run_id}.snapshot.json"
        path.write_text(json.dumps(asdict(run), sort_keys=True, default=str, indent=2), encoding="utf-8")
        return path
