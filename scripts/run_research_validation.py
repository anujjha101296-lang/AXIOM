#!/usr/bin/env python3
"""
Run AXIOM Research Validation Program batch and generate reports.

Usage:
  python3 scripts/run_research_validation.py
  python3 scripts/run_research_validation.py --stage 1 --limit 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from axiom.config import settings
from axiom.research_validation.dataset import dataset_stats
from axiom.research_validation.engine import ResearchValidationEngine
from axiom.research_validation.reports import write_all_reports


def main() -> int:
    parser = argparse.ArgumentParser(description="AXIOM Research Validation Program")
    parser.add_argument("--stage", type=int, default=0, help="Validation stage (0-6)")
    parser.add_argument("--limit", type=int, default=15, help="Problems per batch")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--db", default=None, help="SQLite database path")
    args = parser.parse_args()

    db_path = args.db or settings.db_path
    engine = ResearchValidationEngine(db_path)

    stats = dataset_stats()
    print(f"Dataset: {stats['total']} known-answer problems")
    print(f"Running stage {args.stage} batch (limit={args.limit})...")

    results = engine.run_stage_batch(stage=args.stage, limit=args.limit, seed=args.seed)
    passed = sum(1 for r in results if r.passed)
    print(f"Completed {len(results)} runs — {passed}/{len(results)} passed")

    if results:
        avg_score = sum(r.answer_score for r in results) / len(results)
        avg_composite = sum(r.capability_score.composite() for r in results) / len(results)
        print(f"Mean answer score: {avg_score:.3f}")
        print(f"Mean capability composite: {avg_composite:.3f}")

    written = write_all_reports(ROOT, db_path)
    print("Reports written:")
    for name, path in written.items():
        print(f"  {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
