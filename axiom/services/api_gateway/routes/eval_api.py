"""
FastAPI Evaluation Router for EPIC-002
Exposes capability scores, prize readiness, history, and benchmark triggers.
"""
from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from axiom.config import settings
from axiom.evaluation.frameworks.capability import (
    CapabilitySnapshot,
    CapabilityDimension,
    EvidenceState,
    make_dimension_score_from_benchmark,
)
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.reporting.delta_report import generate_delta_report
from axiom.observability.run_provenance import get_provenance_store, record_scep_run
from axiom.security.deps import eval_route_auth
from axiom.evaluation.benchmarks.suite import (
    run_math_reasoning_benchmarks,
    run_proof_verification_benchmarks,
    run_conjecture_benchmarks,
    run_knowledge_quality_benchmarks,
    run_counterexample_benchmarks,
    run_research_planning_benchmarks,
    run_literature_synthesis_benchmarks,
    run_research_productivity_benchmarks,
)

router = APIRouter(prefix="/eval", tags=["evaluation"])


class BenchmarkRunResponse(BaseModel):
    run_id: str
    timestamp: str
    composite_score: float
    dimensions: Dict[str, Any]
    evidence_tier: Dict[str, Any]
    limitations: List[str]
    readiness: List[Dict[str, Any]]
    weakest_capability: str
    highest_priority: str
    recommended_next_epic: str
    regression_detected: bool


def _get_current_scores(db_path: str) -> Dict[str, Any]:
    """Fetch or run the latest capability scores."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if we have a run recorded
    try:
        row = cursor.execute(
            "SELECT json_data FROM eval_runs ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        row = None
        
    conn.close()
    
    if row:
        return json.loads(row[0])
        
    # Standard baseline fallback if DB empty — explicitly labeled BASELINE
    return {
        "run_id": "initial",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "composite_score": 0.354,
        "evidence_tier": {"aggregate": EvidenceState.BASELINE.value},
        "limitations": [
            "No benchmark run recorded — scores are baseline placeholders",
            "Run POST /eval/run to produce measured capability scores",
        ],
        "dimensions": {
            "mathematical_reasoning": {
                "score": 0.40, "level": 1, "level_name": "L1: Basic",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "proof_verification": {
                "score": 0.35, "level": 0, "level_name": "L0: None",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "conjecture_generation": {
                "score": 0.30, "level": 2, "level_name": "L2: Undergraduate",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "knowledge_quality": {
                "score": 0.45, "level": 2, "level_name": "L2: Undergraduate",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "counterexample_search": {
                "score": 0.35, "level": 2, "level_name": "L2: Undergraduate",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "research_planning": {
                "score": 0.30, "level": 1, "level_name": "L1: Basic",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "literature_synthesis": {
                "score": 0.40, "level": 1, "level_name": "L1: Basic",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
            "research_productivity": {
                "score": 0.30, "level": 2, "level_name": "L2: Undergraduate",
                "benchmark_count": 0, "evidence_state": EvidenceState.BASELINE.value,
            },
        },
    }


@router.get("/scores")
def get_capability_scores(_token: str = Depends(eval_route_auth)):
    """Retrieve the latest capability scores for all 8 dimensions."""
    data = _get_current_scores(settings.db_path)
    return data["dimensions"]


@router.get("/prize-readiness")
def get_prize_readiness(_token: str = Depends(eval_route_auth)):
    """Get the latest prize readiness scores for all 6 Millennium Problems."""
    data = _get_current_scores(settings.db_path)
    
    # Calculate readiness from scores
    scores_map = {}
    for d_name, info in data.get("dimensions", {}).items():
        scores_map[d_name] = info.get("score", 0.0)
        
    engine = PrizeReadinessEngine()
    readiness_list = engine.compute_all(scores_map)
    return engine.to_ranked_list(readiness_list)


@router.get("/history")
def get_run_history(_token: str = Depends(eval_route_auth)):
    """Get the last 10 evaluation runs with provenance summaries."""
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()
    provenance = get_provenance_store(settings.db_path)

    try:
        rows = cursor.execute(
            "SELECT run_id, timestamp, composite_score FROM eval_runs ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()
        history = []
        for r in rows:
            entry = {"run_id": r[0], "timestamp": r[1], "composite_score": r[2]}
            prov = provenance.get("scep", r[0])
            if prov:
                entry["duration_ms"] = prov.get("duration_ms")
                entry["evidence_tier"] = prov.get("evidence_tier", {}).get("aggregate")
                entry["config_hash"] = prov.get("config_hash")
            history.append(entry)
    except sqlite3.OperationalError:
        history = []

    conn.close()
    return history


@router.get("/runs/{run_id}")
def get_eval_run(run_id: str, _token: str = Depends(eval_route_auth)):
    """Retrieve a SCEP evaluation run snapshot and its provenance record."""
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()

    try:
        row = cursor.execute(
            "SELECT json_data FROM eval_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
    except sqlite3.OperationalError:
        row = None

    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Eval run not found: {run_id}")

    snapshot = json.loads(row[0])
    provenance = get_provenance_store(settings.db_path).get("scep", run_id)
    return {"snapshot": snapshot, "provenance": provenance}


@router.post("/run", response_model=BenchmarkRunResponse)
def trigger_benchmark(_token: str = Depends(eval_route_auth)):
    """Run all capability benchmarks synchronously and return current scores & delta report."""
    db_path = settings.db_path
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    wall_start = time.perf_counter()

    # Run all 8 suites
    mr_results, mr_score = run_math_reasoning_benchmarks()
    pv_results, pv_score = run_proof_verification_benchmarks()
    cg_results, cg_score = run_conjecture_benchmarks(db_path)
    kq_results, kq_score = run_knowledge_quality_benchmarks(db_path)
    ce_results, ce_score = run_counterexample_benchmarks(db_path)
    rp_results, rp_score = run_research_planning_benchmarks()
    ls_results, ls_score = run_literature_synthesis_benchmarks(db_path)
    rd_results, rd_score = run_research_productivity_benchmarks(db_path)
    
    import uuid
    run_id = str(uuid.uuid4())[:8]
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    snapshot = CapabilitySnapshot(run_id=run_id, timestamp=timestamp)
    snapshot.dimension_scores = [
        make_dimension_score_from_benchmark(CapabilityDimension.MATHEMATICAL_REASONING, mr_score, len(mr_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.PROOF_VERIFICATION, pv_score, len(pv_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.CONJECTURE_GENERATION, cg_score, len(cg_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.KNOWLEDGE_QUALITY, kq_score, len(kq_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.COUNTEREXAMPLE_SEARCH, ce_score, len(ce_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.RESEARCH_PLANNING, rp_score, len(rp_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.LITERATURE_SYNTHESIS, ls_score, len(ls_results)),
        make_dimension_score_from_benchmark(CapabilityDimension.RESEARCH_PRODUCTIVITY, rd_score, len(rd_results)),
    ]
    snapshot.compute_composite()
    
    # Compute Prize Readiness
    scores_map = {s.dimension.value: s.raw_score for s in snapshot.dimension_scores}
    engine = PrizeReadinessEngine()
    readiness_scores = engine.compute_all(scores_map)
    
    # Get previous run for comparison
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    prev_run = None
    prev_readiness = None
    
    try:
        # Save run first so it exists, but fetch previous first
        prev_row = cursor.execute(
            "SELECT json_data FROM eval_runs ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        
        if prev_row:
            prev_run = json.loads(prev_row[0])
            prev_run_id = prev_run["run_id"]
            readiness_rows = cursor.execute(
                "SELECT json_data FROM eval_readiness WHERE run_id = ?", (prev_run_id,)
            ).fetchall()
            prev_readiness = [json.loads(r[0]) for r in readiness_rows]
    except sqlite3.OperationalError:
        pass
        
    # Ensure tables exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eval_runs (
        run_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        composite_score REAL NOT NULL,
        json_data TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eval_readiness (
        run_id TEXT NOT NULL,
        problem_id TEXT NOT NULL,
        score REAL NOT NULL,
        json_data TEXT NOT NULL,
        PRIMARY KEY (run_id, problem_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eval_results (
        run_id TEXT NOT NULL,
        case_id TEXT NOT NULL,
        score REAL NOT NULL,
        passed INTEGER NOT NULL,
        time_ms REAL NOT NULL,
        notes TEXT,
        PRIMARY KEY (run_id, case_id)
    )
    """)
    
    # Save current run
    cursor.execute(
        "INSERT INTO eval_runs (run_id, timestamp, composite_score, json_data) VALUES (?, ?, ?, ?)",
        (snapshot.run_id, snapshot.timestamp, snapshot.composite_score, json.dumps(snapshot.to_dict()))
    )
    
    for score in readiness_scores:
        cursor.execute(
            "INSERT INTO eval_readiness (run_id, problem_id, score, json_data) VALUES (?, ?, ?, ?)",
            (snapshot.run_id, score.problem_id, score.score, json.dumps(score.to_dict()))
        )

    all_results = mr_results + pv_results + cg_results + kq_results + ce_results + rp_results + ls_results + rd_results
    for res in all_results:
        cursor.execute(
            "INSERT INTO eval_results (run_id, case_id, score, passed, time_ms, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (snapshot.run_id, res.case_id, res.score, 1 if res.passed else 0, res.time_ms, getattr(res, "notes", ""))
        )
        
    conn.commit()
    conn.close()

    duration_ms = (time.perf_counter() - wall_start) * 1000
    record_scep_run(
        db_path,
        snapshot,
        all_results,
        started_at=started_at,
        duration_ms=duration_ms,
        trigger="api",
    )
    
    # Generate delta report
    report = generate_delta_report(
        epic_name="EPIC-002",
        prev_snapshot=prev_run,
        curr_snapshot=snapshot,
        prev_readiness=prev_readiness,
        curr_readiness=readiness_scores
    )
    
    # Save Markdown report
    try:
        report_md_path = f"docs/capability_delta_{run_id}.md"
        with open(report_md_path, "w") as f:
            f.write(report.to_markdown())
    except Exception:
        pass
        
    return {
        "run_id": snapshot.run_id,
        "timestamp": snapshot.timestamp,
        "composite_score": snapshot.composite_score,
        "dimensions": snapshot.to_dict()["dimensions"],
        "evidence_tier": snapshot.evidence_tier,
        "limitations": snapshot.limitations,
        "readiness": [r.to_dict() for r in readiness_scores],
        "weakest_capability": report.weakest_capability,
        "highest_priority": report.highest_priority,
        "recommended_next_epic": report.recommended_next_epic,
        "regression_detected": report.regression_detected,
    }
