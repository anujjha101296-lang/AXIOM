"""Reproducibility — config hashing and replay."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from axiom.research_validation.models import ResearchRunConfig


def config_hash(config: ResearchRunConfig | dict[str, Any]) -> str:
    """Stable hash for run configuration (replay key)."""
    if isinstance(config, ResearchRunConfig):
        payload = config.to_dict()
    else:
        payload = config
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def configs_equivalent(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return config_hash(a) == config_hash(b)
