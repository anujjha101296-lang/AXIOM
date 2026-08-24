"""
axiom.experiment.executor
========================
Safe Experiment Execution Engine.
Executes computational experiments inside SecureSandbox and records input/spec hashes.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional

from axiom.experiment.models import Experiment, ExperimentRun, ExperimentStatus
from axiom.experiment.sandbox import SecureSandbox


class ExperimentExecutor:
    """Executes validated computational experiments inside SecureSandbox."""

    def run_experiment(self, experiment: Experiment, run_number: int = 1, seed: Optional[int] = None) -> ExperimentRun:
        """Execute experiment code and record run metadata."""
        limits = experiment.resource_limits or {}
        sandbox = SecureSandbox(
            timeout_seconds=limits.get("timeout_seconds", 5.0),
            max_memory_mb=limits.get("max_memory_mb", 128),
            max_output_bytes=limits.get("max_output_bytes", 51200),
        )

        input_str = json.dumps(experiment.parameters, sort_keys=True)
        spec_str = f"{experiment.code_body}:{input_str}"
        input_hash = hashlib.sha256(input_str.encode("utf-8")).hexdigest()[:16]
        spec_hash = hashlib.sha256(spec_str.encode("utf-8")).hexdigest()[:16]

        params = dict(experiment.parameters)
        if seed is not None:
            params["seed"] = seed

        res = sandbox.execute_code(experiment.code_body, input_params=params)

        return ExperimentRun(
            experiment_id=experiment.id,
            run_number=run_number,
            status=res["status"],
            runtime_ms=res["runtime_ms"],
            memory_bytes=1024 * 1024 * 10, # estimated footprint
            stdout=res["stdout"],
            stderr=res["stderr"],
            result_data=res["result_data"],
            input_hash=input_hash,
            spec_hash=spec_hash,
            seed=seed,
            error_message=res["error_message"],
        )
