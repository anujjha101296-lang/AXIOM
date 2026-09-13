"""Bridge typed planning agents into the deterministic research runtime."""
from __future__ import annotations

from .agent_protocol import ScientificPlanner
from .research_loop import ExperimentPlan, Hypothesis, Planner, ResearchQuestion


def as_research_planner(agent: ScientificPlanner) -> Planner:
    """Adapt a typed scientific planner to the existing research-loop contract."""
    def planner(question: ResearchQuestion) -> tuple[Hypothesis, ExperimentPlan]:
        if question.model.lower() != "lorenz":
            raise ValueError(f"Unsupported model: {question.model}")
        proposed = agent.plan(question.text)
        rho = float(proposed.parameters["rho"])
        if rho not in question.allowed_rho:
            raise ValueError(f"Planner proposed rho={rho:g} outside the question allowlist")
        return (
            Hypothesis(statement=proposed.hypothesis, rationale=proposed.rationale),
            ExperimentPlan(rho=rho, horizon=float(proposed.parameters["horizon"])),
        )
    return planner
