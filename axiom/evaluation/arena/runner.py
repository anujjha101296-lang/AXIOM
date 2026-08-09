"""Arena runner — executes versioned suite, persists results, ranks weaknesses."""

from __future__ import annotations

import os
import subprocess
from typing import Any

from axiom.evaluation.arena.models import ArenaRun, _new_id, _utc_now
from axiom.evaluation.arena.readiness import evaluate_readiness
from axiom.evaluation.arena.scoring import aggregate_scores, rank_weaknesses
from axiom.evaluation.arena.store import ArenaStore, compare_runs
from axiom.evaluation.arena.suite_v1 import (
    DATASET_VERSION,
    SUITE_VERSION,
    build_catalog,
    grade_case,
    public_catalog,
)


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=os.environ.get("AXIOM_ROOT", "/workspace"),
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        )
    except Exception:  # noqa: BLE001
        return "unknown"


def run_arena(
    db_path: str,
    *,
    is_baseline: bool = False,
    case_ids: list[str] | None = None,
    environment: str = "local",
    notes: str = "",
) -> dict[str, Any]:
    """Run arena_v1 suite against current AXIOM. Does not fabricate scores."""
    catalog = build_catalog()
    if case_ids:
        wanted = set(case_ids)
        catalog = [c for c in catalog if c.benchmark_id in wanted]

    store = ArenaStore(db_path)
    started = _utc_now()
    run = ArenaRun(
        run_id=_new_id("arena"),
        dataset_version=DATASET_VERSION,
        git_commit=_git_commit(),
        axiom_version=f"arena_suite_{SUITE_VERSION}",
        environment=environment,
        configuration={
            "dataset_version": DATASET_VERSION,
            "suite_version": SUITE_VERSION,
            "case_count": len(catalog),
            "anti_gaming": {
                "ground_truth_not_in_catalog_api": True,
                "held_out_supported": True,
            },
        },
        started_at=started,
        is_baseline=is_baseline,
        notes=notes,
    )

    ctx = {"db_path": db_path}
    for case in catalog:
        result = grade_case(case, ctx)
        run.results.append(result)
        if not result.passed:
            run.failures.append(result.benchmark_id)

    run.dimension_scores = aggregate_scores(catalog, run.results)
    run.readiness = evaluate_readiness(run.dimension_scores)
    run.weaknesses = rank_weaknesses(catalog, run.results, run.dimension_scores, top_n=3)
    run.ended_at = _utc_now()
    store.save_run(run)

    payload = run.to_dict()
    prev = store.baseline_run() if not is_baseline else None
    if prev is None:
        # compare to previous non-baseline if any
        latest = store.latest_run()
        if latest and latest.get("run_id") != run.run_id:
            prev = latest
    comparison = compare_runs(prev, payload) if prev else None
    return {
        "run": payload,
        "comparison": comparison,
        "catalog_size": len(public_catalog()),
        "dataset_version": DATASET_VERSION,
    }


def get_public_catalog() -> dict[str, Any]:
    cases = public_catalog()
    return {
        "dataset_version": DATASET_VERSION,
        "suite_version": SUITE_VERSION,
        "count": len(cases),
        "benchmarks": cases,
        "ground_truth_exposed": False,
        "tiers": list(range(0, 11)),
        "notes": [
            "Catalog omits ground-truth answers.",
            "Higher tiers require readiness gate evidence.",
        ],
    }
