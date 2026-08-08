"""AXIOM Research Kernel API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.research_kernel.engine import KernelStageIncompleteError, ResearchKernel
from axiom.research_kernel.models import STAGE_ORDER, KernelStage
from axiom.research_kernel.registry import get_plugin, kernel_manifest, list_plugins

router = APIRouter(prefix="/kernel", tags=["research-kernel"])


class CreateRunRequest(BaseModel):
    objective: str
    plugin_id: str
    context: dict[str, Any] = Field(default_factory=dict)


class ExecuteStageRequest(BaseModel):
    stage: KernelStage | None = None


def _engine() -> ResearchKernel:
    return ResearchKernel(settings.db_path)


@router.get("/manifest")
def get_manifest() -> dict[str, Any]:
    """Return kernel architecture manifest — stages, plugins, integrations."""
    return kernel_manifest()


@router.get("/stages")
def list_stages() -> list[dict[str, Any]]:
    return [
        {"order": i + 1, "stage": s.value, "name": s.name}
        for i, s in enumerate(STAGE_ORDER)
    ]


@router.get("/plugins")
def get_plugins() -> dict[str, Any]:
    plugins = list_plugins()
    return {"count": len(plugins), "plugins": [p.model_dump() for p in plugins]}


@router.get("/plugins/{plugin_id}")
def get_plugin_detail(plugin_id: str) -> dict[str, Any]:
    try:
        plugin = get_plugin(plugin_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "plugin_id": plugin.plugin_id,
        "domain": plugin.domain,
        "name": plugin.name,
        "version": plugin.version,
        "description": plugin.description,
        "benchmarks": plugin.benchmarks(),
    }


@router.post("/runs", status_code=201)
def create_run(body: CreateRunRequest) -> dict[str, Any]:
    try:
        run = _engine().create_run(
            objective=body.objective,
            plugin_id=body.plugin_id,
            context=body.context,
        )
        return run.model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/runs")
def list_runs(limit: int = 50, domain: str | None = None) -> dict[str, Any]:
    runs = _engine().store.list_runs(limit=limit, domain=domain)
    return {"count": len(runs), "runs": [r.model_dump(mode="json") for r in runs]}


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    run = _engine().get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Kernel run not found")
    return run.model_dump(mode="json")


@router.post("/runs/{run_id}/stages")
def execute_stage(run_id: str, body: ExecuteStageRequest | None = None) -> dict[str, Any]:
    try:
        run = _engine().execute_stage(run_id, body.stage if body else None)
        return run.model_dump(mode="json")
    except KernelStageIncompleteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/runs/{run_id}/run")
def run_full_cycle(run_id: str) -> dict[str, Any]:
    try:
        run = _engine().run_full_cycle(run_id)
        return run.model_dump(mode="json")
    except KernelStageIncompleteError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/runs/{run_id}/report")
def get_report(run_id: str) -> dict[str, Any]:
    run = _engine().get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Kernel run not found")
    if not run.report:
        raise HTTPException(status_code=404, detail="Report not generated. Run full cycle first.")
    return {"run_id": run_id, "report": run.report}
