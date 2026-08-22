"""Tests for Phase 13 — End-to-End Scientific Research Workflow Pipeline."""
import pytest
from axiom.research_pipeline.models import (
    ResearchQuestion,
    SourceDocument,
    SourceType,
    FinalResearchArtifact,
)
from axiom.research_pipeline.planner import ResearchPlanner
from axiom.research_pipeline.ingestion import IngestionEngine
from axiom.research_pipeline.pipeline import ResearchPipeline


def test_research_planner():
    planner = ResearchPlanner()
    q = ResearchQuestion(question="Quantum Error Correction")
    plan = planner.create_plan(q)
    queries = planner.generate_queries(plan)

    assert len(plan.sub_questions) == 3
    assert len(queries.queries) == 6
    assert plan.question_id == q.id


def test_ingestion_normalization_and_deduplication():
    doc1 = SourceDocument(url="https://a.org/1", title="Doc 1", source_type=SourceType.PAPER)
    doc2 = SourceDocument(url="https://a.org/2", title="Doc 2", source_type=SourceType.PAPER)

    html1 = "<html><body><h1>Doc 1</h1><p>Quantum error correction code.</p></body></html>"
    html2 = "<html><body><h1>Doc 1</h1><p>Quantum error correction code.</p></body></html>"

    ext1 = IngestionEngine.extract_text(doc1, html1)
    ext2 = IngestionEngine.extract_text(doc2, html2)

    norm1 = IngestionEngine.normalize_source(doc1, ext1)
    norm2 = IngestionEngine.normalize_source(doc2, ext2)

    deduped, dup_count = IngestionEngine.deduplicate_sources([norm1, norm2])

    assert dup_count == 1
    assert len(deduped) == 1
    assert norm1.content_hash == norm2.content_hash


def test_full_13_stage_pipeline_execution():
    pipeline = ResearchPipeline()
    artifact = pipeline.run_pipeline("Quantum Error Correction Surface Codes")

    assert isinstance(artifact, FinalResearchArtifact)
    assert artifact.total_sources_used == 3
    assert len(artifact.claims) > 0
    assert all(len(c.citations) > 0 for c in artifact.claims)
    assert "Surface Codes" in artifact.title or "Quantum Error Correction" in artifact.executive_summary
