from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .research_loop import ResearchStage, Transition


@dataclass(frozen=True)
class ResearchReplay:
    run_id: str
    last_sequence: int
    stage: str
    transitions: tuple[Transition, ...]

    @property
    def terminal(self) -> bool:
        return self.stage in {ResearchStage.COMPLETED.value, ResearchStage.FAILED.value}

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "last_sequence": self.last_sequence,
            "stage": self.stage,
            "terminal": self.terminal,
            "transitions": [
                {"stage": item.stage, "action": item.action, "detail": item.detail}
                for item in self.transitions
            ],
        }


def replay_research_events(events: list[dict[str, Any]]) -> ResearchReplay:
    if not events:
        raise ValueError("Cannot replay an empty research event stream")
    expected = 1
    run_id = None
    transitions = []
    stage = ResearchStage.PLANNED.value
    valid_stages = {item.value for item in ResearchStage}
    for event in events:
        sequence = int(event.get("sequence", 0))
        if sequence != expected:
            raise ValueError(f"Research event sequence gap: expected {expected}, got {sequence}")
        event_run_id = str(event.get("run_id", ""))
        if not event_run_id:
            raise ValueError("Research event is missing run_id")
        if run_id is None:
            run_id = event_run_id
        elif event_run_id != run_id:
            raise ValueError("Research event stream contains multiple run_ids")
        event_stage = str(event.get("stage", ""))
        if event_stage not in valid_stages:
            raise ValueError(f"Unknown research stage: {event_stage}")
        payload = event.get("payload") or {}
        transitions.append(Transition(
            stage=str(payload.get("transition_stage", event_stage)),
            action=str(event.get("event_type", "")).lower(),
            detail=str(payload.get("detail", "")),
        ))
        if not transitions[-1].action:
            raise ValueError("Research event is missing event_type")
        stage = event_stage
        expected += 1
    assert run_id is not None
    return ResearchReplay(run_id, expected - 1, stage, tuple(transitions))


def verify_snapshot_against_replay(snapshot: dict[str, Any], replay: ResearchReplay) -> None:
    if str(snapshot.get("run_id", "")) != replay.run_id:
        raise ValueError("Snapshot run_id does not match replay")
    if str(snapshot.get("stage", "")) != replay.stage:
        raise ValueError(
            f"Snapshot stage {snapshot.get('stage')!r} disagrees with replay stage {replay.stage!r}"
        )


__all__ = ["ResearchReplay", "replay_research_events", "verify_snapshot_against_replay"]
