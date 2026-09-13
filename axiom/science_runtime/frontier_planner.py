"""Optional frontier LLM planner.

The planner emits only a typed ScientificPlan. Execution and verification stay
inside the deterministic scientific runtime.
"""
from __future__ import annotations

import os

from .agent_guard import validate_plan
from .agent_protocol import ScientificPlan


class FrontierScientificPlanner:
    def __init__(self, model: str | None = None, max_turns: int = 2) -> None:
        self.model = model or os.getenv("AXIOM_SCIENTIFIC_MODEL", "gpt-5.6-luna")
        self.max_turns = max_turns

    def plan(self, question: str) -> ScientificPlan:
        from agents import Agent, Runner
        from pydantic import BaseModel, ConfigDict, Field

        class PlanOutput(BaseModel):
            model_config = ConfigDict(extra="forbid")
            hypothesis: str = Field(min_length=1, max_length=1000)
            rationale: str = Field(min_length=1, max_length=1500)
            experiment_name: str = Field(min_length=1, max_length=120)
            parameters: dict[str, float]
            expected_observation: str = Field(min_length=1, max_length=1000)

        agent = Agent(
            name="AXIOM Scientific Planner",
            model=self.model,
            instructions=(
                "Return one bounded Lorenz experiment. Use only rho in "
                "{20,24,28,32,40}, sigma=10, beta=8/3, dt in [0.0005,0.05], "
                "horizon in [0.1,10]. Do not provide code, tools, proofs, or "
                "claims of verified evidence. Return only the requested fields."
            ),
            output_type=PlanOutput,
        )
        result = Runner.run_sync(agent, question, max_turns=self.max_turns)
        output = result.final_output
        return validate_plan(
            ScientificPlan(
                hypothesis=output.hypothesis,
                rationale=output.rationale,
                experiment_name=output.experiment_name,
                parameters=output.parameters,
                expected_observation=output.expected_observation,
            )
        )
