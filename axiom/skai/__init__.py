"""Scientific Knowledge Acquisition & Intelligence Loop (SKAI)."""

from axiom.skai.bridge import bridge_entity_to_egs, bridge_entity_to_er, bridge_source_to_egs, register_text_source
from axiom.skai.conflicts import detect_conflicts
from axiom.skai.expansion import expand_research_question
from axiom.skai.extractor import extract_document_structure, extract_from_latex, extract_from_text
from axiom.skai.gaps import detect_gaps
from axiom.skai.models import (
    AcquisitionResult,
    EntityType,
    KnowledgeEntity,
    KnowledgeScope,
    RelationType,
    SourceQualityTier,
    SourceType,
)
from axiom.skai.orchestrator import SkaiOrchestrator
from axiom.skai.quality import apply_quality, assess_source_quality
from axiom.skai.retrieval import retrieve_for_research
from axiom.skai.saturation import estimate_coverage
from axiom.skai.store import SkaiStore, get_skai_store

__all__ = [
    "AcquisitionResult",
    "EntityType",
    "KnowledgeEntity",
    "KnowledgeScope",
    "RelationType",
    "SkaiOrchestrator",
    "SkaiStore",
    "SourceQualityTier",
    "SourceType",
    "apply_quality",
    "assess_source_quality",
    "bridge_entity_to_egs",
    "bridge_entity_to_er",
    "bridge_source_to_egs",
    "detect_conflicts",
    "detect_gaps",
    "estimate_coverage",
    "expand_research_question",
    "extract_document_structure",
    "extract_from_latex",
    "extract_from_text",
    "get_skai_store",
    "register_text_source",
    "retrieve_for_research",
]
