"""AXIOM Cognitive Architecture — domain models."""

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


class CognitiveLayer(str, Enum):
    """Nine permanent cognitive layers — model-agnostic."""

    PERCEPTION = "perception"
    UNDERSTANDING = "understanding"
    MEMORY = "memory"
    REASONING = "reasoning"
    PLANNING = "planning"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    LEARNING = "learning"
    REFLECTION = "reflection"


LAYER_ORDER: list[CognitiveLayer] = list(CognitiveLayer)


class CognitivePillar(str, Enum):
    """Core separation of concerns (permanent, not model-dependent)."""

    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    MEMORY = "memory"
    PLANNING = "planning"
    VERIFICATION = "verification"
    EXECUTION = "execution"
    LEARNING = "learning"
    REFLECTION = "reflection"


PILLAR_TO_LAYERS: dict[CognitivePillar, list[CognitiveLayer]] = {
    CognitivePillar.KNOWLEDGE: [CognitiveLayer.PERCEPTION, CognitiveLayer.UNDERSTANDING],
    CognitivePillar.MEMORY: [CognitiveLayer.MEMORY],
    CognitivePillar.REASONING: [CognitiveLayer.REASONING],
    CognitivePillar.PLANNING: [CognitiveLayer.PLANNING],
    CognitivePillar.EXECUTION: [CognitiveLayer.EXECUTION],
    CognitivePillar.VERIFICATION: [CognitiveLayer.VERIFICATION],
    CognitivePillar.LEARNING: [CognitiveLayer.LEARNING],
    CognitivePillar.REFLECTION: [CognitiveLayer.REFLECTION],
}


class CognitiveCycleStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class LayerOutput(BaseModel):
    layer: CognitiveLayer
    pillar: CognitivePillar
    subsystem: str
    completed: bool
    artifacts: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class CognitiveCycle(BaseModel):
    cycle_id: str = Field(default_factory=_new_id)
    objective: str
    domain: str = "research"
    model_provider: str = "default"
    status: CognitiveCycleStatus = CognitiveCycleStatus.PENDING
    current_layer: CognitiveLayer = CognitiveLayer.PERCEPTION
    layers_completed: list[CognitiveLayer] = Field(default_factory=list)
    layer_outputs: list[LayerOutput] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    sme_session_id: str | None = None
    workflow_id: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def is_complete(self) -> bool:
        return len(self.layers_completed) == len(LAYER_ORDER)
