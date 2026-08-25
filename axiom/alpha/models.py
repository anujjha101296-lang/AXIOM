"""
axiom.alpha.models
==================
Alpha Access Control, Usage Limits, Session Telemetry, and User Feedback models.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AlphaAccessStatus(str, Enum):
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class AlphaUsageLimits(BaseModel):
    max_missions_per_day: int = 10
    max_llm_calls_per_day: int = 100
    max_file_size_mb: int = 10
    max_uploaded_files: int = 20
    max_experiments_per_day: int = 15
    max_mission_runtime_sec: int = 600
    max_concurrent_tasks: int = 3


class AlphaUserRecord(BaseModel):
    user_id: str
    email: str
    status: AlphaAccessStatus = AlphaAccessStatus.INVITED
    invited_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    activated_at: Optional[str] = None
    limits: AlphaUsageLimits = Field(default_factory=AlphaUsageLimits)


class FeedbackRating(str, Enum):
    YES = "YES"
    NO = "NO"


class AlphaFeedbackSubmit(BaseModel):
    session_id: str
    useful: FeedbackRating
    rating_1_to_5: int = Field(ge=1, le=5)
    what_went_wrong: Optional[str] = ""
    whats_missing: Optional[str] = ""
    would_use_again: bool = True
    would_pay: bool = False


class AlphaTelemetryEvent(BaseModel):
    event_id: str
    session_id: str
    user_id: str
    project_id: str
    status: str
    duration_sec: float
    tools_used: list[str] = []
    models_used: list[str] = []
    failure_reason: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
