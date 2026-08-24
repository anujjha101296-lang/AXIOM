"""
axiom.formal.models
===================
Pydantic Domain Models for Phase 16 Formal Mathematics & Proof Verification Engine.
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


class ProofStatus(str, Enum):
    UNFORMALIZED = "UNFORMALIZED"
    FORMALIZED = "FORMALIZED"
    PROOF_IN_PROGRESS = "PROOF_IN_PROGRESS"
    VERIFIED = "VERIFIED"
    DISPROVEN = "DISPROVEN"
    OPEN = "OPEN"


class FormalLanguage(str, Enum):
    LEAN4 = "LEAN4"
    COQ = "COQ"
    ISABELLE = "ISABELLE"
    SMT_Z3 = "SMT_Z3"


class SMTResult(str, Enum):
    SAT = "SAT"
    UNSAT = "UNSAT"
    UNKNOWN = "UNKNOWN"


class FormalProof(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    theorem_id: str
    proof_script: str
    verifier_output: str = ""
    compiler_version: str = "Lean 4.7.0 / Z3 4.12.2"
    status: ProofStatus = ProofStatus.PROOF_IN_PROGRESS
    is_sorry_free: bool = True
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> FormalProof:
        return cls(
            id=db_obj.id,
            theorem_id=db_obj.theorem_id,
            proof_script=db_obj.proof_script,
            verifier_output=db_obj.verifier_output,
            compiler_version=db_obj.compiler_version,
            status=ProofStatus(db_obj.status),
            is_sorry_free=db_obj.is_sorry_free,
            created_at=db_obj.created_at,
        )


class Counterexample(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    theorem_id: str
    domain: str = "Finite domain"
    assignment: Dict[str, Any] = Field(default_factory=dict)
    witness_summary: str = ""
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> Counterexample:
        assign = {}
        if hasattr(db_obj, "assignment_json") and db_obj.assignment_json:
            try:
                assign = json.loads(db_obj.assignment_json)
            except Exception:
                assign = {}
        return cls(
            id=db_obj.id,
            theorem_id=db_obj.theorem_id,
            domain=db_obj.domain,
            assignment=assign,
            witness_summary=db_obj.witness_summary,
            created_at=db_obj.created_at,
        )


class ProofArtifact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    theorem_id: str
    proof_id: str
    hash_id: str
    artifact_uri: str = ""
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_db(cls, db_obj: Any) -> ProofArtifact:
        return cls(
            id=db_obj.id,
            theorem_id=db_obj.theorem_id,
            proof_id=db_obj.proof_id,
            hash_id=db_obj.hash_id,
            artifact_uri=db_obj.artifact_uri,
            created_at=db_obj.created_at,
        )


class FormalTheorem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_uuid)
    project_id: str
    claim_id: Optional[str] = None
    name: str
    natural_language: str
    formal_statement: str
    language: FormalLanguage = FormalLanguage.LEAN4
    status: ProofStatus = ProofStatus.FORMALIZED
    assumptions: List[str] = Field(default_factory=list)
    variables: List[str] = Field(default_factory=list)
    quantifiers: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    proofs: List[FormalProof] = Field(default_factory=list)
    counterexamples: List[Counterexample] = Field(default_factory=list)
    latest_artifact: Optional[ProofArtifact] = None

    @classmethod
    def from_db(cls, db_obj: Any) -> FormalTheorem:
        assumptions = []
        variables = []
        quantifiers = []
        meta = {}
        if hasattr(db_obj, "assumptions_json") and db_obj.assumptions_json:
            try:
                assumptions = json.loads(db_obj.assumptions_json)
            except Exception:
                assumptions = []
        if hasattr(db_obj, "variables_json") and db_obj.variables_json:
            try:
                variables = json.loads(db_obj.variables_json)
            except Exception:
                variables = []
        if hasattr(db_obj, "quantifiers_json") and db_obj.quantifiers_json:
            try:
                quantifiers = json.loads(db_obj.quantifiers_json)
            except Exception:
                quantifiers = []
        if hasattr(db_obj, "metadata_json") and db_obj.metadata_json:
            try:
                meta = json.loads(db_obj.metadata_json)
            except Exception:
                meta = {}

        return cls(
            id=db_obj.id,
            project_id=db_obj.project_id,
            claim_id=db_obj.claim_id,
            name=db_obj.name,
            natural_language=db_obj.natural_language,
            formal_statement=db_obj.formal_statement,
            language=FormalLanguage(db_obj.language),
            status=ProofStatus(db_obj.status),
            assumptions=assumptions,
            variables=variables,
            quantifiers=quantifiers,
            metadata=meta,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )


class FormalSummary(BaseModel):
    project_id: str
    total_theorems: int = 0
    theorems: List[FormalTheorem] = Field(default_factory=list)
