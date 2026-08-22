"""Data models for Phase 14 Formal Verification Engine."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProverType(str, Enum):
    LEAN4 = "LEAN4"
    COQ = "COQ"
    ISABELLE = "ISABELLE"
    SMT_Z3 = "SMT_Z3"


class FormalStatus(str, Enum):
    VERIFIED = "VERIFIED"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    TYPE_CHECK_FAILED = "TYPE_CHECK_FAILED"
    TIMEOUT = "TIMEOUT"
    UNPROVED_SORRY = "UNPROVED_SORRY"


class FormalTheorem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    statement: str
    prover: ProverType
    imports: List[str] = Field(default_factory=list)
    variables: Dict[str, str] = Field(default_factory=dict)


class ProofStep(BaseModel):
    step_number: int
    tactic_or_command: str
    state_after: Optional[str] = None


class FormalProof(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    theorem_id: str
    prover: ProverType
    code_script: str
    steps: List[ProofStep] = Field(default_factory=list)
    contains_sorry: bool = False


class FormalVerificationResult(BaseModel):
    verification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    theorem_name: str
    prover: ProverType
    status: FormalStatus
    proof_code: str
    error_message: Optional[str] = None
    verification_time_ms: float
    verified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
