"""Counterexample engine (FMTP §9)."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.core.verification.smt_gateway import SmtGateway
from axiom.formal_math.models import CounterexampleRecord


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def search_counterexample(
    claim: str,
    *,
    equation: str | None = None,
    variables: list[str] | None = None,
    modulus: int = 10,
    method: str = "smt_modular",
    num_random_tests: int = 50,
) -> CounterexampleRecord | None:
    """Attempt to disprove a claim before heavy proof investment."""
    if method == "smt_modular" and equation and variables:
        gateway = SmtGateway()
        is_valid, counterexample = gateway.verify_modular_conjecture(equation, modulus, variables)
        if not is_valid and counterexample:
            return CounterexampleRecord(
                counterexample_id=f"cex_{uuid.uuid4().hex[:12]}",
                claim=claim,
                counterexample=counterexample,
                method="smt_modular",
                parameters={"modulus": modulus, "variables": variables},
                verified=True,
                created_at=_utc_now(),
            )
        return None

    if method == "randomized" and equation and variables:
        left, right = [s.strip().replace("^", "**") for s in equation.split("==")]
        for _ in range(num_random_tests):
            env = {v: random.randint(0, modulus - 1) for v in variables}
            try:
                if eval(left, {"__builtins__": None}, env) != eval(right, {"__builtins__": None}, env):
                    return CounterexampleRecord(
                        counterexample_id=f"cex_{uuid.uuid4().hex[:12]}",
                        claim=claim,
                        counterexample=env,
                        method="randomized",
                        parameters={"modulus": modulus, "tests": num_random_tests},
                        verified=False,
                        created_at=_utc_now(),
                    )
            except (SyntaxError, TypeError, ZeroDivisionError):
                continue

    return None
