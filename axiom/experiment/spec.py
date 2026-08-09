"""Experiment validation and specification (SEC §5)."""

from __future__ import annotations

from dataclasses import dataclass

from axiom.experiment.models import ComputeEnvironmentType, ExperimentSpec, ResourceBudget


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]

    def to_dict(self) -> dict:
        return {"valid": self.valid, "errors": self.errors}


def spec_from_dict(data: dict) -> ExperimentSpec:
    """Reconstruct ExperimentSpec from stored dict."""
    budget_data = data.get("resource_budget", {})
    budget = ResourceBudget(**budget_data) if budget_data else ResourceBudget()
    env_type = data.get("environment_type", "python")
    return ExperimentSpec(
        research_question=data.get("research_question", ""),
        hypothesis=data.get("hypothesis", ""),
        objective=data.get("objective", ""),
        variables=data.get("variables", {}),
        inputs=data.get("inputs", {}),
        procedure=data.get("procedure", ""),
        expected_observation=data.get("expected_observation", ""),
        environment_type=ComputeEnvironmentType(env_type),
        resource_budget=budget,
        evaluation_metrics=data.get("evaluation_metrics", []),
        stopping_conditions=data.get("stopping_conditions", {}),
        reproduction_instructions=data.get("reproduction_instructions", ""),
        random_seed=data.get("random_seed"),
        code=data.get("code"),
        tools=data.get("tools", []),
    )


def validate_spec(spec: ExperimentSpec) -> ValidationResult:
    """Validate experiment specification before execution."""
    errors: list[str] = []

    if not spec.research_question.strip():
        errors.append("research_question is required")
    if not spec.hypothesis.strip():
        errors.append("hypothesis is required")
    if not spec.objective.strip():
        errors.append("objective is required")
    if spec.resource_budget.timeout_seconds <= 0:
        errors.append("timeout_seconds must be positive")
    if spec.resource_budget.memory_mb <= 0:
        errors.append("memory_mb must be positive")
    if spec.code and len(spec.code) > 100_000:
        errors.append("code exceeds maximum length (100KB)")

    return ValidationResult(valid=not errors, errors=errors)
