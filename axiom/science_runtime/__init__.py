"""Provider-neutral scientific discovery runtime.

The runtime is deterministic by default. LLMs are optional accelerators, never
required for scientific computation or evidence records.
"""

from .agent_protocol import ScientificPlan, ScientificPlanner
from .benchmark import run_lorenz_reference_benchmark
from .critic import Critique, critique_evidence
from .llm_planners import (
    OllamaAgentsScientificPlanner,
    OpenAIAgentsScientificPlanner,
    PlannerConfigurationError,
    validate_scientific_plan,
)
from .lorenz import run_lorenz_experiment
from .models import ExperimentRecord, LorenzResult
from .research_loop import ResearchQuestion, ResearchRun, ResearchStage, run_research

__all__ = [
    "Critique",
    "ExperimentRecord",
    "LorenzResult",
    "OllamaAgentsScientificPlanner",
    "OpenAIAgentsScientificPlanner",
    "PlannerConfigurationError",
    "ResearchQuestion",
    "ResearchRun",
    "ResearchStage",
    "ScientificPlan",
    "ScientificPlanner",
    "critique_evidence",
    "run_lorenz_experiment",
    "run_lorenz_reference_benchmark",
    "run_research",
    "validate_scientific_plan",
]
