"""FMTP Loop — Formal Mathematics & Theorem-Proving API."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.formal_math.benchmarks import estimate_difficulty, list_benchmarks
from axiom.formal_math.compilation import compile_proof
from axiom.formal_math.conjecture import generate_conjecture
from axiom.formal_math.counterexample import search_counterexample
from axiom.formal_math.decomposition import decompose_goal
from axiom.formal_math.dependency_graph import build_dependency_graph
from axiom.formal_math.explanation import explain_formal_artifact
from axiom.formal_math.formalization import formalize_informal
from axiom.formal_math.library_search import search_library
from axiom.formal_math.millennium_gate import evaluate_millennium_readiness
from axiom.formal_math.models import ProofArtifact, ProofCompilationStatus
from axiom.formal_math.proof_search import attempt_proof_search, generate_proof_strategies
from axiom.formal_math.prover_registry import get_prover, list_provers
from axiom.formal_math.repair import create_failure_record, suggest_repair_tactics
from axiom.formal_math.store import get_formal_math_store
from axiom.security.deps import formal_math_route_auth

router = APIRouter(
    prefix="/formal",
    tags=["formal-math"],
    dependencies=[Depends(formal_math_route_auth)],
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FormalizeRequest(BaseModel):
    statement: str
    theorem_name: str = "informal_theorem"
    prover: str | None = None


class ExplainRequest(BaseModel):
    formal_spec: str
    theorem_name: str = "theorem"
    compilation_status: str = "unknown"


class ProofSearchRequest(BaseModel):
    theorem_name: str
    statement: str
    strategy: str = "direct"


class CompileProofRequest(BaseModel):
    theorem_id: str
    source_code: str
    prover: str = "lean4"
    formal_statement: str = ""


class CounterexampleRequest(BaseModel):
    claim: str
    equation: str | None = None
    variables: list[str] = Field(default_factory=list)
    modulus: int = 10
    method: str = "smt_modular"


class ConjectureRequest(BaseModel):
    source_statement: str
    name: str = "source_theorem"
    domain: str = "unknown"


class RegisterEntityRequest(BaseModel):
    entity_type: str
    name: str
    statement: str
    domain: str = "unknown"
    dependencies: list[str] = Field(default_factory=list)


class RepairRequest(BaseModel):
    theorem_id: str
    approach: str
    prover_output: str
    attempted_tactic: str = ""
    goal_state: str = ""


@router.get("/provers")
def get_provers() -> dict[str, Any]:
    provers = list_provers()
    return {"count": len(provers), "provers": [p.to_dict() for p in provers]}


@router.get("/provers/{prover_id}")
def get_prover_detail(prover_id: str) -> dict[str, Any]:
    prover = get_prover(prover_id)
    if not prover:
        raise HTTPException(status_code=404, detail=f"Prover not found: {prover_id}")
    return prover.to_dict()


@router.post("/formalize")
def formalize_statement(body: FormalizeRequest) -> dict[str, Any]:
    result = formalize_informal(body.statement, theorem_name=body.theorem_name, prover=body.prover)
    get_formal_math_store(settings.db_path).save_formalization(result)
    return result.to_dict()


@router.post("/explain")
def explain_formal(body: ExplainRequest) -> dict[str, Any]:
    explanation = explain_formal_artifact(
        body.formal_spec,
        theorem_name=body.theorem_name,
        compilation_status=body.compilation_status,
    )
    return {"explanation": explanation, "theorem_name": body.theorem_name}


@router.post("/proof/search")
def proof_search(body: ProofSearchRequest) -> dict[str, Any]:
    return attempt_proof_search(body.theorem_name, body.statement, strategy_name=body.strategy)


@router.get("/proof/strategies")
def list_proof_strategies(statement: str) -> dict[str, Any]:
    return {"strategies": generate_proof_strategies(statement)}


@router.post("/proof/compile")
def compile_formal_proof(body: CompileProofRequest) -> dict[str, Any]:
    store = get_formal_math_store(settings.db_path)
    proof_id = f"prf_{uuid.uuid4().hex[:12]}"
    artifact = ProofArtifact(
        proof_id=proof_id,
        theorem_id=body.theorem_id,
        version=1,
        created_at=_utc_now(),
        prover=body.prover,
        prover_version=get_prover(body.prover).version if get_prover(body.prover) else "unknown",
        formal_statement=body.formal_statement or body.source_code[:200],
        source_code=body.source_code,
        compilation_status=ProofCompilationStatus.UNKNOWN,
    )
    status, output, trust_layers = compile_proof(artifact)
    artifact.compilation_status = status
    artifact.verification_output = output
    artifact.trust_layers = trust_layers
    store.save_proof(artifact)

    if status == ProofCompilationStatus.DOES_NOT_COMPILE:
        failure = create_failure_record(
            body.theorem_id,
            "compile",
            output,
            attempted_tactic="compile",
        )
        store.save_failure(failure)

    return artifact.to_dict()


@router.get("/library/search")
def library_search(q: str, domain: str | None = None, limit: int = 10) -> dict[str, Any]:
    results = search_library(q, domain=domain, limit=limit)
    return {"count": len(results), "results": results}


@router.post("/decompose")
def decompose_theorem(theorem_name: str, statement: str) -> dict[str, Any]:
    return decompose_goal(theorem_name, statement)


@router.post("/counterexample")
def find_counterexample(body: CounterexampleRequest) -> dict[str, Any]:
    record = search_counterexample(
        body.claim,
        equation=body.equation,
        variables=body.variables or None,
        modulus=body.modulus,
        method=body.method,
    )
    if not record:
        return {"found": False, "claim": body.claim}
    get_formal_math_store(settings.db_path).save_counterexample(record)
    return {"found": True, "counterexample": record.to_dict()}


@router.post("/conjecture")
def create_conjecture(body: ConjectureRequest) -> dict[str, Any]:
    return generate_conjecture(body.source_statement, name=body.name, domain=body.domain)


@router.post("/entities")
def register_entity(body: RegisterEntityRequest) -> dict[str, Any]:
    entity = get_formal_math_store(settings.db_path).register_entity(
        body.entity_type,
        body.name,
        body.statement,
        domain=body.domain,
        dependencies=body.dependencies,
    )
    return entity.to_dict()


@router.get("/entities/{entity_id}")
def get_entity(entity_id: str) -> dict[str, Any]:
    entity = get_formal_math_store(settings.db_path).get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")
    return entity.to_dict()


@router.get("/entities/{entity_id}/dependencies")
def get_dependency_graph(entity_id: str) -> dict[str, Any]:
    try:
        return build_dependency_graph(get_formal_math_store(settings.db_path), entity_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")


@router.get("/proofs/{proof_id}")
def get_proof(proof_id: str) -> dict[str, Any]:
    proof = get_formal_math_store(settings.db_path).get_proof(proof_id)
    if not proof:
        raise HTTPException(status_code=404, detail=f"Proof not found: {proof_id}")
    return proof.to_dict()


@router.post("/repair/suggest")
def suggest_repair(statement: str, failed_tactic: str) -> dict[str, Any]:
    tactics = suggest_repair_tactics(statement, failed_tactic)
    return {"suggested_tactics": tactics}


@router.post("/repair/failure")
def record_failure(body: RepairRequest) -> dict[str, Any]:
    record = create_failure_record(
        body.theorem_id,
        body.approach,
        body.prover_output,
        goal_state=body.goal_state,
        attempted_tactic=body.attempted_tactic,
    )
    get_formal_math_store(settings.db_path).save_failure(record)
    return record.to_dict()


@router.get("/benchmarks")
def get_benchmarks(level: int | None = None) -> dict[str, Any]:
    return {"benchmarks": list_benchmarks(level)}


@router.get("/difficulty")
def get_difficulty_estimate(statement: str) -> dict[str, Any]:
    return estimate_difficulty(statement)


@router.get("/millennium/readiness")
def millennium_readiness() -> dict[str, Any]:
    return evaluate_millennium_readiness().to_dict()


@router.get("/dashboard")
def formal_math_dashboard() -> dict[str, Any]:
    store = get_formal_math_store(settings.db_path)
    return {
        **store.dashboard_stats(),
        "provers": len(list_provers()),
        "benchmark_levels": len(list_benchmarks()),
    }
