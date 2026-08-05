# Comprehensive Codebase & Infrastructure Survey Report for Mathematical Discovery Engine (MDE)

## 1. Observation

### 1.1 Existing Codebase Directory Structure & Components
The project root is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`.
The codebase consists of Python core packages in `axiom/`, FastAPI service gateway in `axiom/services/api_gateway/`, test suite in `tests/`, and Next.js UI in `ui/`.

#### Core Package Index (`axiom/core/`):
- **`axiom/core/knowledge_graph/`**:
  - `schema.py`: Lines 1-102. Defines Pydantic models for `NodeType` (`PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`), `EdgeType` (`CITES`, `PROVES`, `REFUTES`, `CONTRADICTS`, `EXTENDS`, `CORROBORATES`, `USES_METHOD`), `EpistemicStatus` (`VERIFIED`, `CONJECTURED`, `REFUTED`, `UNDER_REVIEW`), `VerificationTier` (TIER 0-3), `ScientificNode` (polymorphic union using discriminator `type`), `Edge`, and `KnowledgeGraph`.
  - `db.py`: Lines 1-222. Implements `EpistemicStore` using SQLite 3 (`check_same_thread=False`). Stores node payloads as JSON in `nodes.data`. Supports NetworkX conversion via `to_networkx()` returning `nx.DiGraph`.
  - `migrations.py`: Lines 1-155. Implements versioned schema migrations via `_schema_migrations` table.
    - `v1`: `_v1_initial_schema` (`nodes`, `edges` tables & indexes).
    - `v2`: `_v2_proof_lineage` (`proof_lineage` table for verification attempt tracking).
    - `v3`: `_v3_working_memory_snapshots` (`memory_snapshots` table).

- **`axiom/core/parser/`**:
  - `arxiv_parser.py`: LaTeX AST parser extracting titles, authors, abstracts, math environments (`theorem`, `lemma`, `definition`, etc.), and BibTeX keys.
  - `semantic_tracker.py`: Computes logical dependency DAGs, identifies circular dependencies using `networkx.simple_cycles`, and calculates critical path claims.

- **`axiom/core/verification/`**:
  - `lean_exporter.py`: Lines 1-122. Translates claims into Lean 4 format (`export_theorem`). Automatically selects basic tactics (`norm_num`, `rfl`, `ring`, `linarith`, or fallback `sorry`). Writes `.lean` files to local path (default `/tmp/axiom_proofs/`).
  - `smt_gateway.py`: Lines 1-183. Implements `SmtGateway` using `z3-solver`. Supports:
    1. `verify_modular_conjecture`: Modular arithmetic checks $(LHS \pmod m) \neq (RHS \pmod m)$.
    2. `verify_real_inequality`: Real inequality solver ($LHS \le RHS$) over bounded real variables using Z3 Nonlinear Real Arithmetic (NRA).
    3. `verify_polynomial_identity`: Universal real polynomial identity checks ($LHS = RHS$).

- **`axiom/core/reasoning/`**:
  - `mcts.py`: Lines 1-176. Implements `MctsSolver` and `MctsNode`. Uses UCT score selection ($\frac{V}{N} + c \sqrt{\frac{\ln N_{parent}}{N}}$), 7 algebraic rewrite rules (`IDENTITY_ADD`, `IDENTITY_MUL`, `ZERO_MUL`, `ASSOCIATIVE_ADD`, `DISTRIBUTIVE`, `COMMUTATIVE_ADD`, `COMMUTATIVE_MUL`), random rollout playouts up to 8 steps, and path reconstruction.
  - `hypothesis_engine.py`: Lines 1-150. Generates candidate claims from verified theorem nodes using pattern templates (`DUAL`, `BOUND`, `COMPLEX`, `GENERAL`, `COMPOSE`).
  - `self_improvement.py`: System capability self-auditor generating `roadmap.md`.

- **`axiom/core/memory/`**:
  - `working_memory.py`: Lines 1-162. Session-scoped in-memory store tracking active research problems (`set_problem`), active hypotheses (`add_hypothesis`), failed attempts (`record_failure`), and open questions (`add_question`).

- **`axiom/evaluation/`**:
  - `prize_readiness.py`: Lines 1-386. Scores AXIOM capabilities across 7 prize-backed problems (P vs NP, Riemann Hypothesis, Navier-Stokes, Yang-Mills, Hodge, BSD, Poincare) across 5 dimensions (knowledge, reasoning, verification, hypothesis_gen, literature_coverage).

#### Service Gateway (`axiom/services/api_gateway/`):
- `main.py`: Lines 1-466. FastAPI REST server initializing singletons (`EpistemicStore`, `ArxivParser`, `SmtGateway`, `LeanExporter`, `MctsSolver`, `HypothesisEngine`, `WorkingMemory`, `SelfImprovementLoop`, `PrizeReadinessScorer`).
  - Lifespan context manager runs `run_migrations(store.conn)` on startup.
  - Routes:
    - `GET /health`, `GET /ready`, `GET /metrics`
    - `GET /events` (Event bus history)
    - `GET /graph` (Export knowledge graph payload)
    - `POST /ingest` (Ingest arXiv paper LaTeX into EGS)
    - `POST /query` (Search placeholder)
    - `POST /verify/conjecture` (SMT verification & EGS claim node registration)
    - `POST /verify/proof` (MCTS proof search, Lean code export, compiler invocation check, EGS update)
    - `POST /hypothesize` (Generate conjectures & populate working memory)
    - `GET /memory/context`, `POST /memory/reset`, `POST /memory/problem`
    - `POST /self-improve`
    - `GET /benchmark/prize-readiness`
- `auth.py`: Token authentication middleware (`verify_token`).

#### Test Suite (`tests/`):
- `conftest.py`: Test configuration.
- `test_epistemic_layer.py`: Pydantic schema validation, SQLite persistence, NetworkX export, LaTeX parser, semantic tracker circular dependency checks.
- `test_verification_improvements.py`: SMT NRA, SMT polynomial identities, Lean auto-tactic generation, dynamic prize readiness scoring.
- `test_reasoning_pipeline.py`: SMT modular conjecture, MCTS solver, Lean exporter, API endpoints `/verify/conjecture`, `/verify/proof`, `/graph`.
- `test_benchmark.py`: Benchmark suite across 5 capability dimensions.
- `test_api.py`: API health, ready, auth protection, auth success, model gateway client cache.

---

### 1.2 Database Schema & Migration Setup
- Database engine: SQLite 3 (`axiom.db` or `:memory:`).
- Table structures:
  - `nodes`: `id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL, data TEXT NOT NULL`
  - `edges`: `source_id TEXT, target_id TEXT, type TEXT, confidence REAL, provenance TEXT, PRIMARY KEY (source_id, target_id, type)`
  - `_schema_migrations`: `version INTEGER PRIMARY KEY, description TEXT NOT NULL, applied_at TEXT NOT NULL`
  - `proof_lineage`: `id INTEGER PRIMARY KEY AUTOINCREMENT, claim_id TEXT NOT NULL, verifier TEXT NOT NULL, result TEXT NOT NULL, tactic_used TEXT, duration_ms REAL, created_at TEXT NOT NULL`
  - `memory_snapshots`: `id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, snapshot TEXT NOT NULL, created_at TEXT NOT NULL`

---

### 1.3 Infrastructure Toolchain & Installed Dependencies Survey

Execution command output for toolchain check:
```
Python: Python 3.9.6 (/usr/bin/python3)
lean: not found on $PATH
z3: binary not found on $PATH
coqc: not found on $PATH
isabelle: not found on $PATH
pytest: not installed in default system site-packages
pip3 packages: system python 3.9 has default base packages (altgraph, future, macholib, pip 21.2.4, setuptools, wheel)
```

Observations regarding provers & libraries:
1. **Lean 4 (`lean`)**: Binary is missing from local `$PATH`. In `main.py:302`, `verify_proof` checks `if os.path.exists("/usr/local/bin/lean") or os.path.exists("/usr/bin/lean")`. When missing, it returns `compiler_status = "simulated compile success (local Lean bin missing)"`.
2. **Coq (`coqc`) & Isabelle (`isabelle`)**: No binaries installed on system `$PATH`. No exporter or proof checker modules currently exist in `axiom/core/verification/` for Coq or Isabelle.
3. **Z3 SMT (`z3-solver`)**: SMT gateway imports `import z3`. When Python package `z3-solver` is available, Z3 C-bindings execute in-process without requiring external `z3` binary.
4. **SymPy (`sympy`)**: Listed in `pyproject.toml` (`sympy = "^1.12"`), but currently no dedicated SymPy symbolic computation module or REST endpoint exists in `axiom/core/` or `main.py`.
5. **Pytest & Python environment**: `pyproject.toml` defines Poetry project with Python `^3.10`, Pydantic `^2.5.0`, NetworkX `^3.0`, SymPy `^1.12`, PyLaTeXenc `^2.10`, FastAPI `^0.100.0`, Uvicorn `^0.22.0`, Z3-solver `^4.12.0`. In the current environment, network calls to PyPI fail due to sandbox network isolation. Standard library `sqlite3` works natively.

---

## 2. Logic Chain

1. **Baseline Capability Alignment**:
   - The existing AXIOM core provides foundation modules for SQLite storage (EGS), LaTeX parsing (EIE), basic Lean 4 template rendering (LRK), Z3 SMT modular/real checks (AVT), and MCTS rewrite solving (DRSP).
   - However, the current implementation lacks the domain depth, formal multi-prover architecture, theorem retrieval DAGs, exact symbolic math, hypothesis scoring, research planning, and snapshotting required by MDE Requirements R1–R10 in `ORIGINAL_REQUEST.md`.

2. **Database Schema Expansion Gaps (R1 & R8)**:
   - Current schema (`NodeType`: `PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`) lacks explicit models for `MATHEMATICAL_OBJECT`, `DEFINITION`, `EQUIVALENT_STATEMENT`, `THEOREM`, `LEMMA`, `COROLLARY`, `CONJECTURE`, `OPEN_PROBLEM`.
   - Edge types in `EdgeType` (`CITES`, `PROVES`, `REFUTES`, `CONTRADICTS`, `EXTENDS`, `CORROBORATES`, `USES_METHOD`) lack required relationship edges `EQUIVALENT_TO`, `DEPENDS_ON`, `REDUCES_TO`, `SPECIALIZES`.
   - SQLite migration system (`migrations.py`) is modular and ready for `v4` migration script to create `mathematical_objects`, `definitions`, `equivalent_statements`, and expanded `memory_snapshots`.

3. **Theorem Retrieval & Dependency Discovery Gaps (R2)**:
   - `semantic_tracker.py` provides basic NetworkX cycle detection and critical path ranking, but there is no dedicated `/mde/retrieval` endpoint or syntactic/semantic theorem match index.

4. **Formal Proof Verification Gaps (R3)**:
   - `lean_exporter.py` only formats basic Lean 4 string headers and basic Mathlib tactics for single equality/inequality statements.
   - There are no generators or checkers for **Coq** (`.v` files) or **Isabelle** (`.thy` files).
   - Proof checkers must support subprocess validation with graceful fallback diagnostics when binary provers (`lean`, `coqc`, `isabelle`) are not installed on system `$PATH`.

5. **Conjecture Generation & Counterexample Gateways (R4 & R5)**:
   - `hypothesis_engine.py` uses basic string regex dual/bound templates. It needs a quantitative hypothesis novelty and plausibility scorer, plus open problem rankers.
   - `smt_gateway.py` covers basic modular arithmetic and polynomial identities via Z3. To fulfill R5 & R6, it needs integration with exact symbolic solving (SymPy) for complex numbers, Dirichlet series, and probabilistic parameter sweeps.

6. **Target Verification Domain & Riemann Hypothesis Alignment (R7, R8, R9, R10)**:
   - Target domain requires verifying basic number theory/algebraic identities and analytic number theory (Riemann zeta zero tracking, complex zeros $\text{Re}(s) = 1/2$, Dirichlet series $\sum n^{-s}$).
   - `prize_readiness.py` currently has a baseline score model for Riemann Hypothesis (knowledge=0.10, reasoning=0.06, verification=0.04). An explicit `docs/mde_prize_alignment.md` report and research strategy planner (`/mde/strategy`) decomposing RH into zero-free region lemmas are required.

---

## 3. Caveats

1. **System Binary Availability**: `lean`, `z3`, `coqc`, and `isabelle` binaries are not present on the host environment's system `$PATH`. Subprocess validation routines MUST handle command failure / missing binary gracefully and return diagnostic warnings.
2. **Network Isolation**: The environment is isolated from public PyPI index. Dependency verification must rely on standard Python libraries or locally bundled packages.
3. **Read-Only Scope**: This survey report is strictly read-only. No core project code in `axiom/` was modified during this exploration step.

---

## 4. Conclusion

The AXIOM codebase provides a solid, cleanly structured architecture for the Mathematical Discovery Engine (MDE). The current SQLite knowledge graph, FastAPI service gateway, Lean exporter, Z3 SMT gateway, and MCTS reasoning engine can be directly extended without architectural refactoring.

To fulfill all 10 MDE requirements specified in `ORIGINAL_REQUEST.md`, implementation teams should execute the following target design:

1. **Schema Extension (`axiom/core/knowledge_graph/`)**: Write migration `v4` adding `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, and add `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES` graph edges.
2. **Theorem Retrieval Subsystem (`axiom/core/retrieval/`)**: Implement formula parser, dependency resolution DAG builder, and `GET /mde/retrieval` endpoint.
3. **Multi-Prover Architecture (`axiom/core/verification/`)**: Implement formal script generators and subprocess proof checkers for Lean 4, Coq, and Isabelle with diagnostic fallbacks, exposed via `POST /mde/proof/compile`.
4. **Conjecture & Counterexample Subsystems (`axiom/core/discovery/`)**: Implement novelty/plausibility hypothesis scoring (`POST /mde/conjectures/generate`) and multi-engine counterexample search combining Z3 SMT and SymPy exact symbolic math (`POST /mde/counterexample/search`).
5. **Symbolic Mathematics & Memory (`axiom/core/symbolic/` & `axiom/core/memory/`)**: Implement exact SymPy Dirichlet series/zeta zero evaluator and persistent proof attempt memory preventing duplicate tactic failures.
6. **Research Strategy & Prize Alignment (`axiom/core/strategy/` & `docs/`)**: Build hierarchical open problem decomposer (`POST /mde/strategy/plan`) and write `docs/mde_prize_alignment.md` for the Riemann Hypothesis.

---

## 5. Verification Method

To verify the observations and analysis in this report independently:

1. **Inspect Code Files**:
   - `view_file` on `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/knowledge_graph/schema.py` (lines 5-33, 57-63) to verify node types and epistemic status.
   - `view_file` on `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/knowledge_graph/db.py` (lines 24-54) to verify SQLite schema.
   - `view_file` on `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/verification/lean_exporter.py` (lines 19-50) to verify tactic generation heuristics.
   - `view_file` on `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/verification/smt_gateway.py` (lines 8-68) to verify Z3 modular check logic.
   - `view_file` on `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/reasoning/mcts.py` (lines 43-51) to verify algebraic rules.
   - `view_file` on `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/services/api_gateway/main.py` (lines 226-346) to verify `/verify/conjecture` and `/verify/proof` routes.

2. **Verify Database Migration Execution**:
   - Execute: `PYTHONPATH=. python3 -c "import sqlite3; from axiom.core.knowledge_graph.migrations import run_migrations, migration_status; conn = sqlite3.connect(':memory:'); run_migrations(conn); print(migration_status(conn))"`
   - Expected Output: List showing migrations `v1`, `v2`, `v3` as `applied`.

3. **Verify Toolchain Availability**:
   - Execute: `which lean z3 coqc isabelle pytest`
   - Expected Output: Non-zero exit code indicating binaries are missing from local system PATH.

4. **Invalidation Conditions**:
   - If `lean` or `coqc` binaries are discovered on host PATH, compiler check fallback mechanisms can be upgraded to live execution.
   - If SQLite migration system fails to execute `PRAGMA foreign_keys = ON;`, FK constraints must be adjusted.
