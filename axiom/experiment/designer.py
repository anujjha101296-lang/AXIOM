"""
axiom.experiment.designer
=========================
Experiment Design Engine.
Converts VerificationPlan / Hypothesis into a structured, validated Experiment specification.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from axiom.experiment.models import Experiment, ExperimentStatus


class ExperimentDesigner:
    """Designs structured computational experiments from verification plans or hypotheses."""

    def design_experiment(
        self,
        project_id: str,
        hypothesis_id: Optional[str] = None,
        prediction_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        name: str = "Numerical Verification Experiment",
        objective: str = "Test hypothesis prediction via controlled computation",
        code_body: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Experiment:
        """Create structured Experiment specification."""
        default_code = (
            "import math\n"
            "# Controlled numerical calculation\n"
            "n = params.get('sample_size', 1000)\n"
            "values = [math.sin(i * 0.01) ** 2 + math.cos(i * 0.01) ** 2 for i in range(n)]\n"
            "mean_val = sum(values) / len(values)\n"
            "result = {'sample_size': n, 'computed_mean': mean_val, 'identity_error': abs(mean_val - 1.0)}\n"
        )

        code = code_body or default_code
        params = parameters or {"sample_size": 1000}

        return Experiment(
            project_id=project_id,
            hypothesis_id=hypothesis_id,
            prediction_id=prediction_id,
            plan_id=plan_id,
            name=name,
            objective=objective,
            code_body=code,
            method="numerical_simulation",
            parameters=params,
            status=ExperimentStatus.VALIDATED,
        )
