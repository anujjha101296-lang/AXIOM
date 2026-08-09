"""Test pyramid runners (VF §2)."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from axiom.vfactory.models import TestLevel, TestRunResult, _new_id

ROOT = Path(__file__).resolve().parents[2]


def _run_cmd(cmd: list[str], *, cwd: Path | None = None, timeout: float = 120.0) -> tuple[bool, str, str, float]:
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout,
        )
        elapsed = time.monotonic() - start
        return proc.returncode == 0, proc.stdout, proc.stderr, elapsed
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        return False, exc.stdout or "", f"TIMEOUT after {timeout}s", elapsed
    except Exception as exc:
        elapsed = time.monotonic() - start
        return False, "", str(exc), elapsed


def run_static_analysis() -> TestRunResult:
    """Level 1: lint + type check."""
    ok, out, err, elapsed = _run_cmd(
        ["python3", "-m", "ruff", "check", "axiom/", "--select", "E9"],
    )
    return TestRunResult(
        run_id=_new_id("trun"), level=TestLevel.STATIC_ANALYSIS,
        test_name="ruff_syntax", passed=ok, duration_seconds=elapsed,
        output=out, error=err,
    )


def run_unit_tests(test_path: str | None = None) -> TestRunResult:
    """Level 2: unit tests."""
    cmd = ["python3", "-m", "pytest", test_path or "tests/", "--ignore=tests/e2e", "-q", "--tb=no"]
    ok, out, err, elapsed = _run_cmd(cmd, timeout=180.0)
    return TestRunResult(
        run_id=_new_id("trun"), level=TestLevel.UNIT,
        test_name=test_path or "core_suite", passed=ok, duration_seconds=elapsed,
        output=out[-4000:], error=err[-2000:],
    )


def run_health_check(make_target: str) -> TestRunResult:
    """Level 3-6: loop health checks as component/integration gates."""
    ok, out, err, elapsed = _run_cmd(["make", make_target], timeout=120.0)
    return TestRunResult(
        run_id=_new_id("trun"), level=TestLevel.COMPONENT,
        test_name=f"make_{make_target}", passed=ok, duration_seconds=elapsed,
        output=out, error=err,
    )


def run_security_scan() -> TestRunResult:
    """Level 8: TSS security scan."""
    script = ROOT / "scripts" / "tss_security_check.py"
    if not script.exists():
        return TestRunResult(
            run_id=_new_id("trun"), level=TestLevel.SECURITY,
            test_name="tss_security", passed=False, duration_seconds=0.0,
            error="tss_security_check.py not found",
        )
    ok, out, err, elapsed = _run_cmd(["python3", str(script)], timeout=60.0)
    return TestRunResult(
        run_id=_new_id("trun"), level=TestLevel.SECURITY,
        test_name="tss_security", passed=ok, duration_seconds=elapsed,
        output=out, error=err,
    )


def run_scientific_benchmark(script: str) -> TestRunResult:
    """Level 10: scientific capability benchmark."""
    path = ROOT / script
    if not path.exists():
        return TestRunResult(
            run_id=_new_id("trun"), level=TestLevel.SCIENTIFIC,
            test_name=script, passed=False, duration_seconds=0.0,
            error=f"Benchmark script not found: {script}",
        )
    ok, out, err, elapsed = _run_cmd(["python3", str(path)], timeout=180.0)
    return TestRunResult(
        run_id=_new_id("trun"), level=TestLevel.SCIENTIFIC,
        test_name=script, passed=ok, duration_seconds=elapsed,
        output=out, error=err,
    )


LOOP_HEALTH_CHECKS = [
    "erl-health", "simr-health", "fmtp-health",
    "sec-health", "frce-health", "skai-health", "cel-health", "vfactory-health",
]
