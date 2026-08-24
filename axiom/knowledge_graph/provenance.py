"""
axiom.knowledge_graph.provenance
================================
Provenance Verification & Validation Engine.
Chain: CLAIM -> EVIDENCE -> CHUNK -> SOURCE -> DOCUMENT/URL.
Rejects invalid or orphaned claims.
"""
from __future__ import annotations

from typing import List, Optional

from axiom.knowledge_graph.models import GraphClaim, GraphClaimEvidence


class ProvenanceVerifier:
    """Verifies that graph assertions link to authentic evidence and sources."""

    def verify_claim_provenance(
        self,
        claim: GraphClaim,
        evidence_list: List[GraphClaimEvidence],
    ) -> bool:
        """
        Verify claim provenance chain.
        Returns True if claim is backed by at least one valid evidence reference.
        """
        claim_evidences = [e for e in evidence_list if e.claim_id == claim.id]
        if not claim_evidences:
            return False

        for e in claim_evidences:
            # Evidence must have snippet and at least one source linkage (chunk, source, or document)
            if e.snippet and (e.chunk_id or e.source_id or e.document_id):
                return True

        return False
