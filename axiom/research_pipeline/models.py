"""Data models for Phase 13 Research Pipeline.

Covers all 13 pipeline stages:
RESEARCH QUESTION -> RESEARCH PLANNER -> SEARCH QUERIES -> WEB / PAPER / DATA SOURCES
-> FETCH + EXTRACT -> SOURCE NORMALIZATION -> DEDUPLICATION -> RELEVANCE FILTERING
-> STORE AS EVIDENCE -> RETRIEVAL -> MULTI-AGENT ANALYSIS -> CLAIMS + CITATIONS + PROVENANCE
-> FINAL RESEARCH ARTIFACT
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    WEB = "WEB"
    PAPER = "PAPER"
    DATASET = "DATASET"
    INTERNAL_DOC = "INTERNAL_DOC"


class ResearchQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    project_id: str = "default"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ResearchPlan(BaseModel):
    question_id: str
    sub_questions: List[str]
    target_domains: List[str]
    required_source_types: List[SourceType]


class SearchQuery(BaseModel):
    query: str
    target_source_type: SourceType
    sub_question: str


class QuerySet(BaseModel):
    question_id: str
    queries: List[SearchQuery]


class SourceDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    title: str
    source_type: SourceType
    canonical_url: Optional[str] = None


class ExtractedText(BaseModel):
    source_id: str
    raw_html_or_pdf: str
    clean_text: str
    word_count: int


class NormalizedSource(BaseModel):
    source_id: str
    title: str
    normalized_text: str
    content_hash: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FilteredEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    content: str
    relevance_score: float
    is_duplicate: bool = False


class EvidencePacket(BaseModel):
    question_id: str
    evidences: List[FilteredEvidence]
    total_sources_evaluated: int
    deduplicated_count: int


class ProvenanceCitation(BaseModel):
    citation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_id: str
    source_id: str
    canonical_url: str
    cited_text_snippet: str


class Claim(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str
    confidence: float
    citations: List[ProvenanceCitation]


class FinalResearchArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    title: str
    executive_summary: str
    claims: List[Claim]
    methodology_notes: str
    total_sources_used: int
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
