"""Research planning and strategy generation (FRCE §4, §7)."""

from __future__ import annotations

from typing import Any

from axiom.campaign.graph import decompose_problem, find_bottleneck
from axiom.campaign.models import (
    CampaignPhase,
    FrontierCampaign,
    ResearchStrategy,
    _new_id,
)
from axiom.routing.compiler import compile_research_plan


def scope_campaign(campaign: FrontierCampaign) -> FrontierCampaign:
    """Define problem scope, build knowledge base skeleton, decompose (FRCE §1)."""
    decompose_problem(campaign)
    campaign.phase = CampaignPhase.SCOPED
    campaign.journal.append({
        "title": "Campaign scoped",
        "content": f"Decomposed into {len(campaign.research_graph)} graph nodes",
        "phase": "scoping",
    })
    return campaign


def generate_strategies(campaign: FrontierCampaign, *, max_strategies: int = 5) -> list[ResearchStrategy]:
    """Generate competing research strategies using SIMR compiler (FRCE §7)."""
    statement = campaign.objective
    if campaign.problem_definition:
        statement = f"{campaign.objective}. {campaign.problem_definition}"

    plan = compile_research_plan(statement)
    campaign.routing_plan_id = plan.problem_id
    campaign.context["routing_plan"] = plan.to_dict()

    strategies: list[ResearchStrategy] = []
    bottleneck = find_bottleneck(campaign)

    for i, step in enumerate(plan.execution_steps[:max_strategies]):
        if step.get("action") in ("verify", "human_expert_review"):
            continue
        strategy = ResearchStrategy(
            strategy_id=_new_id("strat"),
            name=step.get("strategy_id", f"strategy_{i + 1}"),
            description=f"Strategy via {step.get('strategy_type', 'general')}",
            probability_of_progress=0.1 + 0.15 * (max_strategies - i),
            estimated_cost=float(step.get("estimated_minutes", 30)) / 10.0,
            estimated_runtime_minutes=float(step.get("estimated_minutes", 30)),
            discrimination_score=0.5,
            execution_plan=step,
            linked_node_ids=[bottleneck.node_id] if bottleneck else [],
        )
        strategies.append(strategy)

    if not strategies:
        strategies.append(ResearchStrategy(
            strategy_id=_new_id("strat"),
            name="direct_investigation",
            description="Direct investigation of main problem",
            probability_of_progress=0.3,
            estimated_cost=5.0,
            execution_plan={"action": "investigate", "target": campaign.objective},
        ))

    campaign.strategies = strategies
    campaign.phase = CampaignPhase.RESEARCHING
    return strategies


def plan_hypotheses(campaign: FrontierCampaign, statements: list[str] | None = None) -> FrontierCampaign:
    """Generate hypotheses from open graph nodes."""
    from axiom.campaign.models import CampaignHypothesis

    if statements:
        for stmt in statements:
            campaign.hypotheses.append(CampaignHypothesis(
                hypothesis_id=_new_id("hyp"),
                statement=stmt,
            ))
    else:
        open_nodes = [n for n in campaign.research_graph if n.status.value in ("open", "unknown")]
        for node in open_nodes[:3]:
            campaign.hypotheses.append(CampaignHypothesis(
                hypothesis_id=_new_id("hyp"),
                statement=f"Hypothesis: {node.title} is tractable with current methods",
            ))

    campaign.phase = CampaignPhase.HYPOTHESIS_GENERATION
    return campaign
