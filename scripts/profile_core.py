#!/usr/bin/env python3
"""
Profile core AXIOM modules using cProfile.

Usage:
    python scripts/profile_core.py
    python scripts/profile_core.py --module axiom.research.store
"""
from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
from io import StringIO


def profile_imports() -> None:
    """Import hot-path modules to measure cold-start cost."""
    import axiom.config.settings  # noqa: F401
    import axiom.services.api_gateway.main  # noqa: F401
    import axiom.research.store  # noqa: F401
    import axiom.modes  # noqa: F401


def profile_module(dotted_path: str) -> None:
    __import__(dotted_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile AXIOM core modules")
    parser.add_argument(
        "--module",
        default="",
        help="Dotted module path to import (default: standard import bundle)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of lines in profile report",
    )
    args = parser.parse_args()

    profiler = cProfile.Profile()
    profiler.enable()
    if args.module:
        profile_module(args.module)
    else:
        profile_imports()
    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(args.top)
    print(stream.getvalue())
    return 0


if __name__ == "__main__":
    sys.exit(main())
