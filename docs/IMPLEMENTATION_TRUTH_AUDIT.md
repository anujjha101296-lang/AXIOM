# Implementation Truth Audit

**Date**: 2026-08-20
**Current Git Commit**: 1c64169 feat: implement controlled multi-agent research system (Phase 9)
**Working Tree State**: Clean (nothing to commit)

## 1. Executive Summary
AXIOM is currently an **Orchestration Façade**. While the API gateway, database schemas, and state-machine orchestrations (task graphs, eval runners) are implemented, the core scientific capabilities—Language Modeling, SMT Verification, Symbolic Math, and Retrieval—are entirely mocked, stubbed, or act as placeholders for Phase 2.

## 2. Capability Implementation Matrix

| Capability | Status | Evidence (File / Function) |
|------------|--------|----------------------------|
| **Authentication / Projects** | REAL | `axiom/services/api_gateway/auth.py` handles real JWTs. `axiom.db` persists users. |
| **LLM Integration** | FAÇADE | `axiom/services/model_gateway/client.py` uses `mock-model` and returns hardcoded text. `axiom/research/llm.py` returns `"Mock Answer"`. |
| **Agent Execution / Roles** | ORCHESTRATION | `axiom/multi_agent/roles/base.py` uses "Deterministic LLM mock". Agents execute task graphs but pass fake data. |
| **Document Retrieval** | PARTIAL / MOCK | `axiom/research/agent/tools.py` returns `"Mock document chunk text"`. Embeddings are mock-only. |
| **Knowledge Graph** | PLACEHOLDER | `axiom/core/knowledge_graph/db.py` contains "Old mock database implementation". |
| **Reasoning / SMT Verification** | PLACEHOLDER | `axiom/core/verification/smt_gateway.py` is empty `pass`. `hypothesis_engine.py` is a placeholder. |
| **Evaluation Framework** | REAL LOGIC / FAKE DATA | `axiom/evaluation/run_benchmarks.py` works, but tests the mock capabilities. |

## 3. Test Audit Results
- **Total Tests**: ~853 (649 PASS, 91 FAIL, 31 ERROR, 82 DESELECTED)
- **Primary Failure Mode**: `ValueError: the greenlet library is required to use this function.` Async SQLAlchemy operations crash without the C extension in the sandbox.
- **Test Integrity**: E2E tests (`tests/e2e/*`) heavily rely on mocked backend services (e.g., `class _Z3Sat: pass`).

## 4. Frontend & Backend Audit
- **Frontend**: Fails to build (`next build`) in sandbox due to missing network access for `@next/swc-darwin-arm64`.
- **Backend**: Execution blocked. The `.venv312` virtual environment was removed during the `git clean` baseline enforcing. Missing dependencies.
- **Database**: SQLite + Alembic is correctly tracked in `alembic/versions`.

## 5. Deployment Blockers
- Cannot be deployed as a functional scientific research tool. 
- LLM gateway has no real provider integrations (OpenAI/Anthropic).
- Z3 / Lean compiler binaries are completely missing.
- Production deployment requires replacing the in-memory/stubbed reasoning engines with actual models.

## 6. Critical Technical Debt & Priorities
1. **Remove LLM Mocks**: Implement actual LLM provider integration in `model_gateway/client.py`.
2. **Rebuild Python Environment**: `.venv312` needs standard `requirements.txt` resolution.
3. **Implement Real Vector Store**: Replace dummy document chunking with real vector embeddings (e.g., pgvector).
4. **Implement Real SMT/Lean integration**: Replace `pass` blocks in `smt_gateway.py` with actual sub-process calls.

