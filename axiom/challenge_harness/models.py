"""
axiom.challenge_harness.models
==============================
Pydantic Domain Models for Phase 18 Mathematical Research Challenge Harness.
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


class ChallengeLevel(str, Enum):
    LEVEL_0_BASIC = "LEVEL_0_BASIC"
    LEVEL_1_ELEMENTARY_PROOFS = "LEVEL_1_ELEMENTARY_PROOFS"
    LEVEL_2_INTERMEDIATE = "LEVEL_2_INTERMEDIATE"
    LEVEL_3_ADVANCED = "LEVEL_3_ADVANCED"
    LEVEL_4_OPEN_STYLE = "LEVEL_4_OPEN_STYLE"
    LEVEL_5_FRONTIER = "LEVEL_5_FRONTIER"


class EvaluationOutcome(str, Enum):
    SOLVED = "SOLVED"
    PARTIALLY_SOLVED = "PARTIALLY_SOLVED"
    KNOWN_RESULT_REDISCOVERED = "KNOWN_RESULT_REDISCOVERED"
    RESEARCH_PROGRESS = "RESEARCH_PROGRESS"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAILED = "FAILED"


class FailureClass(str, Enum):
    NONE = "NONE"
    MISUNDERSTOOD_PROBLEM = "MISUNDERSTOOD_PROBLEM"
    BAD_DECOMPOSITION = "BAD_DECOMPOSITION"
    POOR_SOURCE_SELECTION = "POOR_SOURCE_SELECTION"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    LOGICAL_ERROR = "LOGICAL_ERROR"
    MISSED_COUNTEREXAMPLE = "MISSED_COUNTEREXAMPLE"
    BAD_EXPERIMENT = "BAD_EXPERIMENT"
    FORMALIZATION_ERROR = "FORMALIZATION_ERROR"
    PROOF_FAILURE = "PROOF_FAILURE"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    MEMORY_FAILURE = "MEMORY_FAILURE"
    TOOL_FAILURE = "TOOL_FAILURE"


class EvaluationScore(BaseModel):
    overall_score: float = 0.0
    problem_understanding: float = 0.0
    decomposition: float = 0.0
    literature_retrieval: float = 0.0
    evidence_quality: float = 0.0
    citation_validity: float = 0.0
    hypothesis_quality: float = 0.0
    counterexample_search: float = 0.0
    experiment_quality: float = 0.0
    formalization: float = 0.0
    proof_correctness: float = 0.0
    research_memory: float = 0.0
    failure_recovery: float = 0.0
    resource_efficiency: float = 0.0


class Challenge(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    version: str = "AXIOM-MATH-001"
    title: str
    domain: str
    difficulty_level: ChallengeLevel = ChallengeLevel.LEVEL_0_BASIC
    statement: str
    allowed_resources: List[str] = Field(default_factory=list)
    time_budget_sec: int = 300
    tool_budget_steps: int = 20
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> Challenge:
        resources = []
        if hasattr(db_obj, "allowed_resources_json") and db_obj.allowed_resources_json:
            try:
                resources = json.loads(db_obj.allowed_resources_json)
            except Exception:
                resources = []
        return cls(
            id=db_obj.id,
            version=db_obj.version,
            title=db_obj.title,
            domain=db_obj.domain,
            difficulty_level=ChallengeLevel(db_obj.difficulty_level),
            statement=db_obj.statement,
            allowed_resources=resources,
            time_budget_sec=db_obj.time_budget_sec,
            tool_budget_steps=db_obj.tool_budget_steps,
            created_at=db_obj.created_at,
        )


class EvaluationRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    challenge_id: str
    outcome: EvaluationOutcome = EvaluationOutcome.RESEARCH_PROGRESS
    score: EvaluationScore = Field(default_factory=EvaluationScore)
    failure_class: FailureClass = FailureClass.NONE
    runtime_sec: float = 0.0
    steps_used: int = 0
    proof_verified: bool = False
    counterexample_found: bool = False
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> EvaluationRun:
        score_obj = EvaluationScore()
        if hasattr(db_obj, "score_json") and db_obj.score_json:
            try:
                score_dict = json.loads(db_obj.score_json)
                score_obj = EvaluationScore(**score_dict)
            except Exception:
                pass

        return cls(
            id=db_obj.id,
            challenge_id=db_obj.challenge_id,
            outcome=EvaluationOutcome(db_obj.outcome),
            score=score_obj,
            failure_class=FailureClass(db_obj.failure_class),
            runtime_sec=db_obj.runtime_sec,
            steps_used=db_obj.steps_used,
            proof_verified=db_obj.proof_verified,
            counterexample_found=db_obj.counterexample_found,
            created_at=db_obj.created_at,
        )
