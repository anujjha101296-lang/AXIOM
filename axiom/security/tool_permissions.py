"""Tool execution risk classification for agent safety (TSS §6)."""

from __future__ import annotations

from enum import Enum


class ToolRiskClass(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW_RISK_WRITE = "LOW_RISK_WRITE"
    HIGH_RISK_WRITE = "HIGH_RISK_WRITE"
    DESTRUCTIVE = "DESTRUCTIVE"
    PRIVILEGED = "PRIVILEGED"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"


_AUTHORIZATION_REQUIRED = {
    ToolRiskClass.HIGH_RISK_WRITE,
    ToolRiskClass.DESTRUCTIVE,
    ToolRiskClass.PRIVILEGED,
    ToolRiskClass.EXTERNAL_SIDE_EFFECT,
}


def requires_explicit_authorization(risk: ToolRiskClass) -> bool:
    """Return True when human or policy authorization is required before execution."""
    return risk in _AUTHORIZATION_REQUIRED
