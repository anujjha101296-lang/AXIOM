"""Arena runner — executes versioned suite, persists results, ranks weaknesses."""

from __future__ import annotations

import os
import subprocess
from typing import Any

from axiom.evaluation.arena.models import ArenaRun, _new_id, _utc_now
from axiom.evaluation.arena.readiness import evaluate_readiness
from axiom.evaluation.arena.scoring import aggregate_scores, rank_weaknesses
from axiom.evaluation.arena.store import ArenaStore, compare_runs
from axiom.evaluation.arena.suite_ext_sec_lh import (
    DATASET_VERSION as EXT_DATASET,
    build_extension_catalog,
    grade_extension_case,
    public_extension_catalog,
)
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
    include_extension: bool = False,
) -> dict[str, Any]:
    """Run arena suite against current AXIOM. Does not fabricate scores.

    include_extension=True adds arena_ext_sec_lh_v1 (security + long-horizon).
    """
    catalog = build_catalog()
    dataset = DATASET_VERSION
    if include_extension:
        catalog = catalog + build_extension_catalog()
        dataset = f"{DATASET_VERSION}+{EXT_DATASET}"
    if case_ids:
        wanted = set(case_ids)
        catalog = [c for c in catalog if c.benchmark_id in wanted]

    store = ArenaStore(db_path)
    started = _utc_now()
    run = ArenaRun(
        run_id=_new_id("arena"),
        dataset_version=dataset,
        git_commit=_git_commit(),
        axiom_version=f"arena_suite_{SUITE_VERSION}",
        environment=environment,
        configuration={
            "dataset_version": dataset,
            "suite_version": SUITE_VERSION,
            "case_count": len(catalog),
            "include_extension": include_extension,
            "anti_gaming": {
                "ground_truth_not_in_catalog_api": True,
                "held_out_supported": True,
                "arena_v1_immutable": True,
            },
        },
        started_at=started,
        is_baseline=is_baseline,
        notes=notes,
    )

    ctx = {"db_path": db_path}
    ext_ids = {c.benchmark_id for c in build_extension_catalog()}
    for case in catalog:
        if case.benchmark_id in ext_ids:
            result = grade_extension_case(case, ctx)
        else:
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
        latest = store.latest_run()
        if latest and latest.get("run_id") != run.run_id:
            prev = latest
    comparison = compare_runs(prev, payload) if prev else None
    return {
        "run": payload,
        "comparison": comparison,
        "catalog_size": len(catalog),
        "dataset_version": dataset,
    }


def get_public_catalog(*, include_extension: bool = False) -> dict[str, Any]:
    cases = public_catalog()
    dataset = DATASET_VERSION
    if include_extension:
        cases = cases + public_extension_catalog()
        dataset = f"{DATASET_VERSION}+{EXT_DATASET}"
    return {
        "dataset_version": dataset,
        "suite_version": SUITE_VERSION,
        "count": len(cases),
        "benchmarks": cases,
        "ground_truth_exposed": False,
        "tiers": list(range(0, 11)),
        "extension_available": EXT_DATASET,
        "notes": [
            "Catalog omits ground-truth answers.",
            "Higher tiers require readiness gate evidence.",
            "arena_v1 is immutable; security/LH cases live in arena_ext_sec_lh_v1.",
        ],
    }
