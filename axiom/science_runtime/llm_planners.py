"""Provider adapters for structured scientific planning.

LLMs propose plans only. They never execute scientific code, choose arbitrary
runtime tools, access the network, or establish evidence. The deterministic
scientific runtime remains the authority for execution and verification.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import asdict
from typing import Any

from .agent_protocol import ScientificPlan, ScientificPlanner


class PlannerConfigurationError(RuntimeError):
    """Raised when a provider adapter is not configured safely."""


_ALLOWED_PARAMETER_RANGES: dict[str, tuple[float, float]] = {
    "rho": (1.0, 40.0),
    "sigma": (1.0, 20.0),
    "beta": (0.1, 10.0),
    "dt": (0.0001, 0.1),
    "horizon": (0.1, 20.0),
}


def validate_scientific_plan(plan: ScientificPlan) -> ScientificPlan:
    """Validate the provider output before it can enter the runtime boundary."""
    if not plan.hypothesis.strip() or not plan.experiment_name.strip():
        raise ValueError("scientific plans require a hypothesis and experiment name")
    if not plan.parameters:
        raise ValueError("scientific plans require bounded parameters")

    for name, value in plan.parameters.items():
        if name not in _ALLOWED_PARAMETER_RANGES:
            raise ValueError(f"parameter {name!r} is not allowed by the Lorenz adapter")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"parameter {name!r} must be numeric")
        low, high = _ALLOWED_PARAMETER_RANGES[name]
        if not low <= float(value) <= high:
            raise ValueError(f"parameter {name!r} is outside its safe range [{low}, {high}]")

    return plan


class _PlannerOutput:
    """Pydantic-compatible structured output declared lazily by the SDK."""

    def __init__(self, hypothesis: str, rationale: str, experiment_name: str,
                 parameters: dict[str, float], expected_observation: str) -> None:
        self.hypothesis = hypothesis
        self.rationale = rationale
        self.experiment_name = experiment_name
        self.parameters = parameters
        self.expected_observation = expected_observation



def _output_type() -> Any:
    from pydantic import BaseModel, Field

    class ScientificPlanOutput(BaseModel):
        hypothesis: str = Field(min_length=1)
        rationale: str = Field(min_length=1)
        experiment_name: str = Field(min_length=1)
        parameters: dict[str, float]
        expected_observation: str = Field(min_length=1)

    return ScientificPlanOutput


def _instructions() -> str:
    return """You are AXIOM's scientific planning agent.

Produce exactly one bounded computational-science plan for the user's question.
You are a planner, not an executor. Do not claim that an observation is a proof.
Use only these Lorenz parameters: rho, sigma, beta, dt, horizon.
Keep values within conservative numerical ranges. Prefer a single deterministic
experiment that can be executed and independently checked by AXIOM's runtime.
"""


def _to_plan(output: Any) -> ScientificPlan:
    plan = ScientificPlan(**output.model_dump())
    return validate_scientific_plan(plan)


class OpenAIAgentsScientificPlanner(ScientificPlanner):
    """OpenAI Agents SDK planner using the configured OpenAI API key."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("AXIOM_OPENAI_MODEL", "gpt-5-mini")

    async def plan_async(self, question: str) -> ScientificPlan:
        try:
            from agents import Agent, Runner
        except ImportError as exc:
            raise PlannerConfigurationError(
                "openai-agents is not installed; install the AXIOM agent dependencies"
            ) from exc

        agent = Agent(
            name="AXIOM Scientific Planner",
            instructions=_instructions(),
            model=self.model,
            output_type=_output_type(),
        )
        result = await Runner.run(agent, question, max_turns=2)
        return _to_plan(result.final_output)

    def plan(self, question: str) -> ScientificPlan:
        return _run_sync(self.plan_async(question))


class OllamaAgentsScientificPlanner(ScientificPlanner):
    """Local Ollama planner through its OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model or os.getenv("AXIOM_OLLAMA_MODEL", "qwen3:8b")
        self.base_url = base_url or os.getenv(
            "AXIOM_OLLAMA_BASE_URL", "http://localhost:11434/v1"
        )

    async def plan_async(self, question: str) -> ScientificPlan:
        try:
            from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
        except ImportError as exc:
            raise PlannerConfigurationError(
                "openai-agents is not installed; install the AXIOM agent dependencies"
            ) from exc

        set_tracing_disabled(True)
        client = AsyncOpenAI(api_key="ollama", base_url=self.base_url)
        model = OpenAIChatCompletionsModel(model=self.model, openai_client=client)
        agent = Agent(
            name="AXIOM Local Scientific Planner",
            instructions=_instructions(),
            model=model,
            output_type=_output_type(),
        )
        result = await Runner.run(agent, question, max_turns=2)
        return _to_plan(result.final_output)

    def plan(self, question: str) -> ScientificPlan:
        return _run_sync(self.plan_async(question))


def _run_sync(coro: Any) -> ScientificPlan:
    """Run a provider coroutine from synchronous runtime boundaries."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError("use plan_async() when calling a planner from an active event loop")


__all__ = [
    "OllamaAgentsScientificPlanner",
    "OpenAIAgentsScientificPlanner",
    "PlannerConfigurationError",
    "validate_scientific_plan",
]
