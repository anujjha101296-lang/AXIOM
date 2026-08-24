"""
axiom.long_horizon.models
=========================
Pydantic Domain Models for Phase 17 Long-Horizon Mathematical Research Engine.
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


class TaskState(str, Enum):
    PLANNED = "PLANNED"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    FALSIFIED = "FALSIFIED"
    DEFERRED = "DEFERRED"
    ABANDONED = "ABANDONED"
    REVISITABLE = "REVISITABLE"


class ApproachStatus(str, Enum):
    PROMISING = "PROMISING"
    FAILED = "FAILED"
    FALSIFIED = "FALSIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    COMPLETED = "COMPLETED"


class CriticRecommendation(str, Enum):
    CONTINUE = "CONTINUE"
    PIVOT = "PIVOT"
    REVISE = "REVISE"
    ABANDON = "ABANDON"
    INVESTIGATE = "INVESTIGATE"


class ResearchAttempt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    task_id: str
    approach_description: str
    method: str = "Direct Proof"
    result_summary: str = ""
    status: ApproachStatus = ApproachStatus.PROMISING
    failure_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ResearchAttempt:
        return cls(
            id=db_obj.id,
            task_id=db_obj.task_id,
            approach_description=db_obj.approach_description,
            method=db_obj.method,
            result_summary=db_obj.result_summary,
            status=ApproachStatus(db_obj.status),
            failure_reason=db_obj.failure_reason,
            created_at=db_obj.created_at,
        )


class ApproachMemory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    problem_id: str
    approach_hash: str
    summary: str
    status: ApproachStatus
    failure_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ApproachMemory:
        return cls(
            id=db_obj.id,
            problem_id=db_obj.problem_id,
            approach_hash=db_obj.approach_hash,
            summary=db_obj.summary,
            status=ApproachStatus(db_obj.status),
            failure_reason=db_obj.failure_reason,
            created_at=db_obj.created_at,
        )


class ResearchTask(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    subproblem_id: str
    name: str
    strategy: str = "Decomposition"
    state: TaskState = TaskState.PLANNED
    budget_steps: int = 10
    current_step: int = 0
    created_at: datetime = Field(default_factory=utcnow)

    attempts: List[ResearchAttempt] = Field(default_factory=list)

    @classmethod
    def from_db(cls, db_obj: Any) -> ResearchTask:
        return cls(
            id=db_obj.id,
            subproblem_id=db_obj.subproblem_id,
            name=db_obj.name,
            strategy=db_obj.strategy,
            state=TaskState(db_obj.state),
            budget_steps=db_obj.budget_steps,
            current_step=db_obj.current_step,
            created_at=db_obj.created_at,
        )


class ResearchSubproblem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    problem_id: str
    title: str
    statement: str
    dependencies: List[str] = Field(default_factory=list)
    status: TaskState = TaskState.PLANNED
    created_at: datetime = Field(default_factory=utcnow)

    tasks: List[ResearchTask] = Field(default_factory=list)

    @classmethod
    def from_db(cls, db_obj: Any) -> ResearchSubproblem:
        deps = []
        if hasattr(db_obj, "dependencies_json") and db_obj.dependencies_json:
            try:
                deps = json.loads(db_obj.dependencies_json)
            except Exception:
                deps = []
        return cls(
            id=db_obj.id,
            problem_id=db_obj.problem_id,
            title=db_obj.title,
            statement=db_obj.statement,
            dependencies=deps,
            status=TaskState(db_obj.status),
            created_at=db_obj.created_at,
        )


class ResearchMilestone(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    problem_id: str
    title: str
    evidence_summary: str
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ResearchMilestone:
        return cls(
            id=db_obj.id,
            problem_id=db_obj.problem_id,
            title=db_obj.title,
            evidence_summary=db_obj.evidence_summary,
            created_at=db_obj.created_at,
        )


class ResearchProblem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    title: str
    description: str
    formal_statement: str = ""
    status: TaskState = TaskState.PLANNED
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    subproblems: List[ResearchSubproblem] = Field(default_factory=list)
    milestones: List[ResearchMilestone] = Field(default_factory=list)
    memories: List[ApproachMemory] = Field(default_factory=list)

    @classmethod
    def from_db(cls, db_obj: Any) -> ResearchProblem:
        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            title=db_obj.title,
            description=db_obj.description,
            formal_statement=db_obj.formal_statement,
            status=TaskState(db_obj.status),
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )
