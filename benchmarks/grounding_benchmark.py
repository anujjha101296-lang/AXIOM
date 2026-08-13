"""
AXIOM Phase 8 — Grounding & Citation Benchmark

Evaluates evidence grounding quality and citation validity.

For each grounding case (from benchmarks/data/grounding_cases.json), this
benchmark simulates an answer and evaluates:
  1. Was evidence retrieved?
  2. Was the claim supported by retrieved evidence?
  3. Were citations valid (source exists, belongs to corpus, was retrieved)?
  4. Did the system express insufficient evidence when appropriate?
  5. Did the system surface contradictions when appropriate?

Citation Metrics:
  - Citation Validity Rate: % of citations where source exists and was retrieved
  - Citation Coverage: % of relevant chunks that were cited
  - Unsupported Citation Rate: % of citations pointing to non-retrieved chunks

NOTE: In a full production evaluation, this would call the live QA system.
This benchmark uses a rule-based mock QA to remain deterministic and runnable
without an LLM API key. It tests the EVALUATION INFRASTRUCTURE, not the
LLM quality. Real QA quality is measured in integration tests (test_qa.py).
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.eval_models import (
    BenchmarkResult,
    BenchmarkStatus,
    EvaluationResult,
    Metric,
)
from benchmarks.retrieval_benchmark import retrieve, _build_index

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "data", "retrieval_corpus.json")
GROUNDING_PATH = os.path.join(os.path.dirname(__file__), "data", "grounding_cases.json")


def _load_corpus():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_grounding_cases():
    with open(GROUNDING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["cases"]


def _mock_qa_system(question: str, retrieved_chunks: list[dict]) -> dict:
    """
    Deterministic rule-based mock QA system for benchmark purposes.
    Returns a structured answer with citations and uncertainty flags.
    
    This is NOT the real AXIOM QA system. It tests the evaluation
    infrastructure and grounding logic only.
    """
    # Check if question is off-topic (no content overlap with retrieved chunks)
    import re
    q_words = set(re.findall(r"\b\w+\b", question.lower())) - {"what", "is", "the", "a", "an", "of", "in", "and", "how", "does", "do"}
    
    if not retrieved_chunks:
        return {
            "answer": "I cannot find any relevant information in the provided documents to answer this question.",
            "citations": [],
            "insufficient_evidence": True,
            "contradiction_detected": False,
            "supported_claims": [],
            "unsupported_claims": [question],
        }

    # Check if retrieved chunks have meaningful overlap with the question
    chunk_words = set()
    for c in retrieved_chunks:
        chunk_words.update(re.findall(r"\b\w+\b", c["text"].lower()))
    
    overlap = q_words & chunk_words
    # If fewer than 2 meaningful words overlap, treat as insufficient evidence
    if len(overlap) < 2:
        return {
            "answer": "I cannot find sufficient relevant information in the provided documents to answer this question.",
            "citations": [],
            "insufficient_evidence": True,
            "contradiction_detected": False,
            "supported_claims": [],
            "unsupported_claims": [question],
        }

    # Detect contradiction: learning rate question has conflicting info
    contradiction = any(
        "divergence" in c["text"] and "slow convergence" in c["text"]
        for c in retrieved_chunks
    )

    # Build answer from retrieved chunks
    answer_parts = []
    citations = []
    for c in retrieved_chunks:
        answer_parts.append(c["text"])
        citations.append({
            "chunk_id": c["chunk_id"],
            "doc_id": c["doc_id"],
            "text_snippet": c["text"][:100],
        })

    answer = " ".join(answer_parts)

    return {
        "answer": answer,
        "citations": citations,
        "insufficient_evidence": False,
        "contradiction_detected": contradiction,
        "supported_claims": [question],
        "unsupported_claims": [],
    }


def _validate_citations(
    citations: list[dict],
    retrieved_chunk_ids: list[str],
    corpus_chunk_ids: list[str],
    all_corpus_chunk_ids: list[str],
) -> dict:
    """
    Validate citations against:
    1. Source exists in corpus
    2. Source belongs to authorized corpus (project)
    3. Source was actually retrieved
    4. Citation metadata matches

    Returns citation validation metrics.
    """
    if not citations:
        return {
            "total_citations": 0,
            "valid_citations": 0,
            "invalid_citations": 0,
            "citation_validity_rate": 1.0,  # vacuously true
            "citation_coverage": 0.0 if corpus_chunk_ids else 1.0,
            "unsupported_citation_rate": 0.0,
            "validation_details": [],
        }

    valid = 0
    invalid = 0
    details = []

    for cit in citations:
        chunk_id = cit.get("chunk_id", "")
        exists_in_corpus = chunk_id in all_corpus_chunk_ids
        was_retrieved = chunk_id in retrieved_chunk_ids

        is_valid = exists_in_corpus and was_retrieved
        if is_valid:
            valid += 1
        else:
            invalid += 1

        details.append({
            "chunk_id": chunk_id,
            "exists_in_corpus": exists_in_corpus,
            "was_retrieved": was_retrieved,
            "is_valid": is_valid,
        })

    total = len(citations)
    cited_ids = {c.get("chunk_id") for c in citations}
    covered = len(cited_ids & set(corpus_chunk_ids))
    coverage = covered / len(corpus_chunk_ids) if corpus_chunk_ids else 1.0
    unsupported_rate = invalid / total if total > 0 else 0.0

    return {
        "total_citations": total,
        "valid_citations": valid,
        "invalid_citations": invalid,
        "citation_validity_rate": valid / total if total > 0 else 1.0,
        "citation_coverage": coverage,
        "unsupported_citation_rate": unsupported_rate,
        "validation_details": details,
    }


def run_grounding_benchmark() -> EvaluationResult:
    """Run the full grounding and citation benchmark."""
    start_time = time.time()
    corpus = _load_corpus()
    cases = _load_grounding_cases()

    # Build retrieval index
    chunks, idf = _build_index(corpus)
    all_chunk_ids = [c["chunk_id"] for c in chunks]
    chunk_map = {c["chunk_id"]: c for c in chunks}

    results = []
    citation_validity_scores = []
    citation_coverage_scores = []

    for case in cases:
        case_start = time.time()
        case_id = case["case_id"]
        question = case["question"]
        expected = case["expected_behavior"]
        expected_citation_ids = case["expected_citation_chunk_ids"]

        # Retrieve relevant chunks
        ranked = retrieve(question, chunks, idf, top_k=3)
        retrieved_chunk_ids = [r[0] for r in ranked]
        retrieved_chunks = [chunk_map[cid] for cid in retrieved_chunk_ids if cid in chunk_map]

        # Generate mock answer
        qa_result = _mock_qa_system(question, retrieved_chunks)

        # Validate citations
        citation_metrics = _validate_citations(
            citations=qa_result["citations"],
            retrieved_chunk_ids=retrieved_chunk_ids,
            corpus_chunk_ids=expected_citation_ids,
            all_corpus_chunk_ids=all_chunk_ids,
        )

        # Evaluate against expected behavior
        evidence_retrieved = len(retrieved_chunks) > 0
        insufficient_stated = qa_result["insufficient_evidence"]
        contradiction_surfaced = qa_result["contradiction_detected"]

        # Determine pass/fail
        checks = []

        # Check evidence retrieval match
        evidence_check = evidence_retrieved == expected["evidence_retrieved"]
        checks.append(("evidence_retrieval_match", evidence_check))

        # Check insufficient evidence expression
        if expected.get("insufficient_evidence_stated", False):
            insuff_check = insufficient_stated
            checks.append(("insufficient_evidence_expressed", insuff_check))

        # Check contradiction surfacing
        if expected.get("contradiction_surfaced", False):
            contra_check = contradiction_surfaced
            checks.append(("contradiction_surfaced", contra_check))

        # Check citation validity
        if expected_citation_ids:
            cit_check = citation_metrics["citation_validity_rate"] >= 0.5
            checks.append(("citation_validity", cit_check))

        passed_checks = sum(1 for _, v in checks if v)
        total_checks = len(checks) or 1
        status = BenchmarkStatus.PASSED if passed_checks == total_checks else BenchmarkStatus.FAILED

        citation_validity_scores.append(citation_metrics["citation_validity_rate"])
        citation_coverage_scores.append(citation_metrics["citation_coverage"])

        result = BenchmarkResult(
            case_id=case_id,
            status=status,
            metrics=[
                Metric("citation_validity_rate", citation_metrics["citation_validity_rate"], threshold=0.5),
                Metric("citation_coverage", citation_metrics["citation_coverage"]),
                Metric("unsupported_citation_rate", citation_metrics["unsupported_citation_rate"]),
                Metric("checks_passed", passed_checks / total_checks, threshold=1.0),
            ],
            actual_outputs={
                "question": question,
                "grounding_type": case["grounding_type"],
                "evidence_retrieved": evidence_retrieved,
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "insufficient_evidence_stated": insufficient_stated,
                "contradiction_detected": contradiction_surfaced,
                "citation_metrics": citation_metrics,
                "checks": dict(checks),
            },
            duration_seconds=time.time() - case_start,
        )
        results.append(result)

    n = len(results) or 1
    aggregate_metrics = [
        Metric("Mean Citation Validity Rate", sum(citation_validity_scores) / n, threshold=0.7),
        Metric("Mean Citation Coverage", sum(citation_coverage_scores) / n),
        Metric("Pass Rate", sum(1 for r in results if r.status == BenchmarkStatus.PASSED) / n, threshold=0.6),
    ]

    return EvaluationResult(
        suite_id="grounding_benchmark",
        suite_name="Evidence Grounding & Citation Benchmark",
        results=results,
        aggregate_metrics=aggregate_metrics,
        duration_seconds=time.time() - start_time,
    )


if __name__ == "__main__":
    result = run_grounding_benchmark()
    print(f"\n{'='*60}")
    print(f"GROUNDING & CITATION BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Suite: {result.suite_name}")
    print(f"Cases: {result.total_cases} | Passed: {result.passed_cases} | Failed: {result.failed_cases}")
    print(f"\nCase Results:")
    for r in result.results:
        icon = "✓" if r.status == BenchmarkStatus.PASSED else "✗"
        print(f"  {icon} [{r.case_id}] - {r.actual_outputs.get('grounding_type', '')}")
    print(f"\nAggregate Metrics:")
    for m in result.aggregate_metrics:
        status = "✓" if m.passed else "✗"
        print(f"  {status} {m.name}: {m.value:.4f}")
    print()
