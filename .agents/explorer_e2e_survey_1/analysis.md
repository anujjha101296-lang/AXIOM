# Comprehensive E2E Survey & Architecture Analysis: AXIOM Mathematical Discovery Engine (MDE)

**Author**: Explorer 1 (E2E Testing Track)  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_e2e_survey_1`  
**Project Root**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`  
**Date**: 2026-08-05  

---

## 1. Executive Summary

This report presents a thorough survey and architectural assessment of the AXIOM project, specifically focusing on the E2E testing strategy and requirements for the **Mathematical Discovery Engine (MDE)** track. The survey covers current repository structure, existing test suites and fixtures, execution mechanics, public entry points (both Python internal APIs and FastAPI REST microservices), and concrete opaque-box E2E testing specifications for all 21 features detailed in `PROJECT.md`.

---

## 2. Project Directory & Subsystem Analysis

### 2.1 Repository Structure
Root directory: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`

```
/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/
├── .agents/                        # Agent workspace metadata & logs
│   ├── ORIGINAL_REQUEST.md         # User requirements & project prompt history
│   ├── explorer_e2e_survey_1/      # Working directory for E2E Explorer 1
│   └── orchestrator/               # Orchestrator plans & briefings
├── axiom/                          # Main Python source package
│   ├── config/                     # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py             # Pydantic-settings configuration
│   ├── core/                       # Core engine modules
│   │   ├── events/                 # In-process async event bus (`bus.py`)
│   │   ├── knowledge_graph/        # EGS SQLite store (`db.py`, `schema.py`, `migrations.py`)
│   │   ├── memory/                 # Working memory management (`working_memory.py`)
│   │   ├── parser/                 # ArXiv LaTeX parser (`arxiv_parser.py`, `semantic_tracker.py`)
│   │   ├── reasoning/              # MCTS proof search (`mcts.py`), Hypothesis Engine (`hypothesis_engine.py`), Self-Improvement (`self_improvement.py`)
│   │   └── verification/           # Z3 SMT gateway (`smt_gateway.py`), Lean 4 exporter (`lean_exporter.py`)
│   ├── evaluation/                 # Millennium Prize readiness scorer (`prize_readiness.py`)
│   ├── observability/              # Structured logger (`logger.py`) and Prometheus metrics (`metrics.py`)
│   └── services/                   # Microservice entrypoints
│       ├── api_gateway/            # FastAPI app (`main.py`), Auth middleware (`auth.py`)
│       └── model_gateway/          # Model client with SQLite cache (`client.py`)
├── tests/                          # Test suite
│   ├── conftest.py                 # Shared pytest fixtures & env settings
│   ├── test_api.py                 # API gateway endpoints test
│   ├── test_benchmark.py           # 5-dimension scientific capability benchmark
│   ├── test_epistemic_layer.py     # EGS DB, NetworkX export & arXiv parser test
│   ├── test_reasoning_pipeline.py  # SMT, MCTS, Lean exporter & verification endpoints test
│   └── test_verification_improvements.py # NRA SMT, polynomial identity & auto-tactic test
├── ui/                             # Next.js spatial canvas frontend application
├── pyproject.toml                  # Poetry dependencies & pytest/mypy/coverage configuration
├── Makefile                        # Dev commands (`make test`, `make dev`, `make setup`)
├── axiom.db                        # SQLite database file
└── PROJECT.md                      # Monorepo architecture & 21-feature MDE specification
```

### 2.2 Configuration & Dependencies (`pyproject.toml`)
- **Python requirement**: `^3.10`
- **Core dependencies**: `pydantic` (^2.5.0), `pydantic-settings` (^2.0.0), `networkx` (^3.0), `sympy` (^1.12), `pylatexenc` (^2.10), `requests` (^2.31.0), `fastapi` (^0.100.0), `uvicorn` (^0.22.0), `z3-solver` (^4.12.0), `anyio` (^4.0.0).
- **Dev dependencies**: `pytest` (^8.0.0), `pytest-cov` (^4.1.0), `pytest-anyio`, `httpx` (^0.27.0), `ruff` (^0.4.0), `mypy` (^1.10.0).
- **Pytest settings**: `testpaths = ["tests"]`, `addopts = "-v --tb=short"`, markers: `slow`, `integration`, `benchmark`. Minimum coverage threshold: `70%`.

---

## 3. Existing Test Framework & Execution Analysis

### 3.1 Test Suite Inventory under `tests/`

| Test File | Description | Target Subsystem | Key Classes / Functions Tested |
|-----------|-------------|------------------|--------------------------------|
| `conftest.py` | Fixtures and env setup | All | `empty_store`, `seeded_store`, `hypothesis_engine`, `working_memory`, `prize_scorer` |
| `test_api.py` | REST API gateway tests | API Gateway | `/health`, `/ready`, `/ingest`, `/query`, `ModelClient` caching |
| `test_benchmark.py` | 5-dimension SCB benchmark | Core Reasoning | Parsing accuracy, SMT refutation, MCTS proof rate, Hypothesis novelty, Graph growth |
| `test_epistemic_layer.py` | EGS & LaTeX Ingestion | Knowledge Graph | `PaperNode`, `MathematicalClaimNode`, `EpistemicStore`, `ArxivParser`, `SemanticTracker` |
| `test_reasoning_pipeline.py` | Verification & Proof | Reasoning & Verification | `SmtGateway`, `MctsSolver`, `LeanExporter`, `/verify/conjecture`, `/verify/proof`, `/graph` |
| `test_verification_improvements.py` | Advanced SMT & Tactics | Verification & Evaluation | Nonlinear Real Arithmetic, Polynomial identities, Mathlib tactics, `PrizeReadinessScorer` |

### 3.2 Fixtures in `tests/conftest.py`
- Environment variables initialized at import time:
  - `DB_PATH=":memory:"`
  - `AXIOM_API_TOKEN="test_token"`
  - `JWT_SECRET_KEY="test-secret"`
  - `LOG_FORMAT="console"`
  - `LOG_LEVEL="WARNING"`
- Fixtures:
  - `empty_store`: Function-scoped `EpistemicStore(db_path=":memory:")`.
  - `seeded_store`: Pre-seeded in-memory store with 5 verified theorems (`thm-fermat`, `thm-euler`, `thm-pythagor`, `thm-bayes`, `thm-gauss`), 2 concept nodes (`con-prime`, `con-field`), and 1 paper node (`paper-wiles`) linked by a `PROVES` edge.
  - `hypothesis_engine`: `HypothesisEngine` initialized with `seeded_store`.
  - `working_memory`: Fresh `WorkingMemory` instance.
  - `prize_scorer`: Fresh `PrizeReadinessScorer` instance.
  - `self_improvement`: `SelfImprovementLoop` scoped to temporary directory.

### 3.3 Execution Mechanics
- **Primary execution command**: `PYTHONPATH=. pytest tests/ -v` (or `make test`).
- **Benchmark execution command**: `PYTHONPATH=. pytest tests/test_benchmark.py -v -s` (or `make test-benchmark`).
- **Coverage command**: `PYTHONPATH=. pytest tests/ -v --cov=axiom --cov-report=term-missing --cov-fail-under=70` (or `make test-coverage`).
- **Python Environment**: System Python or virtualenv (`.venv`). Note: In offline/sandboxed environments without outbound PyPI access, tests must be run using installed Python packages or pre-built virtual environments.

---

## 4. MDE Feature Public Entry Points (Python & REST APIs)

The MDE track defines entry points across Python internal package APIs (`axiom.core.*`) and FastAPI REST endpoints (`/mde/*`).

### 4.1 FastAPI Microservice Router (`/mde/*`)
To be located at `axiom/services/api_gateway/routes/mde.py` and mounted in `axiom/services/api_gateway/main.py` via `app.include_router(mde_router, prefix="/mde", tags=["mde"])`.

| Endpoint Path | Method | Feature # | Input Payload Schema | Output Response Schema |
|---------------|--------|-----------|----------------------|------------------------|
| `/mde/retrieval` | `GET` | F4 | Query params: `target_formula: str, domain: Optional[str]` | `RetrievalResponsePayload` |
| `/mde/proof/compile` | `POST` | F8 | `ProofCompileRequest(system, theorem_name, code, context)` | `ProofCompileResponse` |
| `/mde/conjectures/generate` | `POST` | F11 | `ConjectureGenerateRequest(max_conjectures, domain)` | `ConjectureGenerateResponse` |
| `/mde/counterexample/search` | `POST` | F14 | `CounterexampleSearchRequest(formula_smt, variables, timeout_seconds)` | `CounterexampleSearchResponse` |
| `/mde/strategy/plan` | `POST` | F18 | `StrategyPlanRequest(problem_id, domain)` | `StrategyPlanResponse` |
| `/mde/strategy/decompose` | `GET` | F18 | Query params: `problem_id: str` | `StrategyDecomposeResponse` |
| `/mde/memory/snapshot` | `POST` | F18 | `MemorySnapshotRequest(session_id)` | `MemorySnapshotResponse` |
| `/mde/verification/review` | `POST` | F18 | `VerificationReviewRequest(claim_id, verification_data)` | `VerificationReviewResponse` |

### 4.2 Python Core API Entry Points (`axiom.core.*`)

```python
# 1. Epistemic Graph Store & Ontological Schema (M1)
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.migrations import run_migrations
from axiom.core.knowledge_graph.schema import (
    MathematicalObjectNode, DefinitionNode, OpenProblemNode, ConjectureNode,
    Edge, EdgeType, EpistemicStatus, VerificationTier
)

# 2. Symbolic Computation Engine (M2)
from axiom.core.symbolic.sympy_engine import SymPyEngine

# 3. Theorem Retrieval & Dependency Discovery (M2)
from axiom.core.retrieval.engine import FormulaRetrievalEngine

# 4. Multi-Prover Formal Proof Architecture (M3)
from axiom.core.verification.lean_exporter import LeanExporter
from axiom.core.verification.lean_checker import LeanChecker
from axiom.core.verification.coq_checker import CoqChecker
from axiom.core.verification.isabelle_checker import IsabelleChecker

# 5. Autonomous Conjecture Generation (M4)
from axiom.core.conjecture.generator import AutonomousConjectureGenerator
from axiom.core.conjecture.novelty_scorer import NoveltyScorer
from axiom.core.conjecture.filters import WeakConjectureFilter

# 6. Counterexample Search Gateway (M5)
from axiom.core.counterexample.gateway import CounterexampleGateway

# 7. Working & Persistent Memory (M6)
from axiom.core.memory.persistent_store import PersistentMemoryStore
from axiom.core.memory.working_memory import WorkingMemory

# 8. Research Strategy Planner (M6)
from axiom.core.strategy.planner import ResearchStrategyPlanner
from axiom.core.strategy.riemann_tree import RiemannTree

# 9. Independent Verification Review Layer (M6)
from axiom.core.verification.review_controller import VerificationReviewController
```

---

## 5. Requirements for Opaque-Box E2E Testing (21 Features)

Opaque-box E2E testing validates behavior exclusively through public APIs and REST microservices without inspecting or mocking internal functions. Below are the precise E2E test requirements for each of the 21 features.

| # | Feature Name | Milestone | Scope & Test Input | Expected Output & Assertion Criteria |
|---|--------------|-----------|--------------------|--------------------------------------|
| 1 | SQLite v4 Schema Migration | M1 | Run `run_migrations(conn)` on SQLite DB | Tables `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts` exist with proper schema and foreign keys. |
| 2 | EGS Ontological Schema Models | M1 | Instantiate `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`, and edges `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES` | Round-trip serialisation to JSON and persistence in `EpistemicStore` succeeds without validation errors. |
| 3 | Exact SymPy Symbolic Engine | M2 | Pass algebraic identities (e.g. $(x+y)^2 = x^2+2xy+y^2$) & Dirichlet series expansions | Returns exact symbolic representation with zero IEEE 754 float drift. |
| 4 | Formula Retrieval & Dependency DAG | M2 | `GET /mde/retrieval?target_formula=a^2+b^2=c^2` | Returns HTTP 200 with `query_formula`, `canonical_form`, `matched_theorems`, `equivalent_formulations`, and NetworkX dependency DAG. |
| 5 | Multi-Prover Script Generators | M2/M3 | Input theorem name, statement, variables for Lean 4, Coq, Isabelle | Generates valid syntactical proof script string containing prover headers (`import`, `Theorem`, `Lemma`, `Theory`). |
| 6 | Proof Compiler Checkers & Fallback | M3 | Submit proof scripts to `LeanChecker`, `CoqChecker`, `IsabelleChecker` when binaries are missing | Returns `is_valid=True/False` with fallback simulation flag and diagnostic warnings logged. |
| 7 | Mathlib Tactic Generator | M3 | Pass statement `"x + y = y + x"` or `"x + 1 > x"` to `auto_generate_tactic` | Selects exact tactic (`ring`, `linarith`, `norm_num`, `rfl`, `positivity`). |
| 8 | Formal Proof Compiler Endpoint | M3 | `POST /mde/proof/compile` with `{"system": "lean4", "theorem_name": "...", "code": "..."}` | Returns HTTP 200 with `ProofCompileResponse` (`is_valid`, `status`, `diagnostics`, `execution_time_ms`). |
| 9 | Autonomous Conjecture Generator | M4 | Call `AutonomousConjectureGenerator.generate(store)` | Produces candidate claim nodes using 5 strategies (`DUAL`, `BOUND`, `COMPLEX`, `GENERAL`, `COMPOSE`). |
| 10 | Novelty Scorer & Weak Filter | M4 | Pass candidate claim nodes through scorer and filter | Filters out tautologies/duplicates; assigns score $N(C) \in [0.0, 1.0]$. |
| 11 | Conjecture Generation Endpoint | M4 | `POST /mde/conjectures/generate` with `{"max_conjectures": 5}` | Returns HTTP 200 with list of ranked conjectures, strategy tags, and novelty scores. |
| 12 | 3-Tier Counterexample Gateway | M5 | Pass invalid conjecture (e.g. $x^2 + y^2 = 5$ mod 7 or real inequality) | Escalate Tier 1 (Sweep) -> Tier 2 (Z3) -> Tier 3 (SymPy). Returns counterexample dictionary within <60s timeout guard. |
| 13 | Counterexample Graph Updater | M5 | Execute refutation search on stored claim node | Node status transitions to `REFUTED` in SQLite store and `COUNTEREXAMPLE_FOR` edge is created. |
| 14 | Counterexample Search Endpoint | M5 | `POST /mde/counterexample/search` with formula and bounds | Returns HTTP 200 with `is_valid`, `counterexample_found`, `counterexample`, `tier_used`, `execution_time_ms`. |
| 15 | Persistent Memory & Tactic Guard | M6 | Store failed proof tactic attempt; launch MCTS proof search | Prunes previously recorded failed tactics from MCTS expansion tree. |
| 16 | Research Strategy Planner | M6 | Request plan for problem `"Riemann Hypothesis"` | Returns root lemma ID, Lemma Prioritization Index $P(L)$, and hierarchical zero-free region DAG tree. |
| 17 | Independent Verification Review Layer | M6 | Submit claim with cross-verifier inputs (SMT + MCTS + Compiler) | Verifies agreement across all verification layers; returns overall verdict and sanity flags. |
| 18 | Strategy, Memory & Review Endpoints | M6 | `POST /mde/strategy/plan`, `GET /mde/strategy/decompose`, `POST /mde/memory/snapshot`, `POST /mde/verification/review` | All endpoints return HTTP 200 OK matching contract schemas. |
| 19 | FastAPI MDE Router Integration | M7 | Send requests to `/mde/*` endpoints on main FastAPI application | OpenAPI documentation lists `/mde` routes; Bearer auth token validation enforced. |
| 20 | Exhaustive MDE Test Suite | M7 | Run complete E2E test suite `pytest tests/test_mde_*.py` | 100% test pass rate across Number Theory and Riemann Hypothesis domains. |
| 21 | Millennium Prize Alignment Report | M7 | Inspect documentation file `docs/mde_prize_alignment.md` | Contains structured analysis evaluating MDE capability against Riemann Hypothesis zeta zeros. |

---

## 6. Recommendations for Implementers & Test Engineers

1. **Isolation**: Use `EpistemicStore(":memory:")` for unit and integration test isolation to prevent polluting `axiom.db`.
2. **Environment Variables**: Ensure `PYTHONPATH=.` and `AXIOM_API_TOKEN="test_token"` are set in test execution environments.
3. **FastAPI Testing**: Use `fastapi.testclient.TestClient(app)` with authorization header `{"Authorization": "Bearer test_token"}` for endpoint tests.
4. **Mocking External Process Execution**: Multi-prover checkers (`lean`, `coqc`, `isabelle`) must handle missing binaries gracefully by falling back to simulation mode without crashing test runs.
5. **Timeout Guard Enforcement**: SMT and counterexample search tests must strictly verify the <60s execution timeout limit.
