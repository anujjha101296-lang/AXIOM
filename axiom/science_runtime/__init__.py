"""Provider-neutral scientific discovery runtime.

The runtime is deterministic by default. LLMs are optional accelerators, never
required for the scientific computation or evidence record.
"""

from .models import ExperimentRecord, LorenzResult
from .lorenz import run_lorenz_experiment

__all__ = ["ExperimentRecord", "LorenzResult", "run_lorenz_experiment"]
