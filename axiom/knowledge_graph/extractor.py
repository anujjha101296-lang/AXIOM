"""
axiom.knowledge_graph.extractor
===============================
Structured Claim and Entity Extraction from Evidence Chunks.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from axiom.knowledge_graph.models import (
    ClaimType,
    EntityType,
    EpistemicStatus,
    GraphClaim,
    GraphClaimEvidence,
    GraphEntity,
)


class ClaimExtractor:
    """Extracts candidate claims from text evidence chunks."""

    def extract_claims(
        self,
        project_id: str,
        text: str,
        chunk_id: Optional[str] = None,
        source_id: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> List[tuple[GraphClaim, GraphClaimEvidence]]:
        """Parse text into candidate claims with evidence links."""
        if not text or not text.strip():
            return []

        # Split text into meaningful sentences or assertions
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 15]
        if not sentences:
            sentences = [text.strip()]

        results = []
        for s in sentences:
            claim_type = self._classify_claim_type(s)
            claim = GraphClaim(
                project_id=project_id,
                claim_text=s,
                claim_type=claim_type,
                epistemic_status=EpistemicStatus.EXTRACTED,
                confidence_score=0.9,
                metadata={"extracted_from_chunk": chunk_id},
            )
            evidence = GraphClaimEvidence(
                claim_id=claim.id,
                chunk_id=chunk_id,
                source_id=source_id,
                document_id=document_id,
                supports=True,
                snippet=s[:300],
            )
            results.append((claim, evidence))

        return results

    def _classify_claim_type(self, text: str) -> ClaimType:
        t = text.lower()
        if any(w in t for w in ["=", ">", "<", "%", "increase", "decrease", "ratio", "score", "accuracy", "rate", "cost"]):
            return ClaimType.QUANTITATIVE
        if any(w in t for w in ["causes", "leads to", "results in", "improves", "reduces", "triggers"]):
            return ClaimType.CAUSAL
        if any(w in t for w in ["is defined as", "refers to", "means", "denotes"]):
            return ClaimType.DEFINITIONAL
        if any(w in t for w in ["compared to", "than", "outperforms", "versus", "vs"]):
            return ClaimType.COMPARATIVE
        if any(w in t for w in ["using", "via", "algorithm", "method", "approach", "architecture"]):
            return ClaimType.METHODOLOGICAL
        return ClaimType.FACTUAL


class EntityExtractor:
    """Extracts candidate entities from text or claims."""

    TAXONOMY = {
        "person": EntityType.PERSON,
        "author": EntityType.PERSON,
        "organization": EntityType.ORGANIZATION,
        "method": EntityType.METHOD,
        "algorithm": EntityType.ALGORITHM,
        "theorem": EntityType.THEOREM,
        "conjecture": EntityType.THEOREM,
        "mathematical_object": EntityType.MATHEMATICAL_OBJECT,
        "dataset": EntityType.DATASET,
        "software": EntityType.SOFTWARE,
        "concept": EntityType.CONCEPT,
        "paper": EntityType.PAPER,
        "field": EntityType.RESEARCH_FIELD,
    }

    def extract_entities(self, project_id: str, text: str) -> List[GraphEntity]:
        """Extract candidate entities using a controlled taxonomy."""
        if not text or not text.strip():
            return []

        extracted = []
        seen_names = set()

        # Extract capitalized multi-word phrases and key domain terms
        candidates = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for c in candidates:
            name = re.sub(r'^(The|A|An)\s+', '', c.strip(), flags=re.IGNORECASE)
            if len(name) > 3 and name.lower() not in seen_names:
                seen_names.add(name.lower())
                e_type = self._infer_type(name, text)
                extracted.append(
                    GraphEntity(
                        project_id=project_id,
                        name=name,
                        entity_type=e_type,
                        domain="scientific",
                    )
                )

        return extracted

    def _infer_type(self, name: str, context: str) -> EntityType:
        nl = name.lower()
        cl = context.lower()

        if "algorithm" in nl or "algorithm" in cl:
            return EntityType.ALGORITHM
        if "theorem" in nl or "lemma" in nl or "conjecture" in nl:
            return EntityType.THEOREM
        if "dataset" in nl or "corpus" in cl:
            return EntityType.DATASET
        if "method" in nl or "framework" in nl:
            return EntityType.METHOD
        if any(w in nl for w in ["zeta", "matrix", "function", "graph", "group", "manifold"]):
            return EntityType.MATHEMATICAL_OBJECT
        return EntityType.CONCEPT
