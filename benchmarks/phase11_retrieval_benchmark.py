#!/usr/bin/env python3
"""Phase 11 Retrieval Benchmark

Measures semantic retrieval quality using deterministic MockEmbeddingProvider.
Tests whether topic-relevant documents rank higher than irrelevant ones.

Run: EMBEDDING_PROVIDER=test ENVIRONMENT=test python benchmarks/phase11_retrieval_benchmark.py
"""
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

os.environ.setdefault("EMBEDDING_PROVIDER", "test")
os.environ.setdefault("ENVIRONMENT", "test")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.research.chunking import TextChunker, TextChunk
from axiom.research.embeddings import MockEmbeddingProvider
from axiom.research.vector_store import cosine_similarity

# ── Benchmark Corpus ──────────────────────────────────────────────────────────

DOCS = {
    "biology": {
        "topic": "biology",
        "text": (
            "Ribosomes are the molecular machines responsible for protein synthesis in all living cells. "
            "During translation, messenger RNA carries the genetic code from the nucleus to the ribosome. "
            "Transfer RNAs bring amino acids that are assembled into polypeptide chains following the codons. "
            "The ribosome moves along the mRNA strand reading each codon and catalyzing peptide bond formation. "
            "Eukaryotic ribosomes are larger (80S) than prokaryotic ribosomes (70S) and differ in composition. "
            "Mitochondria contain their own ribosomes similar to bacterial ribosomes reflecting endosymbiotic origin. "
            "Protein folding occurs co-translationally with chaperone proteins preventing misfolding aggregation. "
            "Post-translational modifications include phosphorylation glycosylation and ubiquitination. "
            "The central dogma describes the flow of genetic information from DNA to RNA to protein. "
            "Gene expression is regulated at multiple levels including transcription RNA processing and translation. "
        ),
    },
    "mathematics": {
        "topic": "mathematics",
        "text": (
            "The Riemann Hypothesis concerns the distribution of non-trivial zeros of the Riemann zeta function. "
            "The hypothesis states that all non-trivial zeros have real part equal to one-half. "
            "The zeta function is defined as the sum of n to the power negative s for all positive integers n. "
            "Euler showed the connection between the zeta function and the distribution of prime numbers. "
            "The prime number theorem describes the asymptotic density of primes using the logarithmic integral. "
            "The analytic continuation extends the zeta function to all complex numbers except s equals one. "
            "The functional equation relates the value at s to the value at one minus s via gamma function. "
            "Random matrix theory has revealed surprising connections to the distribution of zeta zeros. "
            "Hardy proved infinitely many zeros lie on the critical line using the Hardy Z function. "
            "The Generalized Riemann Hypothesis extends the conjecture to Dirichlet L-functions. "
        ),
    },
    "computer_science": {
        "topic": "computer_science",
        "text": (
            "Cache coherence protocols ensure that shared memory remains consistent across multiple CPU cores. "
            "MESI protocol defines four states: Modified Exclusive Shared and Invalid for each cache line. "
            "When a processor writes to a shared cache line it must invalidate copies in other caches. "
            "Snooping protocols use the memory bus to broadcast cache state changes to all processors. "
            "Directory-based protocols use a centralized directory to track which caches hold each line. "
            "False sharing occurs when unrelated variables share a cache line causing unnecessary invalidations. "
            "Non-uniform memory access architecture places memory closer to specific processor groups. "
            "Memory barriers and fences enforce ordering constraints on memory operations across cores. "
            "Load-store queues buffer pending memory operations before they are committed to the cache hierarchy. "
            "Branch prediction reduces pipeline stalls by speculating on the outcome of conditional branches. "
        ),
    },
}

QUERIES = {
    "biology": "protein synthesis ribosomes genetic translation",
    "mathematics": "Riemann zeta function prime numbers critical line",
    "computer_science": "cache coherence CPU memory protocol MESI",
}


def build_chunk_index(
    provider: MockEmbeddingProvider,
    chunker: TextChunker,
) -> Dict[str, Dict]:
    """Chunk all documents and embed them into an in-memory index."""
    index = {}  # chunk_id -> {doc_topic, content, vector}
    for doc_id, doc in DOCS.items():
        chunks: List[TextChunk] = chunker.chunk(
            doc["text"], document_id=doc_id, project_id="benchmark"
        )
        if not chunks:
            continue
        texts = [c.content for c in chunks]
        vectors = provider.embed_batch(texts)
        for chunk, vec in zip(chunks, vectors):
            cid = f"{doc_id}_{chunk.chunk_index}"
            index[cid] = {
                "doc_topic": doc["topic"],
                "content": chunk.content,
                "vector": vec,
            }
    return index


def search(
    index: Dict[str, Dict],
    query_vector: List[float],
    top_k: int = 3,
) -> List[Tuple[float, str, str]]:
    """Return top_k (score, chunk_id, doc_topic) sorted by cosine similarity."""
    scored = []
    for cid, entry in index.items():
        score = cosine_similarity(query_vector, entry["vector"])
        scored.append((score, cid, entry["doc_topic"]))
    scored.sort(reverse=True)
    return scored[:top_k]


def run_benchmark() -> Dict:
    provider = MockEmbeddingProvider()
    chunker = TextChunker(chunk_size=300, chunk_overlap=30)

    print("Building chunk index...")
    index = build_chunk_index(provider, chunker)
    print(f"  Total chunks: {len(index)}")

    results = {}
    for query_topic, query_text in QUERIES.items():
        query_vec = provider.embed_batch([query_text])[0]
        top = search(index, query_vec, top_k=3)

        hits = [entry[2] for entry in top]  # doc_topics
        p_at_1 = 1.0 if hits and hits[0] == query_topic else 0.0
        p_at_3 = sum(1 for h in hits[:3] if h == query_topic) / 3.0

        results[query_topic] = {
            "query": query_text,
            "top_3": [
                {"rank": i + 1, "chunk_id": cid, "doc_topic": topic, "score": round(score, 6)}
                for i, (score, cid, topic) in enumerate(top)
            ],
            "precision_at_1": p_at_1,
            "precision_at_3": round(p_at_3, 4),
            "correct_topic_in_top_1": hits[0] == query_topic if hits else False,
        }

    mean_p1 = sum(r["precision_at_1"] for r in results.values()) / len(results)
    mean_p3 = sum(r["precision_at_3"] for r in results.values()) / len(results)

    report = {
        "benchmark": "phase11_retrieval",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": "MockEmbeddingProvider",
        "total_chunks": len(index),
        "queries": len(QUERIES),
        "mean_precision_at_1": round(mean_p1, 4),
        "mean_precision_at_3": round(mean_p3, 4),
        "results": results,
    }
    return report


def main():
    report = run_benchmark()

    out_dir = Path(__file__).parent.parent / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase11_retrieval_benchmark.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("PHASE 11 RETRIEVAL BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Provider      : {report['provider']}")
    print(f"Total Chunks  : {report['total_chunks']}")
    print(f"Mean P@1      : {report['mean_precision_at_1']:.4f}")
    print(f"Mean P@3      : {report['mean_precision_at_3']:.4f}")
    print()
    for topic, res in report["results"].items():
        top1 = res["top_3"][0] if res["top_3"] else {}
        marker = "✓" if res["correct_topic_in_top_1"] else "✗"
        print(f"  [{marker}] Query '{topic}' → top-1 doc_topic='{top1.get('doc_topic','?')}' score={top1.get('score', 0):.4f}  P@1={res['precision_at_1']:.2f}  P@3={res['precision_at_3']:.2f}")

    print()
    print(f"Results saved: {out_path}")
    return report


if __name__ == "__main__":
    main()
