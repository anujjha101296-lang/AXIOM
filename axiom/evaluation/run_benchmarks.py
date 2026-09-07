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

from axiom.evaluation.frameworks.evidence import run_all_capability_benchmarks
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.reporting.delta_report import generate_delta_report


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

    bundle = run_all_capability_benchmarks(args.db)
    snapshot = bundle.snapshot
    run_id = snapshot.run_id

    print("\n======================================================================")
    print("  Benchmark suite complete (S0-E4 evidence-gated)")
    print("======================================================================")
    for score in snapshot.dimension_scores:
        print(
            f"  {score.dimension.value}: score={score.raw_score:.4f} "
            f"evidence={score.evidence_state.value} cases={score.benchmark_count}"
        )

    engine = PrizeReadinessEngine()
    readiness_scores = engine.compute_all(bundle.scores_map)

    prev_run, prev_readiness = get_latest_run(args.db)

    save_run(args.db, snapshot, readiness_scores, bundle.all_results)
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
