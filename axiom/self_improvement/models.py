"""Data models for Phase 15 Self-Improvement Engine."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RegressionStatus(str, Enum):
    IMPROVED = "IMPROVED"
    UNCHANGED = "UNCHANGED"
    REGRESSED = "REGRESSED"
    FAILED = "FAILED"


class PhaseBenchmarkResult(BaseModel):
    phase_number: int
    phase_name: str
    benchmarks_total: int
    benchmarks_passed: int
    pass_rate: float
    execution_time_ms: float


class CapabilityDelta(BaseModel):
    delta_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    commit_hash: str
    phase_evaluations: List[PhaseBenchmarkResult]
    overall_pass_rate: float
    status: RegressionStatus
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SelfImprovementReport(BaseModel):
    cycle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    baseline_pass_rate: float
    current_pass_rate: float
    regression_status: RegressionStatus
    phase_summaries: List[PhaseBenchmarkResult]
    recommendations: List[str]
