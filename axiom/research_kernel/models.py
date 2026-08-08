"""AXIOM Research Kernel — domain models for the 10-stage research pipeline."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())[:12]


class KernelStage(str, Enum):
    """Ten permanent kernel stages — every research workflow executes all ten."""

    GOAL_DECOMPOSITION = "goal_decomposition"
    RESEARCH_PLANNING = "research_planning"
    EVIDENCE_ACQUISITION = "evidence_acquisition"
    MULTI_AGENT_ORCHESTRATION = "multi_agent_orchestration"
    VERIFICATION_PIPELINE = "verification_pipeline"
    MEMORY_INTEGRATION = "memory_integration"
    REFLECTION = "reflection"
    LEARNING = "learning"
    BENCHMARK_EXECUTION = "benchmark_execution"
    REPORT_GENERATION = "report_generation"


STAGE_ORDER: list[KernelStage] = list(KernelStage)


class KernelRunStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class StageOutput(BaseModel):
    stage: KernelStage
    subsystem: str
    completed: bool
    artifacts: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    duration_ms: float = 0.0


class PluginDescriptor(BaseModel):
    plugin_id: str
    domain: str
    name: str
    version: str
    description: str = ""
    benchmark_count: int = 0


class KernelRun(BaseModel):
    run_id: str = Field(default_factory=_new_id)
    objective: str
    domain: str
    plugin_id: str
    status: KernelRunStatus = KernelRunStatus.PENDING
    current_stage: KernelStage = KernelStage.GOAL_DECOMPOSITION
    stages_completed: list[KernelStage] = Field(default_factory=list)
    stage_outputs: list[StageOutput] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    aca_cycle_id: str | None = None
    sme_session_id: str | None = None
    workflow_id: str | None = None
    report: str | None = None
    benchmark_results: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def is_complete(self) -> bool:
        return len(self.stages_completed) == len(STAGE_ORDER)
