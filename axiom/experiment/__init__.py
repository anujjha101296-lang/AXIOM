"""Scientific Experimentation & Compute Loop package."""

from axiom.experiment.comparison import compare_experiments
from axiom.experiment.counterexample import search_computational_counterexample
from axiom.experiment.environment import capture_environment
from axiom.experiment.executor import execute_experiment
from axiom.experiment.integrity_gate import check_experiment_integrity
from axiom.experiment.models import ExperimentSpec, ExperimentStatus, ResourceBudget
from axiom.experiment.parameter_search import generate_parameter_configs
from axiom.experiment.planner import plan_experiments
from axiom.experiment.plugins import get_plugin, list_plugins
from axiom.experiment.reproduction import compare_experiment_results
from axiom.experiment.sandbox import execute_sandboxed, static_analyze_code
from axiom.experiment.spec import validate_spec
from axiom.experiment.store import ExperimentStore, get_experiment_store

__all__ = [
    "ExperimentSpec",
    "ExperimentStatus",
    "ExperimentStore",
    "ResourceBudget",
    "capture_environment",
    "check_experiment_integrity",
    "compare_experiment_results",
    "compare_experiments",
    "execute_experiment",
    "execute_sandboxed",
    "generate_parameter_configs",
    "get_experiment_store",
    "get_plugin",
    "list_plugins",
    "plan_experiments",
    "search_computational_counterexample",
    "static_analyze_code",
    "validate_spec",
]
