"""Provider-neutral scientific discovery runtime.

The runtime is deterministic by default. LLMs are optional accelerators, never
required for scientific computation or evidence records.
"""

from .benchmark import run_lorenz_reference_benchmark
from .critic import Critique, critique_evidence
from .lorenz import run_lorenz_experiment
from .models import ExperimentRecord, LorenzResult
from .research_loop import ResearchQuestion, ResearchRun, ResearchStage, run_research

__all__ = [
    "Critique",
    "ExperimentRecord",
    "LorenzResult",
    "ResearchQuestion",
    "ResearchRun",
    "ResearchStage",
    "critique_evidence",
    "run_lorenz_experiment",
    "run_lorenz_reference_benchmark",
    "run_research",
]
