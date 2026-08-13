"""
AXIOM Phase 8 — Retrieval Benchmark

Evaluates retrieval quality using the deterministic corpus in
benchmarks/data/retrieval_corpus.json.

Metrics computed:
  - Hit@1, Hit@3, Hit@5: Was the correct chunk in the top-K results?
  - Recall@K: Fraction of relevant chunks found in top-K
  - MRR (Mean Reciprocal Rank): Where did the first correct chunk appear?

This benchmark uses cosine similarity on TF-IDF vectors (no external API
required) to ensure fully deterministic, reproducible results.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import defaultdict
from typing import Optional

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.eval_models import (
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkStatus,
    EvaluationResult,
    Metric,
)

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "data", "retrieval_corpus.json")


# ── TF-IDF retrieval (no external dependencies) ──────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    import re
    return re.findall(r"\b\w+\b", text.lower())


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    counts: dict[str, int] = defaultdict(int)
    for t in tokens:
        counts[t] += 1
    total = len(tokens) or 1
    return {t: c / total for t, c in counts.items()}


def _build_index(corpus: dict) -> tuple[list[dict], dict[str, float]]:
    """Build TF-IDF index over all chunks. Returns (chunk_docs, idf_map)."""
    chunks = []
    for doc in corpus["corpus"]:
        for chunk in doc["chunks"]:
            tokens = _tokenize(chunk["text"])
            chunks.append({
                "chunk_id": chunk["chunk_id"],
                "doc_id": doc["id"],
                "text": chunk["text"],
                "tokens": tokens,
                "tf": _compute_tf(tokens),
            })

    # Compute IDF
    n = len(chunks)
    df: dict[str, int] = defaultdict(int)
    for c in chunks:
        for term in set(c["tokens"]):
            df[term] += 1
    idf = {term: math.log((n + 1) / (count + 1)) + 1 for term, count in df.items()}
    return chunks, idf


def _tfidf_vector(tf: dict[str, float], idf: dict[str, float]) -> dict[str, float]:
    return {term: tf_val * idf.get(term, 1.0) for term, tf_val in tf.items()}


def _cosine_similarity(v1: dict[str, float], v2: dict[str, float]) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[t] * v2[t] for t in common)
    norm1 = math.sqrt(sum(x * x for x in v1.values()))
    norm2 = math.sqrt(sum(x * x for x in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def retrieve(query: str, chunks: list[dict], idf: dict[str, float], top_k: int = 5) -> list[tuple[str, float]]:
    """Return top-K chunk IDs ranked by TF-IDF cosine similarity."""
    q_tokens = _tokenize(query)
    q_tf = _compute_tf(q_tokens)
    q_vec = _tfidf_vector(q_tf, idf)

    scored = []
    for chunk in chunks:
        c_vec = _tfidf_vector(chunk["tf"], idf)
        score = _cosine_similarity(q_vec, c_vec)
        scored.append((chunk["chunk_id"], score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# ── Metric computation ────────────────────────────────────────────────────────

def _hit_at_k(ranked: list[str], relevant: list[str], k: int) -> float:
    """1.0 if any relevant chunk is in top-K, else 0.0."""
    top_k_set = set(ranked[:k])
    return 1.0 if top_k_set & set(relevant) else 0.0


def _recall_at_k(ranked: list[str], relevant: list[str], k: int) -> float:
    """Fraction of relevant chunks found in top-K."""
    if not relevant:
        return 1.0
    top_k_set = set(ranked[:k])
    found = len(top_k_set & set(relevant))
    return found / len(relevant)


def _reciprocal_rank(ranked: list[str], relevant: list[str]) -> float:
    """Reciprocal rank of the first relevant result."""
    relevant_set = set(relevant)
    for i, chunk_id in enumerate(ranked, start=1):
        if chunk_id in relevant_set:
            return 1.0 / i
    return 0.0


# ── Main benchmark runner ─────────────────────────────────────────────────────

def run_retrieval_benchmark(top_k: int = 5) -> EvaluationResult:
    """Run the full retrieval benchmark. Returns an EvaluationResult."""
    start_time = time.time()

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    chunks, idf = _build_index(corpus)

    results: list[BenchmarkResult] = []
    hit1_scores, hit3_scores, hit5_scores, recall_scores, mrr_scores = [], [], [], [], []

    for query_data in corpus["queries"]:
        case_start = time.time()
        query_id = query_data["query_id"]
        question = query_data["question"]
        relevant_ids = query_data["relevant_chunk_ids"]

        ranked_results = retrieve(question, chunks, idf, top_k=top_k)
        ranked_ids = [r[0] for r in ranked_results]

        h1 = _hit_at_k(ranked_ids, relevant_ids, 1)
        h3 = _hit_at_k(ranked_ids, relevant_ids, 3)
        h5 = _hit_at_k(ranked_ids, relevant_ids, 5)
        rec = _recall_at_k(ranked_ids, relevant_ids, top_k)
        rr = _reciprocal_rank(ranked_ids, relevant_ids)

        hit1_scores.append(h1)
        hit3_scores.append(h3)
        hit5_scores.append(h5)
        recall_scores.append(rec)
        mrr_scores.append(rr)

        status = BenchmarkStatus.PASSED if h1 > 0 else BenchmarkStatus.FAILED

        result = BenchmarkResult(
            case_id=query_id,
            status=status,
            metrics=[
                Metric("Hit@1", h1, threshold=1.0),
                Metric("Hit@3", h3, threshold=1.0),
                Metric("Hit@5", h5, threshold=1.0),
                Metric("Recall@K", rec, threshold=0.5),
                Metric("MRR", rr, threshold=0.5),
            ],
            actual_outputs={
                "question": question,
                "relevant_chunk_ids": relevant_ids,
                "ranked_chunk_ids": ranked_ids,
                "scores": [(cid, round(score, 4)) for cid, score in ranked_results],
            },
            duration_seconds=time.time() - case_start,
        )
        results.append(result)

    n = len(results) or 1
    aggregate_metrics = [
        Metric("Mean Hit@1", sum(hit1_scores) / n, threshold=0.6),
        Metric("Mean Hit@3", sum(hit3_scores) / n, threshold=0.7),
        Metric("Mean Hit@5", sum(hit5_scores) / n, threshold=0.8),
        Metric("Mean Recall@K", sum(recall_scores) / n, threshold=0.6),
        Metric("MRR", sum(mrr_scores) / n, threshold=0.5),
    ]

    return EvaluationResult(
        suite_id="retrieval_benchmark",
        suite_name="Retrieval Quality Benchmark",
        results=results,
        aggregate_metrics=aggregate_metrics,
        duration_seconds=time.time() - start_time,
    )


if __name__ == "__main__":
    result = run_retrieval_benchmark()
    print(f"\n{'='*60}")
    print(f"RETRIEVAL BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Suite: {result.suite_name}")
    print(f"Cases: {result.total_cases} | Passed: {result.passed_cases} | Failed: {result.failed_cases}")
    print(f"\nAggregate Metrics:")
    for m in result.aggregate_metrics:
        status = "✓" if m.passed else "✗"
        print(f"  {status} {m.name}: {m.value:.4f} (threshold: {m.threshold})")
    print()
