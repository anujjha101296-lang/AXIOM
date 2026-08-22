"""Data models for Phase 12 Discovery Engine."""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProofStatus(str, Enum):
    PROVED = "PROVED"
    DISPROVED = "DISPROVED"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


class FormulaType(str, Enum):
    SUMMATION = "SUMMATION"
    INEQUALITY = "INEQUALITY"
    RECURRENCE = "RECURRENCE"
    MODULAR = "MODULAR"


class CandidateConjecture(BaseModel):
    id: str
    formula_type: FormulaType
    expression_str: str
    variables: List[str]
    domain_constraints: Dict[str, str] = Field(default_factory=dict)
    generated_at: str


class DiscoveryResult(BaseModel):
    conjecture: CandidateConjecture
    status: ProofStatus
    counterexample: Optional[Dict[str, Any]] = None
    proof_method: str
    closed_form: Optional[str] = None
    verification_time_ms: float
    inductive_samples_checked: int = 0
