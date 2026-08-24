"""
axiom.mission_control.checkpoint
================================
Checkpoint Manager.
Creates immutable research state snapshots for crash recovery and audit trails.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from axiom.mission_control.models import MissionCheckpoint, ResearchMission


class CheckpointManager:
    """Manages immutable research mission checkpoints."""

    def create_checkpoint(self, mission: ResearchMission, summary: str = "") -> MissionCheckpoint:
        """Generate immutable mission checkpoint."""
        snap = {
            "mission_id": mission.id,
            "iteration": mission.current_iteration,
            "state": mission.state.value,
            "budget": mission.budget.model_dump(),
        }
        raw_bytes = json.dumps(snap, sort_keys=True).encode("utf-8")
        chk_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]

        return MissionCheckpoint(
            mission_id=mission.id,
            iteration=mission.current_iteration,
            checkpoint_hash=chk_hash,
            summary=summary or f"Iteration {mission.current_iteration} checkpoint snapshot.",
            state_snapshot=snap,
        )
