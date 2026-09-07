#!/usr/bin/env python3
"""
Run AXIOM Engineering Governance review cycle.

Generates:
  - ENGINEERING_HEALTH.md
  - PRODUCT_HEALTH.md
  - RESEARCH_HEALTH.md
  - TECH_DEBT_BOARD.md
  - TOP_25_PRIORITIES.md
  - .axiom/governance/dashboard.json

Usage:
  python3 scripts/run_engineering_review.py
  python3 scripts/run_engineering_review.py --update-baseline
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from axiom.governance.review import EngineeringReview  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AXIOM engineering governance review")
    parser.add_argument(
        "--workspace",
        default=str(ROOT),
        help="Repository root (default: workspace root)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update performance import baseline after review",
    )
    parser.add_argument(
        "--scores-only",
        action="store_true",
        help="Print scores JSON to stdout without writing reports",
    )
    args = parser.parse_args()

    review = EngineeringReview(args.workspace)
    if args.scores_only:
        snapshot = review.run(update_baseline=args.update_baseline)
        import json

        print(json.dumps(snapshot.scores.as_dict(), indent=2))
        return 0

    snapshot = review.run_and_write(update_baseline=args.update_baseline)
    print(f"Engineering review complete at {snapshot.timestamp}")
    print("Scores:", snapshot.scores.as_dict())
    print("Reports written to repository root and .axiom/governance/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
