"""
axiom.experiment.models
======================
Pydantic Domain Models for Phase 15 Computational Experiment & Verification Engine.
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


class ExperimentStatus(str, Enum):
    PLANNED = "PLANNED"
    VALIDATED = "VALIDATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    TIMEOUT = "TIMEOUT"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    FAILED = "FAILED"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    FAILED_VERIFICATION = "FAILED_VERIFICATION"
    UNVERIFIED = "UNVERIFIED"


class ReproducibilityStatus(str, Enum):
    REPRODUCIBLE = "REPRODUCIBLE"
    NONDETERMINISTIC = "NONDETERMINISTIC"
    FAILED_REPRODUCTION = "FAILED_REPRODUCTION"


class InterpretationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    EXPERIMENT_FAILED = "EXPERIMENT_FAILED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class ObservationLevel(str, Enum):
    COMPUTATIONAL_OBSERVATION = "COMPUTATIONAL_OBSERVATION"
    EMPIRICAL_SUPPORT = "EMPIRICAL_SUPPORT"
    FORMAL_VERIFICATION = "FORMAL_VERIFICATION"
    MATHEMATICAL_PROOF = "MATHEMATICAL_PROOF"


class ExperimentRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    experiment_id: str
    run_number: int = 1
    status: ExperimentStatus = ExperimentStatus.PLANNED
    runtime_ms: float = 0.0
    memory_bytes: int = 0
    stdout: str = ""
    stderr: str = ""
    result_data: Dict[str, Any] = Field(default_factory=dict)
    input_hash: str = ""
    spec_hash: str = ""
    seed: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ExperimentRun:
        res = {}
        if hasattr(db_obj, "result_data_json") and db_obj.result_data_json:
            try:
                res = json.loads(db_obj.result_data_json)
            except Exception:
                res = {}
        return cls(
            id=db_obj.id,
            experiment_id=db_obj.experiment_id,
            run_number=db_obj.run_number,
            status=ExperimentStatus(db_obj.status),
            runtime_ms=db_obj.runtime_ms,
            memory_bytes=db_obj.memory_bytes,
            stdout=db_obj.stdout,
            stderr=db_obj.stderr,
            result_data=res,
            input_hash=db_obj.input_hash,
            spec_hash=db_obj.spec_hash,
            seed=db_obj.seed,
            error_message=db_obj.error_message,
            created_at=db_obj.created_at,
        )


class ExperimentObservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    experiment_id: str
    run_id: str
    observation_level: ObservationLevel = ObservationLevel.COMPUTATIONAL_OBSERVATION
    summary: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    reproducibility_status: ReproducibilityStatus = ReproducibilityStatus.REPRODUCIBLE
    interpretation_status: InterpretationStatus = InterpretationStatus.SUPPORTED
    is_mathematical_proof: bool = False
    limitations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ExperimentObservation:
        metrics = {}
        limits = []
        if hasattr(db_obj, "metrics_json") and db_obj.metrics_json:
            try:
                metrics = json.loads(db_obj.metrics_json)
            except Exception:
                metrics = {}
        if hasattr(db_obj, "limitations_json") and db_obj.limitations_json:
            try:
                limits = json.loads(db_obj.limitations_json)
            except Exception:
                limits = []
        return cls(
            id=db_obj.id,
            experiment_id=db_obj.experiment_id,
            run_id=db_obj.run_id,
            observation_level=ObservationLevel(db_obj.observation_level),
            summary=db_obj.summary,
            metrics=metrics,
            reproducibility_status=ReproducibilityStatus(db_obj.reproducibility_status),
            interpretation_status=InterpretationStatus(db_obj.interpretation_status),
            is_mathematical_proof=db_obj.is_mathematical_proof,
            limitations=limits,
            created_at=db_obj.created_at,
        )


class ExperimentVerification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    experiment_id: str
    run_id: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    independent_method: str
    independent_result: str
    discrepancy: float = 0.0
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ExperimentVerification:
        return cls(
            id=db_obj.id,
            experiment_id=db_obj.experiment_id,
            run_id=db_obj.run_id,
            verification_status=VerificationStatus(db_obj.verification_status),
            independent_method=db_obj.independent_method,
            independent_result=db_obj.independent_result,
            discrepancy=db_obj.discrepancy,
            created_at=db_obj.created_at,
        )


class Experiment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    hypothesis_id: Optional[str] = None
    prediction_id: Optional[str] = None
    plan_id: Optional[str] = None
    name: str
    objective: str
    code_body: str
    method: str = "numerical_simulation"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    resource_limits: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timeout_seconds": 5,
            "max_memory_mb": 128,
            "max_output_bytes": 51200,
        }
    )
    status: ExperimentStatus = ExperimentStatus.PLANNED
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    runs: List[ExperimentRun] = Field(default_factory=list)
    latest_observation: Optional[ExperimentObservation] = None
    latest_verification: Optional[ExperimentVerification] = None

    @classmethod
    def from_db(cls, db_obj: Any) -> Experiment:
        params = {}
        limits = {}
        if hasattr(db_obj, "parameters_json") and db_obj.parameters_json:
            try:
                params = json.loads(db_obj.parameters_json)
            except Exception:
                params = {}
        if hasattr(db_obj, "resource_limits_json") and db_obj.resource_limits_json:
            try:
                limits = json.loads(db_obj.resource_limits_json)
            except Exception:
                limits = {}
        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            hypothesis_id=db_obj.hypothesis_id,
            prediction_id=db_obj.prediction_id,
            plan_id=db_obj.plan_id,
            name=db_obj.name,
            objective=db_obj.objective,
            code_body=db_obj.code_body,
            method=db_obj.method,
            parameters=params,
            resource_limits=limits or {"timeout_seconds": 5, "max_memory_mb": 128, "max_output_bytes": 51200},
            status=ExperimentStatus(db_obj.status),
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )


class ExperimentSummary(BaseModel):
    project_id: str
    total_experiments: int = 0
    experiments: List[Experiment] = Field(default_factory=list)
