from __future__ import annotations

import argparse
import json

from .lorenz import run_lorenz_experiment, sweep_rho
from .report import build_lorenz_evidence_bundle, write_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="AXIOM deterministic scientific runtime")
    parser.add_argument("--rho", type=float, default=28.0)
    parser.add_argument("--steps", type=int, default=10000)
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--evidence", action="store_true", help="emit a reproducible evidence bundle")
    parser.add_argument("--json-out", help="write the evidence bundle to this JSON path")
    parser.add_argument("--report-out", help="write the Markdown report to this path")
    args = parser.parse_args()

    if args.evidence:
        bundle = build_lorenz_evidence_bundle(args.rho)
        if args.json_out or args.report_out:
            write_bundle(args.json_out or "axiom_lorenz_evidence.json", args.report_out or "axiom_lorenz_report.md")
        print(json.dumps(bundle.to_dict(), indent=2))
        return

    if args.sweep:
        values = [20.0, 24.0, 28.0, 32.0, 40.0]
        records = sweep_rho(values)
        print(json.dumps([r.to_dict() for r in records], indent=2))
        return

    record, _ = run_lorenz_experiment(args.rho, steps=args.steps)
    print(json.dumps(record.to_dict(), indent=2))


if __name__ == "__main__":
    main()
