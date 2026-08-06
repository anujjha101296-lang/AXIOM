"""Performance regression detection."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from axiom.governance.models import (
    CollectorResult,
    Finding,
    FindingCategory,
    MetricValue,
    Severity,
)

BASELINE_PATH = ".axiom/governance/performance_baseline.json"
IMPORT_THRESHOLD_MS = 5000


def collect_performance(workspace: Path) -> CollectorResult:
    result = CollectorResult(name="performance")
    import_ms = _measure_import_time(workspace)
    result.metrics.append(
        MetricValue("cold_import_ms", round(import_ms, 1), unit="ms", target=3000, status=_perf_status(import_ms, 3000, 5000))
    )

    baseline_path = workspace / BASELINE_PATH
    previous_ms = None
    if baseline_path.exists():
        try:
            previous_ms = json.loads(baseline_path.read_text())["cold_import_ms"]
        except (json.JSONDecodeError, KeyError):
            previous_ms = None

    if previous_ms is not None:
        delta_pct = ((import_ms - previous_ms) / max(previous_ms, 1)) * 100
        result.metrics.append(
            MetricValue("import_regression_pct", round(delta_pct, 1), unit="%", target=0, status="fail" if delta_pct > 20 else "ok")
        )
        if delta_pct > 20:
            result.findings.append(
                Finding(
                    category=FindingCategory.PERFORMANCE,
                    severity=Severity.HIGH,
                    title=f"Import time regression: +{delta_pct:.0f}%",
                    detail=f"Previous {previous_ms:.0f}ms → current {import_ms:.0f}ms",
                    recommendation="Profile with scripts/profile_core.py; reduce heavy imports at startup",
                    source=BASELINE_PATH,
                    score_impact=4.0,
                )
            )

    if import_ms > IMPORT_THRESHOLD_MS:
        result.findings.append(
            Finding(
                category=FindingCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
                title="Slow cold-start import path",
                detail=f"Core imports took {import_ms:.0f}ms (threshold {IMPORT_THRESHOLD_MS}ms)",
                recommendation="Lazy-import heavy modules (z3, sympy) in request handlers",
                source="import-benchmark",
                score_impact=3.0,
            )
        )

    profile_script = workspace / "scripts" / "profile_core.py"
    result.metrics.append(
        MetricValue("profile_script_present", int(profile_script.exists()), target=1, status="ok" if profile_script.exists() else "warn")
    )

    result.raw["cold_import_ms"] = import_ms
    result.raw["previous_import_ms"] = previous_ms
    return result


def save_performance_baseline(workspace: Path, import_ms: float) -> None:
    baseline_path = workspace / BASELINE_PATH
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps({"cold_import_ms": import_ms}, indent=2) + "\n")


def _perf_status(value: float, ok_at: float, warn_at: float) -> str:
    if value <= ok_at:
        return "ok"
    if value <= warn_at:
        return "warn"
    return "fail"


def _measure_import_time(workspace: Path) -> float:
    code = (
        "import time; t=time.perf_counter(); "
        "import axiom.config.settings; "
        "import axiom.services.api_gateway.main; "
        "print(time.perf_counter()-t)"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=workspace,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(workspace)},
            timeout=60,
        )
        return float(proc.stdout.strip()) * 1000
    except (ValueError, subprocess.TimeoutExpired):
        return 0.0
