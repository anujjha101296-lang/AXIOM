"""Bridge SKAI ↔ EGS ↔ E&R ↔ Research workspace (SKAI §3, §18)."""

from __future__ import annotations

from typing import Any

from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import Edge, EdgeType, MathematicalClaimNode, PaperNode
from axiom.evidence.models import EvidenceType
from axiom.evidence.registry import ClaimRegistry
from axiom.skai.models import EntityType, KnowledgeEntity, SourceProvenance, SourceType, _new_id
from axiom.skai.quality import apply_quality


ENTITY_TO_EGS: dict[EntityType, str] = {
    EntityType.THEOREM: "MATHEMATICAL_CLAIM",
    EntityType.LEMMA: "MATHEMATICAL_CLAIM",
    EntityType.DEFINITION: "DEFINITION",
    EntityType.CONJECTURE: "CONJECTURE",
    EntityType.OPEN_QUESTION: "OPEN_PROBLEM",
}


def bridge_source_to_egs(
    egs: EpistemicStore,
    source: SourceProvenance,
) -> str:
    """Register source as EGS PaperNode."""
    node_id = source.identifier or source.source_id
    paper = PaperNode(
        id=node_id,
        name=source.title,
        arxiv_id=source.identifier if source.source_type == SourceType.PREPRINT else None,
        doi=source.identifier if source.metadata.get("doi") else None,
        published_date=source.published_date,
        metadata={
            "skai_source_id": source.source_id,
            "quality_tier": source.quality_tier.value,
            "reliability_score": source.reliability_score,
            "extraction_method": source.extraction_method,
            "content_hash": source.content_hash,
        },
    )
    egs.add_node(paper)
    return node_id


def bridge_entity_to_egs(
    egs: EpistemicStore,
    entity: KnowledgeEntity,
    egs_paper_id: str,
) -> str:
    """Register extracted entity in EGS."""
    from axiom.core.knowledge_graph.schema import EpistemicStatus, VerificationTier

    node_id = entity.egs_node_id or f"skai_{entity.entity_id}"
    claim = MathematicalClaimNode(
        id=node_id,
        name=entity.title,
        statement=entity.statement,
        status=EpistemicStatus.CONJECTURED,
        tier=VerificationTier.TIER_0_CONJECTURE,
        metadata={"skai_entity_id": entity.entity_id, "entity_type": entity.entity_type.value},
    )
    egs.add_node(claim)
    egs.add_edge(Edge(
        source_id=egs_paper_id,
        target_id=node_id,
        type=EdgeType.PROVES,
        provenance={"origin": "skai_extraction"},
    ))
    entity.egs_node_id = node_id
    return node_id


def bridge_entity_to_er(
    registry: ClaimRegistry,
    entity: KnowledgeEntity,
    source: SourceProvenance,
    *,
    campaign_id: str | None = None,
) -> str:
    """Register entity as E&R claim with quotation evidence."""
    from axiom.evidence.models import ClaimStatus

    claim = registry.register_claim(
        entity.statement,
        campaign_id=campaign_id or entity.campaign_id,
        status=ClaimStatus.SPECULATIVE,
    )
    er_source = registry.register_source(
        title=source.title,
        authors=source.authors,
        content_hash=source.content_hash,
        extraction_method=source.extraction_method,
        metadata={
            "skai_source_id": source.source_id,
            "quality_tier": source.quality_tier.value,
            "source_type": source.source_type.value,
        },
    )
    registry.add_evidence(
        claim.claim_id,
        EvidenceType.QUOTATION,
        summary=entity.statement[:500],
        source_id=er_source.source_id,
        supports=True,
    )
    entity.claim_id = claim.claim_id
    return claim.claim_id


def register_text_source(
    title: str,
    content: str,
    *,
    source_type: SourceType = SourceType.RESEARCHER_DOCUMENT,
    identifier: str | None = None,
    extraction_method: str = "text",
    campaign_id: str | None = None,
    scope: str = "global",
) -> SourceProvenance:
    """Create a source with full provenance from text content."""
    from axiom.skai.extractor import content_hash
    from axiom.skai.models import KnowledgeScope

    source = SourceProvenance(
        source_id=_new_id("src"),
        source_type=source_type,
        title=title,
        identifier=identifier,
        content_hash=content_hash(content),
        extraction_method=extraction_method,
        scope=KnowledgeScope(scope),
        campaign_id=campaign_id,
        metadata={"content_length": len(content)},
    )
    return apply_quality(source)
