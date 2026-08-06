"""Research loop worker package."""

from axiom.research_loop.workers.critic import SkepticCriticWorker
from axiom.research_loop.workers.experiment import ExperimentDesignerWorker
from axiom.research_loop.workers.hypothesis import HypothesisGeneratorWorker
from axiom.research_loop.workers.literature import LiteratureResearcherWorker
from axiom.research_loop.workers.planner import ResearchPlannerWorker
from axiom.research_loop.workers.reporter import ResearchReporterWorker
from axiom.research_loop.workers.synthesis import SynthesisWorker
from axiom.research_loop.workers.verifier import EvidenceVerifierWorker

__all__ = [
    "ResearchPlannerWorker",
    "LiteratureResearcherWorker",
    "HypothesisGeneratorWorker",
    "SkepticCriticWorker",
    "EvidenceVerifierWorker",
    "ExperimentDesignerWorker",
    "SynthesisWorker",
    "ResearchReporterWorker",
]
