"""Bridge structured AI plans into the deterministic research loop.

The bridge deliberately translates only parameters that the current Lorenz
execution runtime can faithfully consume. Provider output never gets to select
arbitrary tools or executable code.
"""
from __future__ import annotations

from .agent_protocol import ScientificPlan
from .llm_planners import validate_scientific_plan
from .research_loop import ExperimentPlan, Hypothesis, ResearchQuestion


_DEFAULT_SIGMA = 10.0
_DEFAULT_BETA = 8.0 / 3.0


def scientific_plan_to_research_planner(plan: ScientificPlan):
    """Return a bounded planner compatible with ``run_research``.

    The current evidence runtime exposes rho, dt, and horizon as experiment
    controls. Sigma and beta remain fixed at the validated Lorenz defaults until
    the evidence pipeline is extended to carry them end-to-end. Rejecting a
    provider plan here is safer than silently executing different parameters.
    """
    plan = validate_scientific_plan(plan)
    sigma = float(plan.parameters.get("sigma", _DEFAULT_SIGMA))
    beta = float(plan.parameters.get("beta", _DEFAULT_BETA))
    if sigma != _DEFAULT_SIGMA or beta != _DEFAULT_BETA:
        raise ValueError(
            "the current Lorenz evidence pipeline only supports sigma=10 and beta=8/3"
        )

    rho = float(plan.parameters["rho"])
    dt = float(plan.parameters.get("dt", 0.01))
    horizon = float(plan.parameters.get("horizon", 2.0))
    # Keep the convergence ladder bounded around the planner-selected timestep.
    dts = tuple(sorted({dt * 2.0, dt, dt / 2.0}, reverse=True))
    if dts[-1] < 0.0001 or dts[0] > 0.1:
        raise ValueError("planner timestep cannot form a safe convergence ladder")

    hypothesis = Hypothesis(statement=plan.hypothesis, rationale=plan.rationale)
    experiment = ExperimentPlan(rho=rho, horizon=horizon, dts=dts)

    def planner(question: ResearchQuestion):
        if question.model.lower() != "lorenz":
            raise ValueError(f"Unsupported model: {question.model}")
        if rho not in question.allowed_rho:
            raise ValueError("planner rho is outside the research question allowlist")
        return hypothesis, experiment

    return planner
