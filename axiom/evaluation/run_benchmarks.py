#!/usr/bin/env python3
"""
AXIOM Evaluation Benchmark Runner
Runs all scientific capability benchmarks, evaluates prize readiness,
saves snapshots to SQLite, checks for regressions, and outputs delta reports.

Usage:
  python3 -m axiom.evaluation.run_benchmarks [--compare-previous] [--db PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import uuid

# Set up path to include workspace root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from axiom.evaluation.frameworks.capability import (
    CapabilitySnapshot,
    CapabilityDimension,
    make_dimension_score_from_benchmark,
)
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.reporting.delta_report import generate_delta_report
from axiom.observability.run_provenance import record_scep_run
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


def init_db(db_path: str):
    """Ensure evaluation tables exist in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Run evaluation schema setup
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
    
    conn.commit()
    conn.close()


def get_latest_run(db_path: str) -> tuple[Optional[dict], Optional[list]]:
    """Retrieve the latest evaluation run and readiness scores from the database."""
    if not os.path.exists(db_path):
        return None, None
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest run JSON
        row = cursor.execute(
            "SELECT json_data FROM eval_runs ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        
        if not row:
            conn.close()
            return None, None
            
        run_data = json.loads(row[0])
        run_id = run_data["run_id"]
        
        # Get matching readiness records
        readiness_rows = cursor.execute(
            "SELECT json_data FROM eval_readiness WHERE run_id = ?", (run_id,)
        ).fetchall()
        
        readiness_data = [json.loads(r[0]) for r in readiness_rows]
        conn.close()
        
        return run_data, readiness_data
    except Exception as e:
        print(f"Error fetching latest run: {e}")
        return None, None


def save_run(db_path: str, snapshot: CapabilitySnapshot, readiness_scores: list, benchmark_results: list | None = None):
    """Persist the run, readiness results, and benchmark case results in SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Save capability snapshot
    cursor.execute(
        "INSERT INTO eval_runs (run_id, timestamp, composite_score, json_data) VALUES (?, ?, ?, ?)",
        (
            snapshot.run_id,
            snapshot.timestamp,
            snapshot.composite_score,
            json.dumps(snapshot.to_dict()),
        )
    )
    
    # Save readiness scores
    for score in readiness_scores:
        cursor.execute(
            "INSERT INTO eval_readiness (run_id, problem_id, score, json_data) VALUES (?, ?, ?, ?)",
            (
                snapshot.run_id,
                score.problem_id,
                score.score,
                json.dumps(score.to_dict()),
            )
        )

    # Save benchmark case results if provided
    if benchmark_results:
        for res in benchmark_results:
            cursor.execute(
                "INSERT INTO eval_results (run_id, case_id, score, passed, time_ms, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    snapshot.run_id,
                    res.case_id,
                    res.score,
                    1 if res.passed else 0,
                    res.time_ms,
                    getattr(res, "notes", ""),
                )
            )
        
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="AXIOM Scientific Capability Evaluation Suite")
    parser.add_argument("--db", type=str, default="axiom.db", help="Path to SQLite database")
    parser.add_argument("--compare-previous", action="store_true", help="Compare current run to the previous database run")
    args = parser.parse_args()

    print("======================================================================")
    print("  Running AXIOM Scientific Capability Benchmarks...")
    print("======================================================================")
    
    init_db(args.db)
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    wall_start = time.perf_counter()
    
    # Run the 8 benchmark suites
    print("\n[1/8] Executing Mathematical Reasoning benchmarks...")
    mr_results, mr_score = run_math_reasoning_benchmarks()
    print(f"      Passed {sum(1 for r in mr_results if r.passed)}/{len(mr_results)} - Score: {mr_score:.4f}")
    
    print("\n[2/8] Executing Proof Verification benchmarks...")
    pv_results, pv_score = run_proof_verification_benchmarks()
    print(f"      Passed {sum(1 for r in pv_results if r.passed)}/{len(pv_results)} - Score: {pv_score:.4f}")
    
    print("\n[3/8] Executing Conjecture Generation benchmarks...")
    cg_results, cg_score = run_conjecture_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in cg_results if r.passed)}/{len(cg_results)} - Score: {cg_score:.4f}")
    
    print("\n[4/8] Executing Knowledge Quality benchmarks...")
    kq_results, kq_score = run_knowledge_quality_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in kq_results if r.passed)}/{len(kq_results)} - Score: {kq_score:.4f}")
    
    print("\n[5/8] Executing Counterexample Search benchmarks...")
    ce_results, ce_score = run_counterexample_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in ce_results if r.passed)}/{len(ce_results)} - Score: {ce_score:.4f}")

    print("\n[6/8] Executing Research Planning benchmarks...")
    rp_results, rp_score = run_research_planning_benchmarks()
    print(f"      Passed {sum(1 for r in rp_results if r.passed)}/{len(rp_results)} - Score: {rp_score:.4f}")

    print("\n[7/8] Executing Literature Synthesis benchmarks...")
    ls_results, ls_score = run_literature_synthesis_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in ls_results if r.passed)}/{len(ls_results)} - Score: {ls_score:.4f}")

    print("\n[8/8] Executing Research Productivity benchmarks...")
    rd_results, rd_score = run_research_productivity_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in rd_results if r.passed)}/{len(rd_results)} - Score: {rd_score:.4f}")

    # Build Snapshot
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
    
    # Check for previous run to compare
    prev_run, prev_readiness = get_latest_run(args.db)
    
    # Save current run with benchmark results
    all_results = mr_results + pv_results + cg_results + kq_results + ce_results + rp_results + ls_results + rd_results
    save_run(args.db, snapshot, readiness_scores, all_results)
    duration_ms = (time.perf_counter() - wall_start) * 1000
    record_scep_run(
        args.db,
        snapshot,
        all_results,
        started_at=started_at,
        duration_ms=duration_ms,
        trigger="cli",
    )
    print(f"\n✓ Saved run snapshot {run_id} in {args.db} (Composite Score: {snapshot.composite_score:.4f})")
    
    # Generate delta report
    report = generate_delta_report(
        epic_name="EPIC-002",
        prev_snapshot=prev_run,
        curr_snapshot=snapshot,
        prev_readiness=prev_readiness,
        curr_readiness=readiness_scores
    )
    
    # Output delta report to stdout
    print("\n======================================================================")
    print(report.to_markdown())
    print("======================================================================")
    
    # Save report files
    os.makedirs("docs", exist_ok=True)
    report_md_path = f"docs/capability_delta_{run_id}.md"
    with open(report_md_path, "w") as f:
        f.write(report.to_markdown())
        
    with open("benchmark_results.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2)
        
    print(f"✓ Wrote Markdown report to: {report_md_path}")
    print(f"✓ Wrote JSON results to: benchmark_results.json")
    
    # If regression check requested
    if args.compare_previous and report.regression_detected:
        print("\n❌ REGRESSION CHECK FAILED! One or more capabilities dropped significantly.")
        for reg in report.regression_details:
            print(f"  - {reg}")
        sys.exit(1)
    
    print("\n🎉 Evaluation run completed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
