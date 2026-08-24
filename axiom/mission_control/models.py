"""
axiom.mission_control.models
============================
Pydantic Domain Models for Phase 19 Autonomous Research Mission Control.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def generate_uuid() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MissionState(str, Enum):
    INITIALIZED = "INITIALIZED"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CHECKPOINTED = "CHECKPOINTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"


class MissionBudget(BaseModel):
    max_iterations: int = 20
    max_time_sec: int = 600
    max_tool_calls: int = 50
    max_experiments: int = 10
    max_proof_attempts: int = 10

    used_iterations: int = 0
    used_time_sec: int = 0
    used_tool_calls: int = 0
    used_experiments: int = 0
    used_proof_attempts: int = 0

    def is_exhausted(self) -> bool:
        return (
            self.used_iterations >= self.max_iterations
            or self.used_time_sec >= self.max_time_sec
            or self.used_tool_calls >= self.max_tool_calls
            or self.used_experiments >= self.max_experiments
            or self.used_proof_attempts >= self.max_proof_attempts
        )


class MissionTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    mission_id: str
    name: str
    assigned_role: str = "Mathematician"
    state: str = "PLANNED"
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> MissionTask:
        return cls(
            id=db_obj.id,
            mission_id=db_obj.mission_id,
            name=db_obj.name,
            assigned_role=db_obj.assigned_role,
            state=db_obj.state,
            created_at=db_obj.created_at,
        )


class MissionCheckpoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    mission_id: str
    iteration: int
    checkpoint_hash: str
    summary: str
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> MissionCheckpoint:
        snap = {}
        if hasattr(db_obj, "state_snapshot_json") and db_obj.state_snapshot_json:
            try:
                snap = json.loads(db_obj.state_snapshot_json)
            except Exception:
                snap = {}

        return cls(
            id=db_obj.id,
            mission_id=db_obj.mission_id,
            iteration=db_obj.iteration,
            checkpoint_hash=db_obj.checkpoint_hash,
            summary=db_obj.summary,
            state_snapshot=snap,
            created_at=db_obj.created_at,
        )


class ResearchMission(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    name: str
    objective: str
    state: MissionState = MissionState.INITIALIZED
    budget: MissionBudget = Field(default_factory=MissionBudget)
    current_iteration: int = 0
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    tasks: List[MissionTask] = Field(default_factory=list)
    checkpoints: List[MissionCheckpoint] = Field(default_factory=list)

    @classmethod
    def from_db(cls, db_obj: Any) -> ResearchMission:
        budget_obj = MissionBudget()
        if hasattr(db_obj, "budget_json") and db_obj.budget_json:
            try:
                b_dict = json.loads(db_obj.budget_json)
                budget_obj = MissionBudget(**b_dict)
            except Exception:
                pass

        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            name=db_obj.name,
            objective=db_obj.objective,
            state=MissionState(db_obj.state),
            budget=budget_obj,
            current_iteration=db_obj.current_iteration,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )
