#!/usr/bin/env python3
"""Phase 13 Benchmark — 13-Stage Autonomous Research Pipeline.

Runs 8 deterministic benchmarks covering:
- BM1: Research question plan decomposition
- BM2: Search query generation
- BM3: Fetch & text extraction (HTML stripping)
- BM4: Source normalization & SHA-256 content hashing
- BM5: Content-hash exact deduplication
- BM6: Relevance threshold filtering
- BM7: Multi-agent synthesis & claim-citation provenance binding
- BM8: End-to-end 13-stage pipeline execution & artifact output

Run: EMBEDDING_PROVIDER=test ENVIRONMENT=development python benchmarks/phase13_pipeline_benchmark.py
"""
import json, time, sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.research_pipeline.models import (
    ResearchQuestion,
    SourceDocument,
    SourceType,
)
from axiom.research_pipeline.planner import ResearchPlanner
from axiom.research_pipeline.ingestion import IngestionEngine
from axiom.research_pipeline.analysis_engine import MultiAgentAnalysisEngine
from axiom.research_pipeline.pipeline import ResearchPipeline


def run_benchmarks():
    planner = ResearchPlanner()
    ingestion = IngestionEngine()
    analyzer = MultiAgentAnalysisEngine()
    results = []

    print("=" * 65)
    print("AXIOM PHASE 13 — RESEARCH PIPELINE BENCHMARKS")
    print("=" * 65)

    # BM1: Plan Decomposition
    t0 = time.time()
    q = ResearchQuestion(question="CRISPR Gene Editing Off-Target Reduction")
    plan = planner.create_plan(q)
    bm1_ok = len(plan.sub_questions) >= 3
    results.append({
        "benchmark_id": "BM1",
        "name": "Research Plan Decomposition",
        "passed": bm1_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm1_ok else 'FAILED'}] BM1: Plan Decomposition ({results[-1]['time_ms']} ms)")

    # BM2: Search Query Generation
    t0 = time.time()
    queries = planner.generate_queries(plan)
    bm2_ok = len(queries.queries) >= 6
    results.append({
        "benchmark_id": "BM2",
        "name": "Search Query Generation",
        "passed": bm2_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm2_ok else 'FAILED'}] BM2: Query Generation ({results[-1]['time_ms']} ms)")

    # BM3: Fetch & Extract
    t0 = time.time()
    doc = SourceDocument(url="https://nature.com/crispr", title="CRISPR Study", source_type=SourceType.PAPER)
    raw_html = "<html><body><h1>CRISPR</h1><p>Engineered Cas9 variants reduce off-target edits.</p></body></html>"
    extracted = ingestion.extract_text(doc, raw_html)
    bm3_ok = "Engineered Cas9" in extracted.clean_text and "<p>" not in extracted.clean_text
    results.append({
        "benchmark_id": "BM3",
        "name": "Fetch & Text Extraction",
        "passed": bm3_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm3_ok else 'FAILED'}] BM3: Text Extraction ({results[-1]['time_ms']} ms)")

    # BM4: Normalization & Hashing
    t0 = time.time()
    normalized = ingestion.normalize_source(doc, extracted)
    bm4_ok = len(normalized.content_hash) == 64 and normalized.normalized_text.islower()
    results.append({
        "benchmark_id": "BM4",
        "name": "Source Normalization & Hashing",
        "passed": bm4_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm4_ok else 'FAILED'}] BM4: Normalization & Hashing ({results[-1]['time_ms']} ms)")

    # BM5: Deduplication
    t0 = time.time()
    deduped, dup_cnt = ingestion.deduplicate_sources([normalized, normalized])
    bm5_ok = len(deduped) == 1 and dup_cnt == 1
    results.append({
        "benchmark_id": "BM5",
        "name": "Exact Content-Hash Deduplication",
        "passed": bm5_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm5_ok else 'FAILED'}] BM5: Deduplication ({results[-1]['time_ms']} ms)")

    # BM6: Relevance Filtering
    t0 = time.time()
    evidences = ingestion.filter_relevance(deduped, query="CRISPR Cas9", threshold=0.1)
    bm6_ok = len(evidences) >= 1 and evidences[0].relevance_score > 0
    results.append({
        "benchmark_id": "BM6",
        "name": "Relevance Threshold Filtering",
        "passed": bm6_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm6_ok else 'FAILED'}] BM6: Relevance Filtering ({results[-1]['time_ms']} ms)")

    # BM7: Provenance Binding
    t0 = time.time()
    pipeline = ResearchPipeline()
    artifact = pipeline.run_pipeline("CRISPR Cas9 Editing")
    bm7_ok = len(artifact.claims) > 0 and len(artifact.claims[0].citations) > 0
    results.append({
        "benchmark_id": "BM7",
        "name": "Provenance Citation Binding",
        "passed": bm7_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm7_ok else 'FAILED'}] BM7: Citation Provenance Binding ({results[-1]['time_ms']} ms)")

    # BM8: End-to-End Execution
    t0 = time.time()
    final_art = pipeline.run_pipeline("High-Temperature Superconductivity Mechanisms")
    bm8_ok = final_art.total_sources_used >= 3 and len(final_art.claims) > 0
    results.append({
        "benchmark_id": "BM8",
        "name": "End-to-End 13-Stage Pipeline Execution",
        "passed": bm8_ok,
        "time_ms": round((time.time() - t0) * 1000, 2),
    })
    print(f"  [{'PASSED' if bm8_ok else 'FAILED'}] BM8: End-to-End Pipeline Execution ({results[-1]['time_ms']} ms)")

    total_passed = sum(1 for r in results if r["passed"])
    summary = {
        "benchmark_suite": "phase13_research_pipeline",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_benchmarks": len(results),
        "passed_benchmarks": total_passed,
        "all_passed": total_passed == len(results),
        "benchmarks": results,
    }

    out_dir = Path(__file__).parent.parent / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase13_pipeline_benchmark.json"
    out_path.write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 65)
    print(f"BENCHMARK RESULT: {total_passed}/{len(results)} PASSED")
    print(f"Saved to: {out_path}")
    print("=" * 65)
    return summary


if __name__ == "__main__":
    run_benchmarks()
