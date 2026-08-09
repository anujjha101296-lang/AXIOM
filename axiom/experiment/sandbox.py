"""Sandboxed code execution (SEC §4, §11, §30)."""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from axiom.experiment.models import ResourceBudget

_FORBIDDEN_IMPORTS = frozenset({
    "os", "subprocess", "socket", "shutil", "ctypes", "pickle",
    "importlib", "sys", "pathlib", "signal", "multiprocessing",
})
_FORBIDDEN_CALLS = frozenset({
    "eval", "exec", "compile", "open", "__import__", "input",
    "getattr", "setattr", "delattr", "globals", "locals",
})


@dataclass
class SandboxResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    terminated_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "terminated_reason": self.terminated_reason,
        }


def static_analyze_code(code: str) -> list[str]:
    """Basic static analysis — reject dangerous patterns before execution."""
    issues: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"Syntax error: {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _FORBIDDEN_IMPORTS:
                    issues.append(f"Forbidden import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in _FORBIDDEN_IMPORTS:
                issues.append(f"Forbidden import from: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN_CALLS:
                issues.append(f"Forbidden call: {node.func.id}()")

    if "while True" in code.replace(" ", ""):
        issues.append("Potential infinite loop detected")

    return issues


def execute_sandboxed(
    code: str,
    *,
    budget: ResourceBudget | None = None,
    seed: int | None = None,
) -> SandboxResult:
    """Execute code in isolated subprocess with resource limits."""
    import time

    budget = budget or ResourceBudget()
    issues = static_analyze_code(code)
    if issues:
        return SandboxResult(
            success=False,
            stdout="",
            stderr="; ".join(issues),
            exit_code=1,
            duration_ms=0.0,
            terminated_reason="static_analysis_failed",
        )

    indented_code = "\n".join(f"    {line}" for line in code.splitlines())
    wrapper = (
        "import random\n"
        f"random.seed({seed if seed is not None else 42})\n"
        "def __axiom_user_main():\n"
        f"{indented_code}\n"
        "__axiom_user_main()\n"
    )

    start = time.monotonic()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(wrapper)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=budget.timeout_seconds,
        )
        duration_ms = (time.monotonic() - start) * 1000
        return SandboxResult(
            success=result.returncode == 0,
            stdout=result.stdout[:100_000],
            stderr=result.stderr[:50_000],
            exit_code=result.returncode,
            duration_ms=round(duration_ms, 2),
        )
    except subprocess.TimeoutExpired:
        duration_ms = (time.monotonic() - start) * 1000
        return SandboxResult(
            success=False,
            stdout="",
            stderr=f"Execution exceeded {budget.timeout_seconds}s timeout",
            exit_code=-1,
            duration_ms=round(duration_ms, 2),
            terminated_reason="timeout",
        )
    finally:
        Path(script_path).unlink(missing_ok=True)
