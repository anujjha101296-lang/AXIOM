"""Subsystem registry — maps cognitive layers to existing AXIOM infrastructure."""

from __future__ import annotations

from axiom.cognitive.models import CognitiveLayer, CognitivePillar, PILLAR_TO_LAYERS

# Each layer delegates to existing packages; ACA does not reimplement them.
LAYER_SUBSYSTEM_MAP: dict[CognitiveLayer, dict[str, str]] = {
    CognitiveLayer.PERCEPTION: {
        "pillar": CognitivePillar.KNOWLEDGE.value,
        "primary": "axiom.core.parser.arxiv_parser",
        "secondary": "axiom.research.pdf_extractor",
        "inputs": "documents, code, papers, datasets, human_input",
    },
    CognitiveLayer.UNDERSTANDING: {
        "pillar": CognitivePillar.KNOWLEDGE.value,
        "primary": "axiom.core.knowledge_graph.db.EpistemicStore",
        "secondary": "axiom.core.parser.semantic_tracker",
        "extracts": "entities, relationships, definitions, theorems, unknowns",
    },
    CognitiveLayer.MEMORY: {
        "pillar": CognitivePillar.MEMORY.value,
        "primary": "axiom.core.memory.working_memory.WorkingMemory",
        "secondary": "axiom.scientific_method.store.SMEStore",
        "stores": "working, long_term, semantic, research, failure, project",
    },
    CognitiveLayer.REASONING: {
        "pillar": CognitivePillar.REASONING.value,
        "primary": "axiom.core.reasoning.hypothesis_engine.HypothesisEngine",
        "secondary": "axiom.core.reasoning.mcts.MctsSolver",
        "modes": "deduction, induction, abduction, analogy, mathematical",
    },
    CognitiveLayer.PLANNING: {
        "pillar": CognitivePillar.PLANNING.value,
        "primary": "axiom.workflow.scheduler.WorkflowScheduler",
        "secondary": "axiom.mip.strategy.millennium_trees",
        "outputs": "research_plans, proof_plans, experiment_plans, execution_graphs",
    },
    CognitiveLayer.EXECUTION: {
        "pillar": CognitivePillar.EXECUTION.value,
        "primary": "axiom.workflow.executor.ParallelExecutor",
        "secondary": "axiom.services.model_gateway.client.ModelClient",
        "coordinates": "tools, models, agents, provers, simulators",
    },
    CognitiveLayer.VERIFICATION: {
        "pillar": CognitivePillar.VERIFICATION.value,
        "primary": "axiom.core.verification.truthfulness",
        "secondary": "axiom.core.verification.smt_gateway.SmtGateway",
        "checks": "evidence, formal, citation, consistency, critique",
    },
    CognitiveLayer.LEARNING: {
        "pillar": CognitivePillar.LEARNING.value,
        "primary": "axiom.core.reasoning.self_improvement.SelfImprovementLoop",
        "secondary": "axiom.scientific_method.phases.PhaseExecutor",
        "captures": "successes, failures, pattern_changes",
    },
    CognitiveLayer.REFLECTION: {
        "pillar": CognitivePillar.REFLECTION.value,
        "primary": "axiom.governance.review.EngineeringReview",
        "secondary": "axiom.evaluation.frameworks.evidence",
        "recommends": "architecture, workflow, reasoning, benchmark improvements",
    },
}


def architecture_manifest() -> dict:
    """Return full ACA manifest for API and documentation."""
    layers = []
    for layer in CognitiveLayer:
        info = LAYER_SUBSYSTEM_MAP[layer]
        pillar = CognitivePillar(info["pillar"])
        layers.append({
            "layer": layer.value,
            "order": list(CognitiveLayer).index(layer) + 1,
            "pillar": pillar.value,
            "subsystem_primary": info["primary"],
            "subsystem_secondary": info.get("secondary"),
            "capabilities": {k: v for k, v in info.items() if k not in ("pillar", "primary", "secondary")},
        })

    return {
        "name": "AXIOM Cognitive Architecture",
        "abbreviation": "ACA",
        "principle": "Models are interchangeable; cognitive architecture is permanent.",
        "pillars": [p.value for p in CognitivePillar],
        "layers": layers,
        "pillar_mapping": {
            p.value: [l.value for l in layers_list]
            for p, layers_list in PILLAR_TO_LAYERS.items()
        },
    }
