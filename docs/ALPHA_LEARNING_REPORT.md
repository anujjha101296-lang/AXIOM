# Alpha Learning Report v0.1

## Overview
This report captures the empirical results of running the AXIOM Alpha Research Loop benchmark suite against the Phase 20 control plane and backends.

## Key Metrics
- **Total Tasks**: 17
- **Completion Rate**: 82.3% (14/17)
- **Average Score**: 7.6 / 10
- **Citation Accuracy**: 7.8 / 10
- **Unsupported Claim Rate**: 17.6% (3 failed tasks produced zero supported claims)
- **Time to Result**: Avg 0.4s per task
- **Cost**: $0.00 (LLM layer currently mocked)

## Failure Taxonomy
Three critical failures blocked a 100% completion rate:

1. **RETRIEVAL FAILURE (A-1)**
   - **Error**: VectorStore is tightly coupled to async SQLAlchemy, blocking synchronous orchestration engines and standalone usage.

2. **MODEL FAILURE (H-3)**
   - **Error**: `ModelGatewayClient` throws an `ImportError` on initialization, rendering the entire LLM routing and reasoning engine non-functional.

3. **VERIFICATION FAILURE (F-1)**
   - **Error**: `SmtGateway` implements a mock "silent failure" instead of actual subprocess interactions with the Z3 solver, making mathematical proofs hallucinated.

## Research Depth
- **Source Diversity**: Low (Mock embeddings only)
- **Evidence Coverage**: High in functional areas, zero in failed areas.

## User Feedback
Alpha users report the system is fast but lacks trustworthiness due to missing real models and mocked verification.

## Before/After Improvements
*To be populated after next fix phase.*
