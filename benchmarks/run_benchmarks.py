#!/usr/bin/env python3
"""
AXIOM Phase 8 — Scientific Evaluation & Benchmarking Platform
Main CLI entry point.

Usage:
  python3 benchmarks/run_benchmarks.py --suite all
  python3 benchmarks/run_benchmarks.py --suite retrieval
  python3 benchmarks/run_benchmarks.py --suite grounding
  python3 benchmarks/run_benchmarks.py --suite agent
  python3 benchmarks/run_benchmarks.py --suite all --save-baseline
  python3 benchmarks/run_benchmarks.py --suite all --compare-baseline

Records for every run:
  - git commit hash and branch
  - timestamp
  - python version
  - benchmark version
  - individual case results
  - aggregate metrics

Results stored in: evaluation_results/<run_id>/
Summary at: evaluation_results/latest_summary.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import platform
import uuid
from datetime import datetime, timezone

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.eval_models import EvaluationRun, EvaluationResult
from benchmarks.retrieval_benchmark import run_retrieval_benchmark
from benchmarks.grounding_benchmark import run_grounding_benchmark
from benchmarks.agent_benchmark import run_agent_benchmark
from benchmarks.regression import (
    compare_runs,
    load_baseline,
    save_baseline,
    print_regression_report,
)
from benchmarks.capability_claims import (
    build_initial_claims,
    update_claims_from_run,
    save_claims,
    print_claims_report,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation_results")


def _git_info() -> tuple[str, str]:
    """Get current git commit hash and branch."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ).decode().strip()
    except Exception:
        commit = "unknown"

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ).decode().strip()
    except Exception:
        branch = "unknown"

    return commit, branch


def _save_run(run: EvaluationRun) -> str:
    """Save run to evaluation_results/<run_id>/results.json and update latest_summary.json."""
    run_dir = os.path.join(RESULTS_DIR, run.run_id)
    os.makedirs(run_dir, exist_ok=True)

    run_path = os.path.join(run_dir, "results.json")
    with open(run_path, "w", encoding="utf-8") as f:
        json.dump(run.to_dict(), f, indent=2)

    # Update latest_summary.json
    summary = {
        "run_id": run.run_id,
        "timestamp": run.timestamp,
        "git_commit": run.git_commit,
        "git_branch": run.git_branch,
        "overall_pass_rate": run.overall_pass_rate,
        "suites": [
            {
                "suite_id": s.suite_id,
                "suite_name": s.suite_name,
                "total_cases": s.total_cases,
                "passed_cases": s.passed_cases,
                "pass_rate": s.pass_rate,
            }
            for s in run.suite_results
        ],
        "results_path": run_path,
    }
    with open(os.path.join(RESULTS_DIR, "latest_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return run_path


def run_suite(suite_name: str) -> list[EvaluationResult]:
    """Run the specified benchmark suite(s)."""
    results = []

    if suite_name in ("retrieval", "all"):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running Retrieval Benchmark...")
        result = run_retrieval_benchmark()
        results.append(result)
        print(f"  → {result.passed_cases}/{result.total_cases} passed | Pass rate: {result.pass_rate:.1%}")

    if suite_name in ("grounding", "all"):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running Grounding & Citation Benchmark...")
        result = run_grounding_benchmark()
        results.append(result)
        print(f"  → {result.passed_cases}/{result.total_cases} passed | Pass rate: {result.pass_rate:.1%}")

    if suite_name in ("agent", "all"):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running Research Agent Benchmark...")
        result = run_agent_benchmark()
        results.append(result)
        print(f"  → {result.passed_cases}/{result.total_cases} passed | Pass rate: {result.pass_rate:.1%}")

    return results


def print_summary(run: EvaluationRun) -> None:
    """Print a clean summary of the run."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Run ID:     {run.run_id}")
    print(f"Timestamp:  {run.timestamp}")
    print(f"Git Commit: {run.git_commit} ({run.git_branch})")
    print(f"\nSuite Results:")
    for suite in run.suite_results:
        icon = "✓" if suite.pass_rate >= 0.6 else "✗"
        print(f"  {icon} {suite.suite_name}: {suite.passed_cases}/{suite.total_cases} ({suite.pass_rate:.1%})")
        for m in suite.aggregate_metrics:
            status = "✓" if (m.passed is None or m.passed) else "✗"
            print(f"      {status} {m.name}: {m.value:.4f}")

    print(f"\nOverall Pass Rate: {run.overall_pass_rate:.1%}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="AXIOM Phase 8 — Scientific Evaluation & Benchmarking Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all benchmarks
  python3 benchmarks/run_benchmarks.py --suite all

  # Run only retrieval benchmark  
  python3 benchmarks/run_benchmarks.py --suite retrieval

  # Establish baseline for regression testing
  python3 benchmarks/run_benchmarks.py --suite all --save-baseline

  # Compare against baseline
  python3 benchmarks/run_benchmarks.py --suite all --compare-baseline

  # Fail pipeline if regression detected
  python3 benchmarks/run_benchmarks.py --suite all --compare-baseline --fail-on-regression
        """,
    )
    parser.add_argument(
        "--suite",
        choices=["retrieval", "grounding", "agent", "all"],
        default="all",
        help="Which benchmark suite to run (default: all)",
    )
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Save this run as the regression baseline",
    )
    parser.add_argument(
        "--compare-baseline",
        action="store_true",
        help="Compare results against stored baseline",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with code 1 if regression is detected",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.05,
        help="Regression tolerance (default: 0.05 = 5%%)",
    )
    parser.add_argument(
        "--show-claims",
        action="store_true",
        help="Show capability claims after benchmarks",
    )

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"AXIOM Scientific Evaluation & Benchmarking Platform")
    print(f"Phase 8 — Benchmark Run")
    print(f"{'='*60}")

    git_commit, git_branch = _git_info()
    print(f"Git: {git_commit} ({git_branch})")
    print(f"Python: {platform.python_version()}")

    # Run benchmarks
    start_time = time.time()
    suite_results = run_suite(args.suite)

    # Build run record
    run = EvaluationRun(
        git_commit=git_commit,
        git_branch=git_branch,
        python_version=platform.python_version(),
        benchmark_version="1.0",
        configuration={
            "suite": args.suite,
            "tolerance": args.tolerance,
        },
        suite_results=suite_results,
    )

    # Save run
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_path = _save_run(run)
    print(f"\n✓ Results saved to: {run_path}")

    # Update capability claims
    claims = build_initial_claims()
    claims = update_claims_from_run(claims, run.to_dict())
    save_claims(claims)

    if args.show_claims:
        print_claims_report(claims)

    # Print summary
    print_summary(run)

    # Regression comparison
    if args.compare_baseline or args.save_baseline:
        baseline_data = load_baseline()

        if args.compare_baseline and baseline_data:
            comparison = compare_runs(run, baseline_data, tolerance=args.tolerance)
            print_regression_report(comparison)

            # Save comparison result
            comparison_path = os.path.join(RESULTS_DIR, run.run_id, "regression.json")
            with open(comparison_path, "w", encoding="utf-8") as f:
                json.dump(comparison.to_dict(), f, indent=2)

            if args.fail_on_regression and comparison.status.value == "REGRESSED":
                print("⛔ PIPELINE FAILURE: Regression detected. Exiting with code 1.")
                sys.exit(1)
        elif args.compare_baseline and not baseline_data:
            print("\nℹ No baseline found. Use --save-baseline to establish one.")

        if args.save_baseline:
            save_baseline(run)

    total_time = time.time() - start_time
    print(f"Total benchmark time: {total_time:.2f}s")

    # Exit with appropriate code
    if run.overall_pass_rate < 0.5:
        print(f"\n⚠ WARNING: Overall pass rate {run.overall_pass_rate:.1%} is below 50%")
        sys.exit(1)

    print("✓ Benchmarks complete.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
