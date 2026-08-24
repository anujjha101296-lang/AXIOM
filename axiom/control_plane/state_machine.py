"""
axiom.control_plane.state_machine
=================================
State Machine Engine.
Enforces canonical state transitions across missions, tasks, proofs, and experiments.
"""
from __future__ import annotations

from typing import Set, Tuple


class StateMachineEngine:
    """Enforces canonical state transition rules."""

    VALID_MISSION_TRANSITIONS: dict[str, Set[str]] = {
        "DRAFT": {"READY", "CANCELLED"},
        "INITIALIZED": {"PLANNING", "RUNNING", "CANCELLED"},
        "PLANNING": {"RUNNING", "PAUSED", "CANCELLED"},
        "RUNNING": {"PAUSED", "BLOCKED", "CHECKPOINTED", "COMPLETED", "FAILED", "CANCELLED", "BUDGET_EXCEEDED", "EMERGENCY_STOPPED"},
        "PAUSED": {"RUNNING", "CANCELLED", "EMERGENCY_STOPPED"},
        "BLOCKED": {"RUNNING", "CANCELLED", "FAILED"},
        "CHECKPOINTED": {"RUNNING", "PAUSED", "COMPLETED"},
        "COMPLETED": set(),
        "FAILED": set(),
        "CANCELLED": set(),
        "BUDGET_EXCEEDED": set(),
        "EMERGENCY_STOPPED": set(),
    }

    def validate_mission_transition(self, current_state: str, target_state: str) -> Tuple[bool, str]:
        """Validate whether a mission state transition is legal."""
        allowed = self.VALID_MISSION_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            return False, f"Illegal state transition from {current_state} to {target_state}"
        return True, "Valid transition"
