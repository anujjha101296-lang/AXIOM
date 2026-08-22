# AXIOM Phase 13 — End-to-End Autonomous Scientific Research Pipeline

## Overview

Phase 13 implements a complete 13-stage autonomous scientific research pipeline. It transforms raw research questions into grounded, provenance-bound scientific artifacts through structured planning, query decomposition, HTML/PDF extraction, lowercasing/hashing normalization, exact deduplication, relevance filtering, multi-agent evidence synthesis, and claim-citation binding.

---

## 13-Stage Execution Flow

```
RESEARCH QUESTION
       ↓
RESEARCH PLANNER
       ↓
SEARCH QUERIES
       ↓
WEB / PAPER / DATA SOURCES
       ↓
FETCH + EXTRACT
       ↓
SOURCE NORMALIZATION
       ↓
DEDUPLICATION
       ↓
RELEVANCE FILTERING
       ↓
STORE AS EVIDENCE
       ↓
RETRIEVAL
       ↓
MULTI-AGENT ANALYSIS
       ↓
CLAIMS + CITATIONS + PROVENANCE
       ↓
FINAL RESEARCH ARTIFACT
```

---

## Component Architecture

1. **`axiom/research_pipeline/models.py`**: Pydantic v2 models covering all 13 pipeline data structures (`ResearchQuestion`, `ResearchPlan`, `QuerySet`, `SourceDocument`, `ExtractedText`, `NormalizedSource`, `FilteredEvidence`, `EvidencePacket`, `ProvenanceCitation`, `Claim`, `FinalResearchArtifact`).
2. **`axiom/research_pipeline/planner.py`**: Decomposes top-level research questions into targeted sub-questions and structured multi-domain search queries.
3. **`axiom/research_pipeline/ingestion.py`**: Handles HTML/PDF tag stripping, text normalization, SHA-256 content-hash deduplication, and keyword relevance thresholding.
4. **`axiom/research_pipeline/analysis_engine.py`**: Multi-agent evidence synthesis engine that binds claims to precise citations (`canonical_url`, `evidence_id`, `source_id`, `cited_text_snippet`).
5. **`axiom/research_pipeline/pipeline.py`**: Main orchestrator executing the 13 stages sequentially and persisting results to `evaluation_results/phase13/`.
6. **`axiom/services/api_gateway/routes/pipeline.py`**: REST API router mounting `POST /api/v1/research-pipeline/run`.

---

## REST API

### `POST /api/v1/research-pipeline/run`
Executes an autonomous 13-stage research cycle.

**Request:**
```json
{
  "question": "Quantum Error Correction Surface Codes",
  "simulated_sources": [
    {
      "url": "https://arxiv.org/abs/2401.00001",
      "title": "Quantum Error Correction Surface Codes",
      "source_type": "PAPER",
      "canonical_url": "https://arxiv.org/abs/2401.00001"
    }
  ]
}
```

**Response:**
```json
{
  "artifact_id": "...",
  "question_id": "...",
  "title": "Research Artifact: Quantum Error Correction Surface Codes",
  "executive_summary": "...",
  "claims": [
    {
      "claim_id": "...",
      "statement": "...",
      "confidence": 0.95,
      "citations": [
        {
          "citation_id": "...",
          "evidence_id": "...",
          "source_id": "...",
          "canonical_url": "https://arxiv.org/abs/2401.00001",
          "cited_text_snippet": "..."
        }
      ]
    }
  ],
  "methodology_notes": "Sequential 13-stage autonomous pipeline execution with provenance-bound citations.",
  "total_sources_used": 1
}
```

---

## Verification & Testing

```bash
# Run unit tests
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python -m pytest tests/test_phase13_pipeline.py -v

# Run 8-suite benchmark
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python benchmarks/phase13_pipeline_benchmark.py
```
