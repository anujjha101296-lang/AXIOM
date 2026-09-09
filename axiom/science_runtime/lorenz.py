from __future__ import annotations

import hashlib
import math
import uuid
from typing import Callable

from .models import ExperimentRecord, LorenzResult

State = tuple[float, float, float]


def _rhs(state: State, sigma: float, rho: float, beta: float) -> State:
    x, y, z = state
    return (sigma * (y - x), x * (rho - z) - y, x * y - beta * z)


def _rk4_step(state: State, dt: float, rhs: Callable[[State], State]) -> State:
    k1 = rhs(state)
    k2 = rhs(tuple(a + dt * b / 2 for a, b in zip(state, k1)))
    k3 = rhs(tuple(a + dt * b / 2 for a, b in zip(state, k2)))
    k4 = rhs(tuple(a + dt * b for a, b in zip(state, k3)))
    return tuple(a + dt * (b1 + 2*b2 + 2*b3 + b4) / 6 for a, b1, b2, b3, b4 in zip(state, k1, k2, k3, k4))  # type: ignore[return-value]


def simulate_lorenz(
    rho: float,
    *,
    sigma: float = 10.0,
    beta: float = 8.0 / 3.0,
    dt: float = 0.01,
    steps: int = 10000,
    initial_state: State = (1.0, 1.0, 1.0),
) -> list[State]:
    if dt <= 0 or steps <= 0:
        raise ValueError("dt and steps must be positive")
    trajectory = [initial_state]
    rhs = lambda s: _rhs(s, sigma, rho, beta)
    state = initial_state
    for _ in range(steps):
        state = _rk4_step(state, dt, rhs)
        if not all(math.isfinite(v) for v in state):
            raise FloatingPointError("Lorenz integration diverged to a non-finite state")
        trajectory.append(state)
    return trajectory


def _distance(a: State, b: State) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def run_lorenz_experiment(
    rho: float,
    *,
    dt: float = 0.01,
    steps: int = 10000,
    perturbation: float = 1e-9,
) -> tuple[ExperimentRecord, list[State]]:
    """Run a deterministic two-trajectory sensitivity experiment.

    This is an evidence-producing numerical experiment, not a mathematical proof
    of chaos. The evidence tier is deliberately marked NUMERICAL_OBSERVATION.
    """
    base = (1.0, 1.0, 1.0)
    perturbed = (1.0 + perturbation, 1.0, 1.0)
    trajectory = simulate_lorenz(rho, dt=dt, steps=steps, initial_state=base)
    second = simulate_lorenz(rho, dt=dt, steps=steps, initial_state=perturbed)
    final_distance = _distance(trajectory[-1], second[-1])
    xs = [abs(s[0]) for s in trajectory]
    payload = f"lorenz|{rho}|{dt}|{steps}|{perturbation}".encode()
    experiment_id = "lorenz-" + hashlib.sha256(payload).hexdigest()[:16]
    result = LorenzResult(
        sigma=10.0,
        rho=rho,
        beta=8.0 / 3.0,
        dt=dt,
        steps=steps,
        initial_state=base,
        final_state=trajectory[-1],
        mean_abs_x=sum(xs) / len(xs),
        max_abs_x=max(xs),
        divergence_indicator=final_distance,
    )
    record = ExperimentRecord(
        experiment_id=experiment_id,
        question="When does small initial-condition uncertainty amplify in the Lorenz system?",
        hypothesis=f"For rho={rho:g}, nearby trajectories will separate measurably over time.",
        model="dx/dt=sigma(y-x); dy/dt=x(rho-z)-y; dz/dt=xy-beta z",
        parameters={"rho": rho, "sigma": 10.0, "beta": 8.0 / 3.0, "dt": dt, "steps": float(steps)},
        method="fixed-step RK4; paired initial conditions",
        seed=0,
        result=result.to_dict(),
        evidence_tier="NUMERICAL_OBSERVATION",
        reproducible=True,
    )
    return record, trajectory


def sweep_rho(values: list[float]) -> list[ExperimentRecord]:
    return [run_lorenz_experiment(rho)[0] for rho in values]
