# Handoff Report: E2E Survey & Architecture Analysis (MDE Track)

**Agent**: Explorer 1 (E2E Testing Track)  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_e2e_survey_1`  
**Project Root**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`  
**Date**: 2026-08-05  

---

## 1. Observation

1. **Project Directory & Structure**:
   - Monorepo located at `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`.
   - Core source package: `axiom/` containing subpackages `config/`, `core/` (`events/`, `knowledge_graph/`, `memory/`, `parser/`, `reasoning/`, `verification/`), `evaluation/`, `observability/`, and `services/` (`api_gateway/`, `model_gateway/`).
   - Core database store: `axiom/core/knowledge_graph/db.py` line 19 (`EpistemicStore` SQLite wrapper).
   - Schema definitions: `axiom/core/knowledge_graph/schema.py` lines 5-29 (`NodeType`, `EdgeType`, `EpistemicStatus`, `VerificationTier`).
   - Database migrations: `axiom/core/knowledge_graph/migrations.py` lines 114-118 (migrations v1, v2, v3 currently defined).
   - Core verification modules: `axiom/core/verification/smt_gateway.py` (Z3 SMT gateway lines 4-183) and `axiom/core/verification/lean_exporter.py` (Lean 4 exporter lines 5-122).
   - Main API Gateway: `axiom/services/api_gateway/main.py` lines 46-466 (FastAPI app, health/ready checks, `/graph`, `/ingest`, `/query`, `/verify/conjecture`, `/verify/proof`, `/hypothesize`, `/memory/*`, `/self-improve`, `/benchmark/prize-readiness`).

2. **Existing Test Framework & Execution Setup**:
   - Shared fixtures in `tests/conftest.py` lines 14-18: `os.environ.setdefault("DB_PATH", ":memory:")`, `AXIOM_API_TOKEN="test_token"`, `JWT_SECRET_KEY="test-secret"`. Fixtures: `empty_store`, `seeded_store`, `hypothesis_engine`, `working_memory`, `prize_scorer`, `self_improvement`.
   - Existing test files under `tests/`: `conftest.py`, `test_api.py`, `test_benchmark.py`, `test_epistemic_layer.py`, `test_reasoning_pipeline.py`, `test_verification_improvements.py`.
   - Test execution configuration in `pyproject.toml` lines 35-42:
     ```toml
     [tool.pytest.ini_options]
     testpaths = ["tests"]
     addopts = "-v --tb=short"
     markers = ["slow", "integration", "benchmark"]
     ```
   - Execution command from `Makefile` line 53: `PYTHONPATH=. python3 -m pytest tests/ -v`.

3. **MDE Architectural Requirements**:
   - `PROJECT.md` lines 18-40 detail 21 distinct features across 7 milestones (M1 through M7).
   - Interface contracts for EGS ↔ Retrieval, Symbolic ↔ Counterexample, Multi-Prover ↔ Verification, Strategy ↔ Memory defined in `PROJECT.md` lines 54-71.
   - FastAPI microservice router for MDE specified to be mounted at `axiom/services/api_gateway/routes/mde.py` (`/mde/*`) on the main application (`PROJECT.md` line 38).

---

## 2. Logic Chain

1. **Observation 1 & 2** establish that AXIOM has an existing, well-structured test harness using `pytest`, `httpx.TestClient` for FastAPI testing, and in-memory SQLite instances (`:memory:`) for test isolation.
2. **Observation 1 & 3** indicate that while baseline components for graph storage, SMT solving, Lean exporting, and hypothesis generation exist in `axiom/core/`, the specific MDE features (v4 schema migrations, SymPy exact engine, formula retrieval DAG, multi-prover checkers, autonomous conjecture generator, 3-tier counterexample gateway, persistent memory, research strategy planner, independent verification review layer, and `/mde/*` REST router) are planned across Milestones 1 through 7.
3. Therefore, an opaque-box E2E testing framework for MDE must test features at two clear interfaces:
   - Python Core APIs (`axiom.core.*`)
   - FastAPI Microservices Router (`/mde/*`)
4. The 21 features mapped in `PROJECT.md` can be systematically validated end-to-end against their external contracts using `pytest` test modules `tests/test_mde_*.py` operating with in-memory stores and authorized HTTP test clients.

---

## 3. Caveats

1. **System Python Environment Dependencies**: Direct execution of `pytest` in shell returned `No module named pytest` on `/usr/bin/python3` because dependencies are installed in project-specific virtualenvs or site-packages. Execution of pytest must use the python environment where dependencies are present or invoke via `PYTHONPATH=. pytest`.
2. **Lean / Coq / Isabelle Compiler Binaries**: External formal prover binaries (`lean`, `coqc`, `isabelle`) may not be pre-installed in all execution environments. Proof checker components (Feature 6) must simulate compilation when binaries are absent, as already implemented in `axiom/services/api_gateway/main.py` lines 301-312.

---

## 4. Conclusion

The survey and E2E testing plan for AXIOM Mathematical Discovery Engine (MDE) is complete. The existing repository structure, test runner configuration (`pytest`), database fixtures, and API gateway provide a solid foundation for implementing and verifying the 21 MDE features across Milestones M1–M7.

All findings, entry points, contract schemas, and 21 E2E test requirements have been compiled into `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_e2e_survey_1/analysis.md`.

---

## 5. Verification Method

1. **Inspect Analysis Report**:
   ```bash
   view_file /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_e2e_survey_1/analysis.md
   ```
2. **Inspect Project Specs & Fixtures**:
   - `PROJECT.md`
   - `tests/conftest.py`
   - `axiom/services/api_gateway/main.py`
3. **Run Existing Test Suite** (when python environment with dependencies is activated):
   ```bash
   PYTHONPATH=. pytest tests/ -v
   ```
