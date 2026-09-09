"""Provider-neutral scientific discovery runtime.

The runtime is deterministic by default. LLMs are optional accelerators, never
required for scientific computation or evidence records.
"""

from .benchmark import run_lorenz_reference_benchmark
from .critic import Critique, critique_evidence
from .lorenz import run_lorenz_experiment
from .models import ExperimentRecord, LorenzResult

__all__ = [
    "Critique",
    "ExperimentRecord",
    "LorenzResult",
    "critique_evidence",
    "run_lorenz_experiment",
    "run_lorenz_reference_benchmark",
]
