from __future__ import annotations

from .agent_protocol import ScientificPlan

ALLOWED_RHO = frozenset({20.0, 24.0, 28.0, 32.0, 40.0})


def validate_plan(plan: ScientificPlan) -> ScientificPlan:
    if set(plan.parameters) != {"rho", "sigma", "beta", "dt", "horizon"}:
        raise ValueError("invalid scientific plan parameters")
    if float(plan.parameters["rho"]) not in ALLOWED_RHO:
        raise ValueError("rho outside allowlist")
    if float(plan.parameters["sigma"]) != 10.0:
        raise ValueError("sigma outside contract")
    if float(plan.parameters["beta"]) != 8.0 / 3.0:
        raise ValueError("beta outside contract")
    if not 0.0005 <= float(plan.parameters["dt"]) <= 0.05:
        raise ValueError("dt outside contract")
    if not 0.1 <= float(plan.parameters["horizon"]) <= 10.0:
        raise ValueError("horizon outside contract")
    return plan
