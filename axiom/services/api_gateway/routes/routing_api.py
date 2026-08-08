"""SIMR Loop — Scientific Intelligence & Model Routing API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.routing.compiler import compile_research_plan
from axiom.routing.failure_memory import get_failure_memory
from axiom.routing.model_registry import get_model, list_models
from axiom.routing.profiler import profile_problem
from axiom.routing.selector import route_task
from axiom.routing.store import get_routing_store
from axiom.routing.strategies import generate_strategies, select_strategies
from axiom.routing.tool_registry import get_tool, list_tools
from axiom.security.deps import routing_route_auth

router = APIRouter(
    prefix="/routing",
    tags=["routing"],
    dependencies=[Depends(routing_route_auth)],
)


class RouteRequest(BaseModel):
    statement: str
    budget_usd: float | None = None
    required_capabilities: list[str] = Field(default_factory=list)
    persist: bool = True


class ProfileRequest(BaseModel):
    statement: str
    required_capabilities: list[str] = Field(default_factory=list)


class CompileRequest(BaseModel):
    statement: str


class RecordFailureRequest(BaseModel):
    model_id: str
    failure_type: str
    description: str
    problem_domain: str = "unknown"
    capability: str | None = None
    severity: str = "medium"


class RecordConflictRequest(BaseModel):
    source_a: str
    source_b: str
    claim_a: str
    claim_b: str
    confidence_a: float = 0.5
    confidence_b: float = 0.5


class RecordCostRequest(BaseModel):
    decision_id: str | None = None
    campaign_id: str | None = None
    tokens: int = 0
    model_calls: int = 0
    tool_calls: int = 0
    compute_seconds: float = 0.0
    estimated_usd: float = 0.0


@router.get("/models")
def get_models() -> dict[str, Any]:
    models = list_models()
    return {"count": len(models), "models": [m.to_dict() for m in models]}


@router.get("/models/{model_id}")
def get_model_detail(model_id: str) -> dict[str, Any]:
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
    return model.to_dict()


@router.get("/tools")
def get_tools() -> dict[str, Any]:
    tools = list_tools()
    return {"count": len(tools), "tools": [t.to_dict() for t in tools]}


@router.get("/tools/{tool_id}")
def get_tool_detail(tool_id: str) -> dict[str, Any]:
    tool = get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}")
    return tool.to_dict()


@router.post("/profile")
def profile_research_problem(body: ProfileRequest) -> dict[str, Any]:
    profile = profile_problem(
        body.statement,
        required_capabilities=body.required_capabilities or None,
    )
    return profile.to_dict()


@router.post("/select")
def select_routing(body: RouteRequest) -> dict[str, Any]:
    profile = profile_problem(
        body.statement,
        required_capabilities=body.required_capabilities or None,
    )
    memory = get_failure_memory(settings.db_path)
    decision = route_task(
        body.statement,
        profile=profile,
        budget_usd=body.budget_usd,
        failure_memory=memory,
    )
    if body.persist:
        get_routing_store(settings.db_path).save_decision(decision)
    return decision.to_dict()


@router.post("/compile")
def compile_plan(body: CompileRequest) -> dict[str, Any]:
    plan = compile_research_plan(body.statement)
    return plan.to_dict()


@router.get("/strategies")
def list_strategies(statement: str) -> dict[str, Any]:
    profile = profile_problem(statement)
    strategies = generate_strategies(profile)
    selected = select_strategies(profile)
    return {
        "problem_id": profile.problem_id,
        "candidates": [s.to_dict() for s in strategies],
        "selected": [s.to_dict() for s in selected],
    }


@router.get("/decisions")
def list_routing_decisions(limit: int = 50) -> dict[str, Any]:
    decisions = get_routing_store(settings.db_path).list_decisions(limit=limit)
    return {"count": len(decisions), "decisions": [d.to_dict() for d in decisions]}


@router.get("/decisions/{decision_id}")
def get_routing_decision(decision_id: str) -> dict[str, Any]:
    decision = get_routing_store(settings.db_path).get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision not found: {decision_id}")
    return decision.to_dict()


@router.get("/dashboard")
def routing_dashboard() -> dict[str, Any]:
    store = get_routing_store(settings.db_path)
    memory = get_failure_memory(settings.db_path)
    return {
        **store.dashboard_stats(),
        "model_count": len(list_models()),
        "tool_count": len(list_tools()),
        "recent_failures": len(memory.list_failures(limit=10)),
    }


@router.post("/failures")
def record_model_failure(body: RecordFailureRequest) -> dict[str, Any]:
    record = get_failure_memory(settings.db_path).record_failure(
        body.model_id,
        body.failure_type,
        body.description,
        problem_domain=body.problem_domain,
        capability=body.capability,
        severity=body.severity,
    )
    return record.to_dict()


@router.get("/failures")
def list_model_failures(model_id: str | None = None, limit: int = 50) -> dict[str, Any]:
    failures = get_failure_memory(settings.db_path).list_failures(model_id=model_id, limit=limit)
    return {"count": len(failures), "failures": [f.to_dict() for f in failures]}


@router.post("/conflicts")
def record_knowledge_conflict(body: RecordConflictRequest) -> dict[str, Any]:
    return get_failure_memory(settings.db_path).record_conflict(
        body.source_a,
        body.source_b,
        body.claim_a,
        body.claim_b,
        confidence_a=body.confidence_a,
        confidence_b=body.confidence_b,
    )


@router.post("/costs")
def record_research_cost(body: RecordCostRequest) -> dict[str, Any]:
    return get_routing_store(settings.db_path).record_cost(
        decision_id=body.decision_id,
        campaign_id=body.campaign_id,
        tokens=body.tokens,
        model_calls=body.model_calls,
        tool_calls=body.tool_calls,
        compute_seconds=body.compute_seconds,
        estimated_usd=body.estimated_usd,
    )
