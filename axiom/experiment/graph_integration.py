"""
axiom.experiment.graph_integration
===================================
Knowledge Graph Integration for Computational Experiments.
Connects Experiment, Observation, and Verification nodes into Phase 13 Claim Graph.
"""
from __future__ import annotations

from typing import Any, Dict

from axiom.experiment.models import Experiment, ExperimentObservation, ExperimentVerification


class ExperimentGraphIntegrator:
    """Integrates computational experiments into the Phase 13 Scientific Knowledge Graph."""

    def build_graph_nodes(
        self,
        experiment: Experiment,
        observation: ExperimentObservation,
        verification: ExperimentVerification,
    ) -> Dict[str, Any]:
        """Construct knowledge graph edges and nodes for experiment execution."""
        return {
            "nodes": [
                {"id": experiment.id, "type": "EXPERIMENT", "name": experiment.name},
                {"id": observation.id, "type": "OBSERVATION", "name": observation.summary[:60]},
                {"id": verification.id, "type": "VERIFICATION", "name": verification.verification_status.value},
            ],
            "edges": [
                {"source": experiment.hypothesis_id or "hypothesis-root", "target": experiment.id, "relation": "TESTED_BY"},
                {"source": experiment.id, "target": observation.id, "relation": "PRODUCED"},
                {"source": observation.id, "target": experiment.hypothesis_id or "hypothesis-root", "relation": observation.interpretation_status.value},
                {"source": experiment.id, "target": verification.id, "relation": "HAS_VERIFICATION"},
            ],
        }
