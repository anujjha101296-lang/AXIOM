"""
axiom.control_plane.models
==========================
Pydantic Domain Models for Phase 20 Production Control Plane.
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


class WorkerStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    DRAINING = "DRAINING"
    FAILED = "FAILED"


class AgentProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    name: str
    role: str
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_models: List[str] = Field(default_factory=list)
    max_steps: int = 20
    max_tokens: int = 100000
    timeout_sec: int = 300

    @classmethod
    def from_db(cls, db_obj: Any) -> AgentProfile:
        tools, models = [], []
        if hasattr(db_obj, "allowed_tools_json") and db_obj.allowed_tools_json:
            try:
                tools = json.loads(db_obj.allowed_tools_json)
            except Exception:
                pass
        if hasattr(db_obj, "allowed_models_json") and db_obj.allowed_models_json:
            try:
                models = json.loads(db_obj.allowed_models_json)
            except Exception:
                pass

        return cls(
            id=db_obj.id,
            name=db_obj.name,
            role=db_obj.role,
            allowed_tools=tools,
            allowed_models=models,
            max_steps=db_obj.max_steps,
            max_tokens=db_obj.max_tokens,
            timeout_sec=db_obj.timeout_sec,
        )


class DomainEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    mission_id: Optional[str] = None
    task_id: Optional[str] = None
    event_type: str
    actor: str = "system"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> DomainEvent:
        p = {}
        if hasattr(db_obj, "payload_json") and db_obj.payload_json:
            try:
                p = json.loads(db_obj.payload_json)
            except Exception:
                pass

        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            mission_id=db_obj.mission_id,
            task_id=db_obj.task_id,
            event_type=db_obj.event_type,
            actor=db_obj.actor,
            payload=p,
            timestamp=db_obj.timestamp,
        )


class WorkerNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    hostname: str
    status: WorkerStatus = WorkerStatus.AVAILABLE
    current_task_id: Optional[str] = None
    last_heartbeat: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> WorkerNode:
        return cls(
            id=db_obj.id,
            hostname=db_obj.hostname,
            status=WorkerStatus(db_obj.status),
            current_task_id=db_obj.current_task_id,
            last_heartbeat=db_obj.last_heartbeat,
        )
