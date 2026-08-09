"""SKAI orchestrator — full knowledge acquisition loop (SKAI §1, §20)."""

from __future__ import annotations

from typing import Any

from axiom.core.events.bus import Topics, event_bus
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.evidence.registry import ClaimRegistry
from axiom.skai.bridge import bridge_entity_to_egs, bridge_entity_to_er, bridge_source_to_egs, register_text_source
from axiom.skai.citation_graph import build_citation_relations
from axiom.skai.conflicts import detect_conflicts
from axiom.skai.expansion import expand_research_question
from axiom.skai.extractor import extract_document_structure
from axiom.skai.gaps import detect_gaps
from axiom.skai.models import (
    AcquisitionResult,
    KnowledgeEntity,
    KnowledgeRelation,
    KnowledgeScope,
    RelationType,
    SourceType,
    _new_id,
)
from axiom.skai.quality import apply_quality
from axiom.skai.retrieval import retrieve_for_research
from axiom.skai.saturation import estimate_coverage
from axiom.skai.store import SkaiStore, get_skai_store


class SkaiOrchestrator:
    """
    Scientific Knowledge Acquisition & Intelligence Loop.

    Research changes the knowledge base; the knowledge base changes future research.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = get_skai_store(db_path)
        self.egs = EpistemicStore(db_path)
        self.claims = ClaimRegistry(db_path)

    def acquire_from_text(
        self,
        title: str,
        content: str,
        *,
        research_question: str = "",
        source_type: SourceType = SourceType.RESEARCHER_DOCUMENT,
        identifier: str | None = None,
        is_latex: bool = False,
        campaign_id: str | None = None,
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
        bridge_to_egs: bool = True,
        bridge_to_er: bool = True,
    ) -> AcquisitionResult:
        """Full acquisition pipeline: source → extract → graph → conflicts → gaps."""
        source = register_text_source(
            title, content,
            source_type=source_type,
            identifier=identifier,
            extraction_method="latex" if is_latex else "text",
            campaign_id=campaign_id,
            scope=scope.value,
        )
        source.scope = scope
        self.store.save_source(source)

        extraction = extract_document_structure(content, source.source_id, is_latex=is_latex)
        entity_ids: list[str] = []
        egs_paper_id: str | None = None

        if bridge_to_egs:
            egs_paper_id = bridge_source_to_egs(self.egs, source)

        for entity in extraction["entities"]:
            entity.scope = scope
            entity.campaign_id = campaign_id
            self.store.save_entity(entity)
            entity_ids.append(entity.entity_id)

            if bridge_to_egs and egs_paper_id:
                bridge_entity_to_egs(self.egs, entity, egs_paper_id)
            if bridge_to_er:
                bridge_entity_to_er(self.claims, entity, source, campaign_id=campaign_id)

        relation_ids: list[str] = []
        if extraction.get("citation_keys"):
            rels = build_citation_relations(self.store, source.source_id, extraction["citation_keys"])
            relation_ids = [r.relation_id for r in rels]

        conflicts = detect_conflicts(self.store)
        gaps = detect_gaps(self.store, campaign_id=campaign_id)
        coverage = estimate_coverage(self.store, research_question or title)
        expanded = expand_research_question(research_question or title)

        try:
            event_bus.publish(Topics.PAPER_INGESTED, {"source_id": source.source_id, "title": title})
            event_bus.publish(Topics.GRAPH_UPDATED, {"entity_count": len(entity_ids)})
        except Exception:
            pass

        result = AcquisitionResult(
            acquisition_id=_new_id("acq"),
            research_question=research_question or title,
            sources=[source.source_id],
            entities=entity_ids,
            relations=relation_ids,
            conflicts=[c.conflict_id for c in conflicts],
            gaps=[g.gap_id for g in gaps],
            coverage=coverage,
            expanded_questions=expanded,
        )
        return result

    def acquire_for_campaign(
        self,
        research_question: str,
        *,
        campaign_id: str,
        content: str | None = None,
        title: str = "Campaign literature synthesis",
    ) -> AcquisitionResult:
        """Literature acquisition for FRCE campaign cycles."""
        if content:
            return self.acquire_from_text(
                title, content,
                research_question=research_question,
                campaign_id=campaign_id,
                scope=KnowledgeScope.CAMPAIGN,
            )

        # Synthesize from existing knowledge + expanded questions
        expanded = expand_research_question(research_question)
        coverage = estimate_coverage(self.store, research_question, strategies_used=["direct_search"])
        gaps = detect_gaps(self.store, campaign_id=campaign_id)

        return AcquisitionResult(
            acquisition_id=_new_id("acq"),
            research_question=research_question,
            gaps=[g.gap_id for g in gaps],
            coverage=coverage,
            expanded_questions=expanded,
            status="planned",
        )

    def synthesize_knowledge(self, research_question: str, *, campaign_id: str | None = None) -> dict[str, Any]:
        """Produce knowledge synthesis for a research question."""
        retrieval = retrieve_for_research(
            self.store, research_question, campaign_id=campaign_id,
        )
        coverage = estimate_coverage(self.store, research_question)
        gaps = detect_gaps(self.store, campaign_id=campaign_id)
        conflicts = detect_conflicts(self.store)

        return {
            "research_question": research_question,
            "retrieval": retrieval,
            "coverage": coverage.to_dict(),
            "gaps": [g.to_dict() for g in gaps],
            "conflicts": [c.to_dict() for c in conflicts],
            "graph_summary": self.store.graph_summary(),
            "synthesis_note": "Computational synthesis — not established scientific fact",
        }

    def propagate_reliability(self, disproved_entity_id: str) -> list[str]:
        """If claim A disproved, reassess dependents (SKAI §13)."""
        reassess: list[str] = []
        for rel in self.store.list_relations(entity_id=disproved_entity_id):
            if rel.relation_type in (RelationType.DEPENDS_ON, RelationType.SUPPORTS, RelationType.PROVES):
                dependent = self.store.get_entity(rel.target_entity_id)
                if dependent:
                    dependent.verification_status = "reassess"
                    dependent.confidence = max(0.0, dependent.confidence - 0.3)
                    self.store.save_entity(dependent)
                    reassess.append(dependent.entity_id)
        return reassess

    def manifest(self) -> dict[str, Any]:
        return {
            "name": "AXIOM Scientific Knowledge Acquisition & Intelligence Loop",
            "version": "1.0",
            "capabilities": [
                "multi_channel_source_acquisition",
                "source_quality_assessment",
                "structure_extraction",
                "citation_graph",
                "conflict_detection",
                "research_gap_detection",
                "literature_saturation",
                "reasoning_aware_retrieval",
                "knowledge_versioning",
                "egs_er_bridge",
                "scope_isolation",
            ],
            "integrations": ["EGS", "E&R", "FRCE", "Research Workspace"],
            "principles": [
                "Never store paragraphs without provenance",
                "Source quality is explicit metadata",
                "Unresolved conflicts become research tasks",
                "Never silently rewrite historical knowledge",
                "Weak claims never become trusted through repetition",
            ],
            "graph_summary": self.store.graph_summary(),
        }
