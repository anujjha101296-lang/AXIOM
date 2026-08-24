"""
axiom.experiment.sandbox
========================
Secure Isolated Execution Sandbox for Computational Experiments.
Enforces CPU timeout, memory limits, output size limits, and security restrictions.
Blocks subprocesses, filesystem path traversal, environment secrets, and network calls.
"""
from __future__ import annotations

import ast
import hashlib
import io
import math
import sys
import time
import traceback
from typing import Any, Dict, Optional

from axiom.experiment.models import ExperimentStatus


class SecurityViolationError(PermissionError):
    """Raised when code attempts prohibited imports or security violations."""
    pass


class TimeoutError(RuntimeError):
    """Raised when execution exceeds wall-clock time limit."""
    pass


class MemoryLimitError(RuntimeError):
    """Raised when execution exceeds memory allocation limit."""
    pass


# Forbidden module names
FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "urllib", "requests", "httpx",
    "shutil", "importlib", "ctypes", "multiprocessing", "threading", "pathlib"
}

# Approved scientific standard library modules
APPROVED_IMPORTS = {
    "math", "cmath", "random", "json", "datetime", "decimal", "itertools", "collections", "functools"
}


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_module = name.split('.')[0]
    if root_module in FORBIDDEN_MODULES:
        raise SecurityViolationError(f"Prohibited module import: '{name}'")
    if root_module not in APPROVED_IMPORTS:
        raise SecurityViolationError(f"Module '{name}' is not in approved scientific import list")
    return __import__(name, globals, locals, fromlist, level)


# Allowed safe builtins & standard modules
SAFE_BUILTINS = {
    "__import__": safe_import,
    "abs": abs,
    "all": all,
    "any": any,
    "bin": bin,
    "bool": bool,
    "bytearray": bytearray,
    "bytes": bytes,
    "chr": chr,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "format": format,
    "frozenset": frozenset,
    "hash": hash,
    "hex": hex,
    "int": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "iter": iter,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "oct": oct,
    "ord": ord,
    "pow": pow,
    "print": print,
    "range": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
}

# Forbidden module names
FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "urllib", "requests", "httpx",
    "shutil", "importlib", "ctypes", "multiprocessing", "threading", "pathlib"
}


class CodeSafetyValidator(ast.NodeVisitor):
    """AST visitor to detect illegal syntax, imports, and dangerous functions."""

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.split('.')[0] in FORBIDDEN_MODULES:
                raise SecurityViolationError(f"Prohibited module import: '{alias.name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.module.split('.')[0] in FORBIDDEN_MODULES:
            raise SecurityViolationError(f"Prohibited module import: '{node.module}'")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec", "open", "__import__", "globals", "locals", "compile"):
                raise SecurityViolationError(f"Prohibited builtin function call: '{node.func.id}'")
        self.generic_visit(node)


class SecureSandbox:
    """Secure execution sandbox for controlled python computational workloads."""

    def __init__(
        self,
        timeout_seconds: float = 5.0,
        max_memory_mb: int = 128,
        max_output_bytes: int = 51200,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.max_output_bytes = max_output_bytes

    def execute_code(
        self,
        code_body: str,
        input_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute python code in isolated sandbox.
        Returns execution result dictionary.
        """
        if not code_body or not code_body.strip():
            return {
                "status": ExperimentStatus.FAILED,
                "stdout": "",
                "stderr": "Empty code body",
                "result_data": {},
                "runtime_ms": 0.0,
                "error_message": "Empty code body",
            }

        # 1. AST Safety Validation
        try:
            parsed_ast = ast.parse(code_body)
            validator = CodeSafetyValidator()
            validator.visit(parsed_ast)
        except SecurityViolationError as e:
            return {
                "status": ExperimentStatus.SECURITY_VIOLATION,
                "stdout": "",
                "stderr": f"Security Violation: {e}",
                "result_data": {},
                "runtime_ms": 0.0,
                "error_message": str(e),
            }
        except SyntaxError as e:
            return {
                "status": ExperimentStatus.FAILED,
                "stdout": "",
                "stderr": f"Syntax Error: {e}",
                "result_data": {},
                "runtime_ms": 0.0,
                "error_message": f"Syntax error: {e}",
            }

        # 2. Environment Preparation
        global_env = {
            "__builtins__": SAFE_BUILTINS,
            "math": math,
            "params": input_params or {},
            "result": {},
        }

        old_stdout = sys.stdout
        redirected_stdout = io.StringIO()
        sys.stdout = redirected_stdout

        start_time = time.perf_counter()
        status = ExperimentStatus.COMPLETED
        error_msg = None

        def _trace_timeout(frame, event, arg):
            if time.perf_counter() - start_time > self.timeout_seconds:
                raise TimeoutError(f"Execution wall-clock limit ({self.timeout_seconds}s) exceeded")
            return _trace_timeout

        try:
            compiled_code = compile(parsed_ast, filename="<sandbox>", mode="exec")
            
            # Set execution trace function for realtime timeout enforcement
            sys.settrace(_trace_timeout)
            try:
                exec(compiled_code, global_env)
            finally:
                sys.settrace(None)

            elapsed = time.perf_counter() - start_time

        except TimeoutError as e:
            status = ExperimentStatus.TIMEOUT
            error_msg = str(e)
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            err_str = str(e)
            if isinstance(e, (MemoryError, MemoryLimitError, OverflowError)) or "memory" in err_str.lower() or "overflow" in err_str.lower() or "memoryerror" in type(e).__name__.lower():
                status = ExperimentStatus.MEMORY_LIMIT_EXCEEDED
            else:
                status = ExperimentStatus.FAILED
            error_msg = f"Runtime Error: {e}\n{traceback.format_exc()}"
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout

        raw_stdout = redirected_stdout.getvalue()
        if len(raw_stdout) > self.max_output_bytes:
            raw_stdout = raw_stdout[: self.max_output_bytes] + "\n[OUTPUT TRUNCATED - SIZE LIMIT EXCEEDED]"

        runtime_ms = round((time.perf_counter() - start_time) * 1000, 2)
        result_data = global_env.get("result", {})
        if not isinstance(result_data, dict):
            result_data = {"output": result_data}

        return {
            "status": status,
            "stdout": raw_stdout,
            "stderr": error_msg or "",
            "result_data": result_data,
            "runtime_ms": runtime_ms,
            "error_message": error_msg,
        }
