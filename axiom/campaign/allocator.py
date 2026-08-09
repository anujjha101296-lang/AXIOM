"""Resource allocation with exploitation + exploration (FRCE §8)."""

from __future__ import annotations

from axiom.campaign.models import FrontierCampaign, ResearchStrategy


def score_strategy(strategy: ResearchStrategy) -> float:
    """Score strategy for resource allocation."""
    if strategy.status != "active":
        return -1.0
    cost = max(strategy.estimated_cost, 0.1)
    return (
        strategy.probability_of_progress * strategy.discrimination_score
    ) / cost


def allocate_resources(
    campaign: FrontierCampaign,
    *,
    max_workers: int = 5,
) -> list[ResearchStrategy]:
    """
    Allocate workers across strategies using exploit/explore split (FRCE §8).

    Does not automatically choose cheapest forever — reserves exploration budget.
    """
    active = [s for s in campaign.strategies if s.status == "active"]
    if not active:
        return []

    explore_frac = campaign.budget.exploration_fraction
    explore_slots = max(1, int(max_workers * explore_frac))
    exploit_slots = max_workers - explore_slots

    ranked = sorted(active, key=score_strategy, reverse=True)
    selected: list[ResearchStrategy] = []

    # Exploitation: top-scoring strategies
    for s in ranked[:exploit_slots]:
        s.workers_allocated = 1
        selected.append(s)

    # Exploration: lower-ranked or diverse strategies
    remaining = [s for s in ranked if s not in selected]
    for s in remaining[:explore_slots]:
        s.workers_allocated = 1
        selected.append(s)

    return selected


def consume_budget(
    campaign: FrontierCampaign,
    *,
    time_seconds: float = 0,
    compute_units: float = 0,
    model_calls: int = 0,
    tool_calls: int = 0,
) -> bool:
    """Consume budget; return False if exceeded (STOP, PRESERVE, REPORT)."""
    c = campaign.budget.consumed
    c["time_seconds"] = c.get("time_seconds", 0) + time_seconds
    c["compute_units"] = c.get("compute_units", 0) + compute_units
    c["model_calls"] = c.get("model_calls", 0) + model_calls
    c["tool_calls"] = c.get("tool_calls", 0) + tool_calls
    return not campaign.budget.budget_exceeded()


def where_next_compute(campaign: FrontierCampaign) -> dict:
    """Answer: where should the next unit of compute go?"""
    allocated = allocate_resources(campaign)
    if not allocated:
        return {"recommendation": "none", "reason": "no active strategies or budget exhausted"}

    top = max(allocated, key=score_strategy)
    return {
        "recommendation": top.strategy_id,
        "strategy_name": top.name,
        "score": round(score_strategy(top), 4),
        "exploration_fraction": campaign.budget.exploration_fraction,
        "budget_remaining": {
            "compute_units": campaign.budget.compute_units - campaign.budget.consumed.get("compute_units", 0),
            "model_calls": campaign.budget.model_calls - campaign.budget.consumed.get("model_calls", 0),
        },
    }
