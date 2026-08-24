"""
axiom.mission_control.controller
================================
Mission Controller Module.
Coordinates research mission execution, budget enforcement, pause/resume, and emergency stop.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

from axiom.mission_control.checkpoint import CheckpointManager
from axiom.mission_control.models import MissionCheckpoint, MissionState, ResearchMission
from axiom.mission_control.scheduler import MissionTaskScheduler


class MissionController:
    """Controls research mission execution and budget limits."""

    def __init__(self):
        self.scheduler = MissionTaskScheduler()
        self.checkpoint_manager = CheckpointManager()

    def start_mission(self, mission: ResearchMission) -> Tuple[ResearchMission, MissionCheckpoint]:
        """Start or resume a research mission."""
        if mission.state in (MissionState.EMERGENCY_STOPPED, MissionState.CANCELLED):
            raise ValueError(f"Cannot start mission in state {mission.state.value}")

        mission.state = MissionState.RUNNING
        chk = self.checkpoint_manager.create_checkpoint(mission, "Mission execution started.")
        mission.checkpoints.append(chk)
        return mission, chk

    def pause_mission(self, mission: ResearchMission) -> Tuple[ResearchMission, MissionCheckpoint]:
        """Pause a running mission."""
        mission.state = MissionState.PAUSED
        chk = self.checkpoint_manager.create_checkpoint(mission, "Mission paused by user.")
        mission.checkpoints.append(chk)
        return mission, chk

    def emergency_stop(self, mission: ResearchMission) -> Tuple[ResearchMission, MissionCheckpoint]:
        """Trigger immediate emergency stop."""
        mission.state = MissionState.EMERGENCY_STOPPED
        chk = self.checkpoint_manager.create_checkpoint(mission, "EMERGENCY STOP TRIGGERED.")
        mission.checkpoints.append(chk)
        return mission, chk

    def step_mission(self, mission: ResearchMission) -> Tuple[bool, str, Optional[MissionCheckpoint]]:
        """
        Execute one bounded research iteration step.
        Returns (continued, status_message, optional_checkpoint).
        """
        if mission.state != MissionState.RUNNING:
            return False, f"Mission is in state {mission.state.value}", None

        # Check budget
        if mission.budget.is_exhausted():
            mission.state = MissionState.BUDGET_EXCEEDED
            chk = self.checkpoint_manager.create_checkpoint(mission, "Budget exhausted.")
            return False, "Budget limit reached", chk

        # Increment iteration
        mission.current_iteration += 1
        mission.budget.used_iterations += 1
        mission.budget.used_tool_calls += 2

        chk = self.checkpoint_manager.create_checkpoint(mission, f"Completed iteration {mission.current_iteration}.")
        mission.checkpoints.append(chk)

        if mission.current_iteration >= mission.budget.max_iterations:
            mission.state = MissionState.COMPLETED
            return False, "Mission completed maximum iterations", chk

        return True, f"Executed iteration {mission.current_iteration}", chk
