"""Research compiler — problem → execution plan (SIMR §30)."""

from __future__ import annotations

from axiom.routing.capability_graph import resolve_capability_graph
from axiom.routing.models import ProblemProfile, ResearchExecutionPlan
from axiom.routing.profiler import profile_problem
from axiom.routing.selector import route_task
from axiom.routing.strategies import generate_strategies, select_strategies


def compile_research_plan(
    statement: str,
    *,
    profile: ProblemProfile | None = None,
) -> ResearchExecutionPlan:
    """Transform research question into an auditable execution plan."""
    prof = profile or profile_problem(statement)
    graph = resolve_capability_graph(prof)
    strategies = generate_strategies(prof)
    selected = select_strategies(prof)
    decision = route_task(statement, profile=prof)

    execution_steps = []
    for i, strategy in enumerate(selected):
        execution_steps.append({
            "step": i + 1,
            "strategy_id": strategy.strategy_id,
            "strategy_type": strategy.strategy_type.value,
            "models": strategy.models,
            "tools": strategy.tools,
            "verifiers": strategy.verifiers,
            "estimated_minutes": strategy.estimated_minutes,
        })

    execution_steps.append({
        "step": len(execution_steps) + 1,
        "action": "verify",
        "verifiers": decision.verification_plan,
    })
    if decision.requires_human_review:
        execution_steps.append({
            "step": len(execution_steps) + 1,
            "action": "human_expert_review",
            "trigger": "confidence_boundary",
        })

    return ResearchExecutionPlan(
        problem_id=prof.problem_id,
        profile=prof.to_dict(),
        capability_requirements=graph["required_capabilities"],
        strategies=[s.to_dict() for s in strategies],
        selected_strategy=selected[0].to_dict() if selected else {},
        model_graph=graph,
        execution_steps=execution_steps,
        verification_plan=decision.verification_plan,
        cost_estimate=decision.cost_estimate,
        requires_human_review=decision.requires_human_review,
    )
