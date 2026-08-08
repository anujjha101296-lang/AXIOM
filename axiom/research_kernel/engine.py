"""AXIOM Research Kernel — permanent execution engine for research workflows."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from axiom.observability.run_provenance import RunProvenance, capture_environment, get_provenance_store
from axiom.research_kernel.models import STAGE_ORDER, KernelRun, KernelRunStatus, KernelStage
from axiom.research_kernel.pipeline import StageExecutor
from axiom.research_kernel.registry import get_plugin
from axiom.research_kernel.store import KernelStore


class KernelStageIncompleteError(Exception):
    """Raised when a kernel stage cannot be executed or has already completed."""


class ResearchKernel:
    """
    Permanent execution engine for every research workflow.
    Orchestrates ACA, SME, workflow, and domain plugins without duplicating logic.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = KernelStore(db_path)
        self.executor = StageExecutor(db_path)

    def create_run(
        self,
        objective: str,
        plugin_id: str,
        context: dict[str, Any] | None = None,
    ) -> KernelRun:
        plugin = get_plugin(plugin_id)
        run = KernelRun(
            objective=objective,
            domain=plugin.domain,
            plugin_id=plugin_id,
            status=KernelRunStatus.IN_PROGRESS,
            context=context or {},
        )
        self.store.save(run)
        return run

    def get_run(self, run_id: str) -> KernelRun | None:
        return self.store.get(run_id)

    def execute_stage(self, run_id: str, stage: KernelStage | None = None) -> KernelRun:
        run = self._load(run_id)
        plugin = get_plugin(run.plugin_id)
        target = stage or run.current_stage

        if target in run.stages_completed:
            raise KernelStageIncompleteError(f"Stage {target.value} already completed.")

        idx = STAGE_ORDER.index(target)
        if idx > 0 and STAGE_ORDER[idx - 1] not in run.stages_completed:
            raise KernelStageIncompleteError(
                f"Cannot execute {target.value}: prior stage {STAGE_ORDER[idx - 1].value} not completed."
            )

        result = self.executor.execute(run, target, plugin)
        run.stage_outputs.append(result)

        if not result.completed:
            run.status = KernelRunStatus.FAILED
            self.store.save(run)
            raise KernelStageIncompleteError(
                f"Stage {target.value} failed: {'; '.join(result.errors)}"
            )

        run.stages_completed.append(target)
        next_idx = idx + 1
        if next_idx < len(STAGE_ORDER):
            run.current_stage = STAGE_ORDER[next_idx]
        else:
            run.status = KernelRunStatus.COMPLETED
            run.current_stage = target
            self._record_provenance(run)

        run.updated_at = datetime.now(timezone.utc)
        self.store.save(run)
        return run

    def run_full_cycle(self, run_id: str) -> KernelRun:
        run = self._load(run_id)
        started = time.perf_counter()

        for stage in STAGE_ORDER:
            if stage not in run.stages_completed:
                run = self.execute_stage(run_id, stage)

        run.context["total_duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
        run.status = KernelRunStatus.COMPLETED
        # Refresh report with final status and all stage checkmarks
        if run.report:
            from axiom.research_kernel.reports import generate_kernel_report
            run.report = generate_kernel_report(run, get_plugin(run.plugin_id))
        self.store.save(run)
        return run

    def _load(self, run_id: str) -> KernelRun:
        run = self.store.get(run_id)
        if not run:
            raise ValueError(f"Kernel run not found: {run_id}")
        return run

    def _record_provenance(self, run: KernelRun) -> None:
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        record = RunProvenance(
            run_id=run.run_id,
            run_type="kernel",
            started_at=run.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            finished_at=finished,
            duration_ms=run.context.get("total_duration_ms", 0.0),
            config_hash=None,
            inputs={"objective": run.objective, "domain": run.domain, "plugin_id": run.plugin_id},
            environment=capture_environment(),
            evidence_tier={
                "rollup": run.context.get("evidence", {}).get("evidence_tier", "simulated"),
                "benchmarks_passed": sum(1 for b in run.benchmark_results if b.get("passed")),
            },
            runtime={
                "stages_completed": len(run.stages_completed),
                "aca_cycle_id": run.aca_cycle_id,
                "sme_session_id": run.sme_session_id,
            },
        )
        get_provenance_store(self.db_path).save(record)
