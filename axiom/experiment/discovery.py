"""Discovery signal detection — conservative (SEC §26)."""

from __future__ import annotations

from typing import Any


_DISCOVERY_SIGNALS = frozenset({
    "unexpected_pattern",
    "counterexample",
    "performance_anomaly",
    "phase_transition",
    "new_relationship",
    "unexpected_optimization",
})


def detect_discovery_signals(results: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect unusual observations — must NOT auto-classify as discoveries."""
    signals: list[dict[str, Any]] = []

    stdout = results.get("sandbox", {}).get("stdout", "")
    stdout_u = stdout.upper()
    # Do not treat NO_COUNTEREXAMPLE as a hit (substring trap).
    if "COUNTEREXAMPLE_FOUND" in stdout_u or any(
        line.strip() == "COUNTEREXAMPLE" for line in stdout_u.splitlines()
    ):
        signals.append({
            "signal": "counterexample",
            "severity": "high",
            "action": "trigger_er_counterexample_workflow",
            "auto_discovery": False,
        })

    if results.get("unexpected"):
        signals.append({
            "signal": "unexpected_pattern",
            "severity": "medium",
            "action": "investigate_and_reproduce",
            "auto_discovery": False,
        })

    return signals
