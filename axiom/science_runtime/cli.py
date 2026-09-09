from __future__ import annotations

import argparse
import json

from .lorenz import run_lorenz_experiment, sweep_rho


def main() -> None:
    parser = argparse.ArgumentParser(description="AXIOM deterministic scientific runtime")
    parser.add_argument("--rho", type=float, default=28.0)
    parser.add_argument("--steps", type=int, default=10000)
    parser.add_argument("--sweep", action="store_true")
    args = parser.parse_args()

    if args.sweep:
        values = [20.0, 24.0, 28.0, 32.0, 40.0]
        records = sweep_rho(values)
        print(json.dumps([r.to_dict() for r in records], indent=2))
        return

    record, _ = run_lorenz_experiment(args.rho, steps=args.steps)
    print(json.dumps(record.to_dict(), indent=2))


if __name__ == "__main__":
    main()
