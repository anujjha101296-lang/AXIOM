"""
AXIOM MIP — FastAPI Router
All /mip/* endpoints for the Mathematical Intelligence Platform.
Mounted in axiom/services/api_gateway/main.py at prefix /mip.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/mip", tags=["Mathematical Intelligence Platform"])

# ─────────────── Shared DB helper ───────────────

def _db_path() -> str:
    import os
    return os.getenv("AXIOM_DB_PATH", "axiom.db")


# ══════════════════════════════════════════════════
# Dept A — Knowledge Endpoints
# ══════════════════════════════════════════════════

class IngestPayload(BaseModel):
    object_type: str
    name: str
    statement: str
    domain: str = "unknown"
    latex: str | None = None
    source_ref: str | None = None
    tags: list[str] = []
    metadata: dict[str, Any] = {}


@router.post("/knowledge/ingest", summary="Ingest a new mathematical entity")
async def knowledge_ingest(payload: IngestPayload) -> dict[str, Any]:
    """Ingest a new mathematical object into MIP knowledge store."""
    from axiom.mip.knowledge.ontology import classify_domain, MathDomain
    from axiom.mip.knowledge.schema import MathNode, MathObjectType

    node_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Auto-classify domain if not provided
    domain = payload.domain
    if domain == "unknown":
        domain = classify_domain(payload.statement).value

    conn = sqlite3.connect(_db_path())
    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO mip_objects
                (id, object_type, name, statement, domain, epistemic_status,
                 latex, source_ref, tags, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'unknown', ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    payload.object_type,
                    payload.name,
                    payload.statement,
                    domain,
                    payload.latex,
                    payload.source_ref,
                    json.dumps(payload.tags),
                    json.dumps(payload.metadata),
                    now,
                    now,
                ),
            )
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")
    finally:
        conn.close()

    return {
        "node_id": node_id,
        "object_type": payload.object_type,
        "name": payload.name,
        "domain": domain,
        "message": "Successfully ingested into MIP knowledge store",
    }


@router.get("/knowledge/lookup", summary="Look up a mathematical concept")
async def knowledge_lookup(name: str, domain: str | None = None) -> dict[str, Any]:
    """Retrieve a mathematical concept by name (fuzzy match)."""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        query = "SELECT * FROM mip_objects WHERE name LIKE ? "
        params: list[Any] = [f"%{name}%"]
        if domain:
            query += "AND domain = ? "
            params.append(domain)
        query += "ORDER BY updated_at DESC LIMIT 10"
        rows = conn.execute(query, params).fetchall()
        results = [dict(r) for r in rows]
    except sqlite3.OperationalError:
        results = []
    finally:
        conn.close()

    return {
        "found": len(results) > 0,
        "count": len(results),
        "results": results,
    }


@router.get("/knowledge/domain/{domain}", summary="List entities in a domain")
async def knowledge_by_domain(domain: str, limit: int = 20) -> dict[str, Any]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM mip_objects WHERE domain = ? ORDER BY created_at DESC LIMIT ?",
            (domain, limit),
        ).fetchall()
        results = [dict(r) for r in rows]
    except sqlite3.OperationalError:
        results = []
    finally:
        conn.close()
    return {"domain": domain, "count": len(results), "entities": results}


# ══════════════════════════════════════════════════
# Dept B — Formal Mathematics Endpoints
# ══════════════════════════════════════════════════

class FormalGeneratePayload(BaseModel):
    theorem_name: str
    statement: str
    system: str = "lean4"  # lean4, coq, isabelle
    hypotheses: list[str] = []
    namespace: str = "AXIOM"


@router.post("/formal/generate", summary="Generate formal proof script")
async def formal_generate(payload: FormalGeneratePayload) -> dict[str, Any]:
    """Generate a formal proof script for Lean 4, Coq, or Isabelle."""
    system = payload.system.lower()
    try:
        if system == "lean4":
            from axiom.mip.formal.lean4 import generate_theorem
            result = generate_theorem(
                payload.theorem_name, payload.statement,
                namespace=payload.namespace,
                hypotheses=payload.hypotheses or None,
            )
            return {
                "system": "lean4",
                "theorem_name": result.theorem_name,
                "script": result.script,
                "suggested_tactics": result.suggested_tactics,
                "fallback_mode": result.fallback_mode,
            }
        elif system == "coq":
            from axiom.mip.formal.coq import generate_theorem
            result = generate_theorem(
                payload.theorem_name, payload.statement,
                hypotheses=payload.hypotheses or None,
            )
            return {
                "system": "coq",
                "theorem_name": result.theorem_name,
                "script": result.script,
            }
        elif system == "isabelle":
            from axiom.mip.formal.isabelle import generate_theorem
            result = generate_theorem(
                payload.theorem_name, payload.statement,
                hypotheses=payload.hypotheses or None,
            )
            return {
                "system": "isabelle",
                "theorem_name": result.theorem_name,
                "script": result.script,
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown formal system: {system}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/formal/compile", summary="Compile a formal proof script")
async def formal_compile(
    system: str,
    script: str,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Compile a formal proof script and return compilation result."""
    from axiom.core.verification.truthfulness import evidence_mode_from_compile_result, EvidenceMode

    system = system.lower()
    try:
        if system == "lean4":
            from axiom.mip.formal.lean4 import compile_lean4
            success, output = compile_lean4(script, timeout_seconds)
        elif system == "coq":
            from axiom.mip.formal.coq import compile_coq
            success, output = compile_coq(script, timeout_seconds)
        elif system == "isabelle":
            from axiom.mip.formal.isabelle import compile_isabelle
            success, output = compile_isabelle(script, timeout_seconds)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown system: {system}")

        evidence_mode = evidence_mode_from_compile_result(success, output)
        formally_verified = success and evidence_mode == EvidenceMode.FORMAL_COMPILER
        return {
            "system": system,
            "success": success,
            "output": output,
            "evidence_mode": evidence_mode.value,
            "formally_verified": formally_verified,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ══════════════════════════════════════════════════
# Dept D — Conjecture Generation Endpoints
# ══════════════════════════════════════════════════

class ConjectureGeneratePayload(BaseModel):
    n_conjectures: int = 5
    min_novelty: float = 0.25
    seed_domain: str | None = None


@router.post("/conjecture/generate", summary="Generate candidate conjectures")
async def conjecture_generate(payload: ConjectureGeneratePayload) -> dict[str, Any]:
    """Autonomously generate new mathematical conjectures from EGS patterns."""
    try:
        from axiom.mip.conjecture.generator import ConjectureGenerator
        gen = ConjectureGenerator(db_path=_db_path(), min_novelty=payload.min_novelty)
        candidates = gen.generate(
            n_conjectures=payload.n_conjectures,
            seed_domain=payload.seed_domain,
        )
        saved_ids = gen.save_to_db(candidates)
        return {
            "count": len(candidates),
            "conjectures": [
                {
                    "id": saved_ids[i] if i < len(saved_ids) else None,
                    "statement": c.statement,
                    "strategy": c.strategy,
                    "novelty_score": c.novelty_score,
                    "domain": c.domain,
                    "source_node_ids": c.source_node_ids,
                }
                for i, c in enumerate(candidates)
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/conjecture/ranked", summary="Get ranked open conjectures")
async def conjecture_ranked(limit: int = 20) -> dict[str, Any]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM mip_conjectures WHERE status='open' ORDER BY novelty_score DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return {"count": len(rows), "conjectures": [dict(r) for r in rows]}
    except sqlite3.OperationalError:
        return {"count": 0, "conjectures": []}
    finally:
        conn.close()


# ══════════════════════════════════════════════════
# Dept F — Research Strategy Endpoints
# ══════════════════════════════════════════════════

@router.post("/strategy/plan", summary="Generate research plan for a problem")
async def strategy_plan(problem_id: str, max_lemmas: int = 10) -> dict[str, Any]:
    """Generate a prioritized research plan for a Millennium Prize Problem."""
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES, get_prioritized_queue
    if problem_id not in MILLENNIUM_TREES:
        available = list(MILLENNIUM_TREES.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Problem '{problem_id}' not found. Available: {available}",
        )
    tree = MILLENNIUM_TREES[problem_id]
    queue = get_prioritized_queue(problem_id)[:max_lemmas]
    return {
        "problem_id": problem_id,
        "problem_name": tree.name,
        "total_lemmas": len(get_prioritized_queue(problem_id)),
        "prioritized_queue": queue,
        "recommended_next_attack": queue[0] if queue else None,
    }


@router.get("/strategy/decompose/{problem_id}", summary="Get hierarchical problem decomposition")
async def strategy_decompose(problem_id: str) -> dict[str, Any]:
    """Return full hierarchical decomposition tree for a Millennium Problem."""
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES
    if problem_id not in MILLENNIUM_TREES:
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")
    tree = MILLENNIUM_TREES[problem_id]
    return {"problem_id": problem_id, "tree": tree.to_dict()}


@router.get("/strategy/roadmap", summary="Get current research roadmap")
async def strategy_roadmap() -> dict[str, Any]:
    """Return overview of all 6 Millennium Problems with priority indices."""
    from axiom.mip.strategy.millennium_trees import MILLENNIUM_TREES
    return {
        "problems": [
            {
                "id": pid,
                "name": tree.name,
                "domain": tree.domain,
                "feasibility": tree.feasibility,
                "top_lemma": get_prioritized_queue_top(pid),
            }
            for pid, tree in MILLENNIUM_TREES.items()
        ]
    }


def get_prioritized_queue_top(problem_id: str) -> dict | None:
    from axiom.mip.strategy.millennium_trees import get_prioritized_queue
    q = get_prioritized_queue(problem_id)
    return q[0] if q else None


# ══════════════════════════════════════════════════
# Dept G — Memory Endpoints
# ══════════════════════════════════════════════════

# Session memory singleton (process-scoped)
_SESSION_MEMORY: Any = None


def _get_session_memory():
    global _SESSION_MEMORY
    if _SESSION_MEMORY is None:
        from axiom.mip.memory.episodic import EpisodicMemory
        _SESSION_MEMORY = EpisodicMemory()
    return _SESSION_MEMORY


@router.get("/memory/context", summary="Get current working memory state")
async def memory_context() -> dict[str, Any]:
    """Return the current session's working memory context."""
    mem = _get_session_memory()
    return mem.to_dict()


class MemorySnapshotPayload(BaseModel):
    problem_id: str | None = None
    note: str | None = None


@router.post("/memory/snapshot", summary="Persist session memory to long-term store")
async def memory_snapshot(payload: MemorySnapshotPayload) -> dict[str, Any]:
    """Persist current episodic memory to semantic long-term store."""
    from axiom.mip.memory.episodic import SemanticMemory
    mem = _get_session_memory()
    if payload.problem_id:
        mem.problem_id = payload.problem_id
    semantic = SemanticMemory(db_path=_db_path())
    try:
        snapshot_id = semantic.save_snapshot(mem)
        return {"snapshot_id": snapshot_id, "session_id": mem.session_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/memory/failed_tactics/{theorem_id}", summary="Get failed tactics for theorem")
async def memory_failed_tactics(theorem_id: str) -> dict[str, Any]:
    from axiom.mip.memory.episodic import SemanticMemory, FailureGuard
    mem = _get_session_memory()
    semantic = SemanticMemory(db_path=_db_path())
    guard = FailureGuard(mem, semantic)
    excluded = guard.get_excluded_tactics(theorem_id)
    return {"theorem_id": theorem_id, "failed_tactics": excluded, "count": len(excluded)}


# ══════════════════════════════════════════════════
# Dept H — Verification Endpoints
# ══════════════════════════════════════════════════

class VerifyPayload(BaseModel):
    claim: str
    proof_script: str | None = None
    timeout_seconds: float = 30.0


@router.post("/verify/claim", summary="Run independent verification consensus on a claim")
async def verify_claim(payload: VerifyPayload) -> dict[str, Any]:
    """Run multi-verifier consensus (SMT + Formal + Sanity) on a mathematical claim."""
    from axiom.core.verification.truthfulness import EvidenceMode, is_simulated_compiler_output
    from axiom.mip.verification.consensus import VerificationConsensus
    engine = VerificationConsensus(timeout_seconds=payload.timeout_seconds)
    result = engine.verify(payload.claim, payload.proof_script)

    formally_proven = any(
        r.verifier_name == "Formal/Lean4"
        and r.verdict.value == "VERIFIED"
        and not is_simulated_compiler_output(r.evidence)
        for r in result.verifier_results
    )
    evidence_modes = []
    for r in result.verifier_results:
        if r.verifier_name == "Formal/Lean4":
            evidence_modes.append(
                EvidenceMode.FORMAL_COMPILER.value
                if formally_proven
                else EvidenceMode.SIMULATED.value
                if is_simulated_compiler_output(r.evidence)
                else EvidenceMode.UNVERIFIED.value
            )
        elif r.verifier_name == "SMT/Z3":
            evidence_modes.append(EvidenceMode.SMT_FINITE.value)
        else:
            evidence_modes.append(EvidenceMode.HEURISTIC.value)

    return {
        "claim": result.claim,
        "final_verdict": result.final_verdict,
        "agreement_ratio": result.agreement_ratio,
        "explanation": result.explanation,
        "total_execution_time_ms": result.total_execution_time_ms,
        "formally_proven": formally_proven,
        "evidence_modes": sorted(set(evidence_modes)),
        "verifier_results": [
            {
                "verifier": r.verifier_name,
                "verdict": r.verdict,
                "confidence": r.confidence,
                "evidence": r.evidence,
                "execution_time_ms": r.execution_time_ms,
            }
            for r in result.verifier_results
        ],
    }
