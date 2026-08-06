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
    make_dimension_score,
)
from axiom.evaluation.frameworks.prize_readiness import PrizeReadinessEngine
from axiom.evaluation.reporting.delta_report import generate_delta_report
from axiom.evaluation.benchmarks.suite import (
    run_math_reasoning_benchmarks,
    run_proof_verification_benchmarks,
    run_conjecture_benchmarks,
    run_knowledge_quality_benchmarks,
    run_research_planning_benchmarks,
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


def save_run(db_path: str, snapshot: CapabilitySnapshot, readiness_scores: list):
    """Persist the run and readiness results in SQLite."""
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
    
    # Run the 5 benchmark suites
    print("\n[1/5] Executing Mathematical Reasoning benchmarks...")
    mr_results, mr_score = run_math_reasoning_benchmarks()
    print(f"      Passed {sum(1 for r in mr_results if r.passed)}/{len(mr_results)} - Score: {mr_score:.4f}")
    
    print("\n[2/5] Executing Proof Verification benchmarks...")
    pv_results, pv_score = run_proof_verification_benchmarks()
    print(f"      Passed {sum(1 for r in pv_results if r.passed)}/{len(pv_results)} - Score: {pv_score:.4f}")
    
    print("\n[3/5] Executing Conjecture Generation benchmarks...")
    cg_results, cg_score = run_conjecture_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in cg_results if r.passed)}/{len(cg_results)} - Score: {cg_score:.4f}")
    
    print("\n[4/5] Executing Knowledge Quality benchmarks...")
    kq_results, kq_score = run_knowledge_quality_benchmarks(args.db)
    print(f"      Passed {sum(1 for r in kq_results if r.passed)}/{len(kq_results)} - Score: {kq_score:.4f}")
    
    print("\n[5/5] Executing Research Planning benchmarks...")
    rp_results, rp_score = run_research_planning_benchmarks()
    print(f"      Passed {sum(1 for r in rp_results if r.passed)}/{len(rp_results)} - Score: {rp_score:.4f}")
    
    # Other dimensions are estimated or simulated in the absence of more complex tools
    ce_score = 0.35  # Counterexample: basic SMT sweep
    ls_score = 0.40  # Literature: arXiv parsing
    rd_score = 0.50  # Productivity: autonomous loop iterations
    
    # Build Snapshot
    run_id = str(uuid.uuid4())[:8]
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    snapshot = CapabilitySnapshot(run_id=run_id, timestamp=timestamp)
    snapshot.dimension_scores = [
        make_dimension_score(CapabilityDimension.MATHEMATICAL_REASONING, mr_score, len(mr_results)),
        make_dimension_score(CapabilityDimension.PROOF_VERIFICATION, pv_score, len(pv_results)),
        make_dimension_score(CapabilityDimension.CONJECTURE_GENERATION, cg_score, len(cg_results)),
        make_dimension_score(CapabilityDimension.KNOWLEDGE_QUALITY, kq_score, len(kq_results)),
        make_dimension_score(CapabilityDimension.COUNTEREXAMPLE_SEARCH, ce_score, 5, estimated=True),
        make_dimension_score(CapabilityDimension.RESEARCH_PLANNING, rp_score, len(rp_results)),
        make_dimension_score(CapabilityDimension.LITERATURE_SYNTHESIS, ls_score, 10, estimated=True),
        make_dimension_score(CapabilityDimension.RESEARCH_PRODUCTIVITY, rd_score, 3, estimated=True),
    ]
    snapshot.compute_composite()
    
    # Compute Prize Readiness
    scores_map = {s.dimension.value: s.raw_score for s in snapshot.dimension_scores}
    engine = PrizeReadinessEngine()
    readiness_scores = engine.compute_all(scores_map)
    
    # Check for previous run to compare
    prev_run, prev_readiness = get_latest_run(args.db)
    
    # Save current run
    save_run(args.db, snapshot, readiness_scores)
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
