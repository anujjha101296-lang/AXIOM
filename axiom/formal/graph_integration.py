"""
axiom.formal.graph_integration
==============================
Knowledge Graph Integration for Formal Mathematics.
Connects FormalTheorem and ProofArtifact nodes into Phase 13 Claim Graph.
"""
from __future__ import annotations

from typing import Any, Dict

from axiom.formal.models import FormalProof, FormalTheorem, ProofArtifact


class FormalGraphIntegrator:
    """Integrates formal mathematical theorems and proofs into Phase 13 Claim Graph."""

    def build_graph_nodes(
        self,
        theorem: FormalTheorem,
        proof: FormalProof,
        artifact: ProofArtifact,
    ) -> Dict[str, Any]:
        """Construct knowledge graph edges and nodes for formal proof verification."""
        return {
            "nodes": [
                {"id": theorem.id, "type": "FORMAL_THEOREM", "name": theorem.name},
                {"id": proof.id, "type": "FORMAL_PROOF", "name": proof.status.value},
                {"id": artifact.id, "type": "PROOF_ARTIFACT", "name": artifact.hash_id},
            ],
            "edges": [
                {"source": theorem.claim_id or "claim-root", "target": theorem.id, "relation": "FORMALIZED_AS"},
                {"source": theorem.id, "target": proof.id, "relation": "PROVED_BY"},
                {"source": proof.id, "target": artifact.id, "relation": "PERSISTED_AS"},
            ],
        }
