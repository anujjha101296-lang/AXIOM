"""Parameter search (SEC §6)."""

from __future__ import annotations

import itertools
import random
from typing import Any, Iterator

from axiom.experiment.models import SearchStrategy


def generate_parameter_configs(
    param_space: dict[str, list[Any]],
    strategy: SearchStrategy = SearchStrategy.GRID,
    *,
    max_configs: int = 20,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate parameter configurations — records every config tested."""
    if not param_space:
        return [{}]

    if strategy == SearchStrategy.GRID:
        keys = list(param_space.keys())
        values = [param_space[k] for k in keys]
        configs = [dict(zip(keys, combo)) for combo in itertools.product(*values)]
        return configs[:max_configs]

    if strategy == SearchStrategy.RANDOM:
        rng = random.Random(seed)
        keys = list(param_space.keys())
        configs = []
        for _ in range(min(max_configs, 50)):
            config = {k: rng.choice(param_space[k]) for k in keys}
            if config not in configs:
                configs.append(config)
        return configs

    return [{}]
