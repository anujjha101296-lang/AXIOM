"""Proof dependency graph (FMTP §17)."""

from __future__ import annotations

from typing import Any

from axiom.formal_math.models import TrustLayer
from axiom.formal_math.store import FormalMathStore


def build_dependency_graph(
    store: FormalMathStore,
    theorem_id: str,
) -> dict[str, Any]:
    """Construct theorem → definitions → lemmas → axioms dependency graph."""
    entity = store.get_entity(theorem_id)
    if not entity:
        raise KeyError(f"Theorem not found: {theorem_id}")

    proofs = store.list_proofs(theorem_id=theorem_id)
    nodes: list[dict[str, Any]] = [
        {
            "id": entity.entity_id,
            "type": entity.entity_type,
            "name": entity.name,
            "statement": entity.statement,
            "trust_layer": TrustLayer.FORMAL_LIBRARY.value,
        }
    ]
    edges: list[dict[str, str]] = []

    for dep_id in entity.dependencies:
        dep = store.get_entity(dep_id)
        if dep:
            nodes.append({
                "id": dep.entity_id,
                "type": dep.entity_type,
                "name": dep.name,
                "trust_layer": TrustLayer.FORMAL_LIBRARY.value,
            })
            edges.append({"source": dep_id, "target": theorem_id, "type": "depends_on"})

    for proof in proofs:
        nodes.append({
            "id": proof.proof_id,
            "type": "proof",
            "prover": proof.prover,
            "status": proof.compilation_status.value,
            "trust_layers": proof.trust_layers,
        })
        edges.append({"source": proof.proof_id, "target": theorem_id, "type": "proves"})

        for lib, version in proof.library_versions.items():
            lib_id = f"lib_{lib}"
            nodes.append({
                "id": lib_id,
                "type": "library",
                "name": lib,
                "version": version,
                "trust_layer": TrustLayer.FORMAL_LIBRARY.value,
            })
            edges.append({"source": lib_id, "target": proof.proof_id, "type": "imported_by"})

    nodes.append({
        "id": "trusted_kernel",
        "type": "kernel",
        "name": "Theorem prover kernel",
        "trust_layer": TrustLayer.TRUSTED_KERNEL.value,
    })

    return {
        "theorem_id": theorem_id,
        "nodes": nodes,
        "edges": edges,
        "axiom_chain": ["trusted_kernel"],
    }
