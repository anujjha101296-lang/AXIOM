"""Model router — intelligent model/tool selection (SIMR §5, §14)."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from axiom.routing.failure_memory import FailureMemory
from axiom.routing.model_registry import get_fallback_model, get_model, models_for_capability
from axiom.routing.models import ProblemProfile, RoutingDecision, VerificationRequirement
from axiom.routing.profiler import profile_problem
from axiom.routing.strategies import select_strategies
from axiom.routing.tool_registry import get_tool, tools_for_capability


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _model_available(model_id: str) -> bool:
    model = get_model(model_id)
    if not model:
        return False
    if model.availability == "available":
        return True
    if model.provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    if model.provider == "google":
        return bool(os.getenv("GEMINI_API_KEY"))
    return model_id == "mock-model"


def route_task(
    statement: str,
    *,
    profile: ProblemProfile | None = None,
    budget_usd: float | None = None,
    failure_memory: FailureMemory | None = None,
) -> RoutingDecision:
    """Select model, tools, and strategy for a research task."""
    prof = profile or profile_problem(statement)
    strategies = select_strategies(prof)
    strategy = strategies[0]

    primary_cap = prof.required_capabilities[0] if prof.required_capabilities else "research_planning"
    candidates = models_for_capability(primary_cap)

    if failure_memory:
        candidates = failure_memory.filter_models(candidates, primary_cap)

    selected_model = "mock-model"
    for model in candidates:
        if _model_available(model.model_id):
            if budget_usd is not None and model.cost_per_1k_tokens * 10 > budget_usd:
                continue
            selected_model = model.model_id
            break

    if not _model_available(selected_model):
        fallback = get_fallback_model(selected_model)
        selected_model = fallback or "mock-model"

    tools = list(strategy.tools)
    for cap in prof.required_capabilities:
        for tool in tools_for_capability(cap):
            if tool.tool_id not in tools:
                tools.append(tool.tool_id)

    tools = [t for t in tools if get_tool(t) is not None][:8]

    verification_plan = list(strategy.verifiers)
    if prof.verification_requirement == VerificationRequirement.FORMAL:
        verification_plan = list(dict.fromkeys(verification_plan + ["lean_exporter", "smt_gateway"]))
    elif prof.verification_requirement == VerificationRequirement.HUMAN_REVIEW:
        verification_plan.append("human_expert_review")

    requires_human = (
        prof.difficulty.value == "frontier"
        or prof.uncertainty > 0.65
        or prof.verification_requirement == VerificationRequirement.HUMAN_REVIEW
        or prof.safety_risk in ("medium", "high")
    )

    model_spec = get_model(selected_model)
    cost = strategy.estimated_cost
    if model_spec:
        cost += model_spec.cost_per_1k_tokens * 5

    rationale_parts = [
        f"Domain: {prof.domain.value}",
        f"Strategy: {strategy.strategy_type.value}",
        f"Primary capability: {primary_cap}",
        f"Model {selected_model} selected by capability benchmark ranking",
    ]
    if failure_memory and failure_memory.has_recent_failures(selected_model, primary_cap):
        rationale_parts.append("Model penalized for recent failures in this capability")

    return RoutingDecision(
        decision_id=f"rtd_{uuid.uuid4().hex[:12]}",
        problem_id=prof.problem_id,
        created_at=_utc_now(),
        profile=prof.to_dict(),
        selected_model=selected_model,
        selected_tools=tools,
        selected_strategy=strategy.strategy_id,
        rationale="; ".join(rationale_parts),
        verification_plan=verification_plan,
        fallback_model=get_fallback_model(selected_model),
        cost_estimate=round(cost, 4),
        requires_human_review=requires_human,
        model_version=model_spec.version if model_spec else "unknown",
        metadata={
            "strategy_type": strategy.strategy_type.value,
            "strategy_description": strategy.description,
            "alternatives": [s.strategy_id for s in strategies[1:]],
        },
    )
