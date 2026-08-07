"""
FastAPI Evaluation Router for EPIC-002
Exposes capability scores, prize readiness, history, and benchmark triggers.
S0-E4: all scores include evidence_state, benchmark_count, and limitations.
"""
from __future__ import annotations

import json
import sqlite3
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from axiom.config import settings
from axiom.evaluation.frameworks.evidence import (
    REQUIRED_SCORE_FIELDS,
    build_baseline_dimensions_dict,
    build_baseline_snapshot,
    run_all_capability_benchmarks,
)
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.reporting.delta_report import generate_delta_report
from axiom.observability.run_provenance import ProvenanceStore, get_provenance_store, record_scep_run

router = APIRouter(prefix="/eval", tags=["evaluation"])


class BenchmarkRunResponse(BaseModel):
    run_id: str
    timestamp: str
    composite_score: float
    dimensions: dict[str, Any]
    readiness: list[dict[str, Any]]
    weakest_capability: str
    highest_priority: str
    recommended_next_epic: str
    regression_detected: bool


def _normalize_dimension(dim_name: str, info: dict[str, Any]) -> dict[str, Any]:
    """Backfill S0-E4 fields on legacy stored snapshots."""
    if all(f in info for f in REQUIRED_SCORE_FIELDS):
        return info
    baseline = build_baseline_dimensions_dict().get(dim_name, {})
    merged = {**baseline, **info}
    if "limitations" not in merged or not merged["limitations"]:
        merged["limitations"] = baseline.get("limitations", ["Legacy snapshot — re-run benchmarks for full evidence."])
    if "evidence_state" not in merged:
        merged["evidence_state"] = "estimated" if merged.get("estimated") else "measured"
    if "benchmark_count" not in merged:
        merged["benchmark_count"] = 0
    if "confidence" not in merged:
        merged["confidence"] = 0.5
    return merged


def _normalize_snapshot(data: dict[str, Any]) -> dict[str, Any]:
    dimensions = data.get("dimensions", {})
    data["dimensions"] = {
        name: _normalize_dimension(name, info) for name, info in dimensions.items()
    }
    return data


def _get_current_scores(db_path: str) -> dict[str, Any]:
    """Fetch latest capability scores or return evidence-gated baseline."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        row = cursor.execute(
            "SELECT json_data FROM eval_runs ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        row = None

    conn.close()

    if row:
        return _normalize_snapshot(json.loads(row[0]))

    baseline = build_baseline_snapshot()
    return baseline.to_dict()


@router.get("/scores")
def get_capability_scores():
    """Retrieve the latest capability scores for all 8 dimensions."""
    data = _get_current_scores(settings.db_path)
    return data["dimensions"]


@router.get("/prize-readiness")
def get_prize_readiness():
    """Get the latest prize readiness scores for all 6 Millennium Problems."""
    data = _get_current_scores(settings.db_path)

    scores_map = {}
    for d_name, info in data.get("dimensions", {}).items():
        scores_map[d_name] = info.get("score", 0.0)

    engine = PrizeReadinessEngine()
    readiness_list = engine.compute_all(scores_map)
    return engine.to_ranked_list(readiness_list)


@router.get("/history")
def get_run_history():
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
def get_eval_run(run_id: str):
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

    snapshot = _normalize_snapshot(json.loads(row[0]))
    provenance = get_provenance_store(settings.db_path).get("scep", run_id)
    return {"snapshot": snapshot, "provenance": provenance}


def _ensure_eval_tables(cursor: sqlite3.Cursor) -> None:
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


@router.post("/run", response_model=BenchmarkRunResponse)
def trigger_benchmark():
    """Run all capability benchmarks synchronously and return current scores & delta report."""
    db_path = settings.db_path
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    wall_start = time.perf_counter()

    bundle = run_all_capability_benchmarks(db_path)
    snapshot = bundle.snapshot
    duration_ms = (time.perf_counter() - wall_start) * 1000

    engine = PrizeReadinessEngine()
    readiness_scores = engine.compute_all(bundle.scores_map)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    prev_run = None
    prev_readiness = None

    try:
        prev_row = cursor.execute(
            "SELECT json_data FROM eval_runs ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()

        if prev_row:
            prev_run = _normalize_snapshot(json.loads(prev_row[0]))
            prev_run_id = prev_run["run_id"]
            readiness_rows = cursor.execute(
                "SELECT json_data FROM eval_readiness WHERE run_id = ?", (prev_run_id,)
            ).fetchall()
            prev_readiness = [json.loads(r[0]) for r in readiness_rows]
    except sqlite3.OperationalError:
        pass

    _ensure_eval_tables(cursor)

    cursor.execute(
        "INSERT INTO eval_runs (run_id, timestamp, composite_score, json_data) VALUES (?, ?, ?, ?)",
        (snapshot.run_id, snapshot.timestamp, snapshot.composite_score, json.dumps(snapshot.to_dict())),
    )

    for score in readiness_scores:
        cursor.execute(
            "INSERT INTO eval_readiness (run_id, problem_id, score, json_data) VALUES (?, ?, ?, ?)",
            (snapshot.run_id, score.problem_id, score.score, json.dumps(score.to_dict())),
        )

    for res in bundle.all_results:
        cursor.execute(
            "INSERT INTO eval_results (run_id, case_id, score, passed, time_ms, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (snapshot.run_id, res.case_id, res.score, 1 if res.passed else 0, res.time_ms, getattr(res, "notes", "")),
        )

    conn.commit()
    conn.close()

    record_scep_run(
        db_path,
        snapshot,
        bundle.all_results,
        started_at=started_at,
        duration_ms=duration_ms,
        trigger="api",
    )

    report = generate_delta_report(
        epic_name="EPIC-002",
        prev_snapshot=prev_run,
        curr_snapshot=snapshot,
        prev_readiness=prev_readiness,
        curr_readiness=readiness_scores,
    )

    try:
        report_md_path = f"docs/capability_delta_{snapshot.run_id}.md"
        with open(report_md_path, "w") as f:
            f.write(report.to_markdown())
    except OSError:
        pass

    return {
        "run_id": snapshot.run_id,
        "timestamp": snapshot.timestamp,
        "composite_score": snapshot.composite_score,
        "dimensions": snapshot.to_dict()["dimensions"],
        "readiness": [r.to_dict() for r in readiness_scores],
        "weakest_capability": report.weakest_capability,
        "highest_priority": report.highest_priority,
        "recommended_next_epic": report.recommended_next_epic,
        "regression_detected": report.regression_detected,
    }
