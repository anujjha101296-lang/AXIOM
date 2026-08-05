# Technical Analysis & Specification Report: MDE Requirements R4, R5, R7, R8, R9, R10

**Author**: explorer_mde_3  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_mde_3`  
**Target Project**: AXIOM Mathematical Discovery Engine (MDE)  
**Date**: 2026-08-05  

---

## 1. Observation

Direct code and structural analysis of the existing AXIOM codebase (`/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`) revealed the following baseline implementations and missing capabilities for Requirements R4, R5, R7, R8, R9, and R10:

### 1.1 Existing Hypothesis Generation (`axiom/core/reasoning/hypothesis_engine.py`)
- **Observed Lines 23–34, 90–149**: `HypothesisEngine` uses 5 fixed pattern templates (`TEMPLATES`): generalisation, composition, dual (swapping quantifiers), bound refinement ($\le C \to \le C/2$), and complex extension ($\mathbb{N},\mathbb{Z},\mathbb{R} \to \mathbb{C}$).
- **Limitations**:
  - Lacks mathematical novelty score ranking.
  - Lacks filtering of weak/trivial conjectures (e.g. syntactic tautologies or equivalent variations).
  - Only exposed at endpoint `POST /hypothesize` (`axiom/services/api_gateway/main.py:351-383`), which lacks parameterization for target domains (e.g., number theory, zeta zeros) or custom novelty score thresholds.

### 1.2 Existing SMT Verification (`axiom/core/verification/smt_gateway.py`)
- **Observed Lines 8–69, 91–137, 139–182**: `SmtGateway` contains `verify_modular_conjecture`, `verify_real_inequality`, and `verify_polynomial_identity` using Z3 `Solver()`.
- **Limitations**:
  - Exposed via legacy endpoint `POST /verify/conjecture` (`main.py:226–269`), which only handles integer modular arithmetic.
  - Lacks multi-tier computational sweep (fuzzing/parameter grid search) and exact symbolic solving via SymPy.
  - Lacks explicit execution timeout guarding under 60 seconds across multi-tier checks.

### 1.3 Existing Working Memory & Storage (`axiom/core/memory/working_memory.py`)
- **Observed Lines 20–47, 49–160**: `WorkingMemory` provides an in-memory dataclass `ResearchContext` storing `failed_attempts` and `active_hypotheses`.
- **Limitations**:
  - Epistemic session data is ephemeral and lost when the FastAPI process terminates.
  - No persistent SQLite tables exist for memory snapshots (`memory_snapshots`) or detailed failed proof search paths.
  - MCTS proof search (`axiom/core/reasoning/mcts.py`) currently operates independently of `WorkingMemory`, meaning failed tactics are not checked or pruned during MCTS tactic expansion.

### 1.4 Research Strategy & Decomposition
- **Observed**: No dedicated research strategy planner module currently exists in `axiom/core/`.
- **Limitations**: Problem decomposition into intermediate lemmas, hierarchical DAG representation, and tactic prioritization for complex targets like the Riemann Hypothesis are missing.

### 1.5 Verification Review & Cross-Checking
- **Observed**: `axiom/services/api_gateway/main.py:272-346` runs MCTS solver, exports Lean code, and attempts local compiler execution, but does not cross-check SMT counterexample results against MCTS proof outputs or perform independent multi-verifier reviews.

### 1.6 Evaluation & Prize Readiness (`axiom/evaluation/prize_readiness.py`)
- **Observed Lines 85–102**: `PrizeReadinessScorer` contains static baseline definitions for the Riemann Hypothesis with initial scores (`knowledge=0.10, reasoning=0.06, verification=0.04, hypothesis_gen=0.08, literature_coverage=0.12`).
- **Limitations**: Missing the dedicated evaluation report `docs/mde_prize_alignment.md` analyzing MDE capability gaps for Millennium Prize targets.

---

## 2. Logic Chain

From the observations above, the logical progression to achieve full compliance with MDE requirements R4, R5, R7, R8, R9, and R10 is structured as follows:

1. **R4 (Conjecture Generation & Hypothesis Scorer)**:
   - *Observation*: Current generation relies on basic string substitution without scoring or filtering.
   - *Deduction*: To output high-quality claims via `POST /mde/conjectures/generate`, we must introduce a formal **Mathematical Novelty Scorer $N(C)$**, an AST-based **Weak Conjecture Filter**, and expanded generation strategies (pattern mining, duality, bound refinement, domain translation, and pair composition).

2. **R5 (Counterexample Search Gateway)**:
   - *Observation*: Z3 solver is isolated and only handles modular arithmetic in the API endpoint.
   - *Deduction*: To satisfy `POST /mde/counterexample/search`, we must construct a 3-tier gateway (Computational Parameter Sweep $\to$ Z3 SMT Solver $\to$ SymPy Exact Solver) bounded by a strict 60-second timer. If a counterexample is found, variable assignments are returned and the target EGS node status is transitioned to `REFUTED`.

3. **R7 (Research Strategy Planner)**:
   - *Observation*: MCTS and proof tools run on flat expressions without goal decomposition.
   - *Deduction*: To attack open problems (e.g. Riemann Hypothesis), a strategy planner must recursively decompose target open problems into intermediate lemma DAGs and rank lemmas by a **Prioritization Index $P(L)$** incorporating provability, dependency depth, and tactic coverage.

4. **R8 (Mathematical Memory & Snapshotting)**:
   - *Observation*: Working memory is purely in-process; search engines repeat failed search paths.
   - *Deduction*: We must implement persistent SQLite snapshotting (`memory_snapshots` table) and build a **Failure Index Lookup** that prunes known failed tactic sequences during MCTS tactic expansion.

5. **R9 (Independent Verification & Architecture Review)**:
   - *Observation*: Proof and verification steps do not audit each other.
   - *Deduction*: An **Independent Verification Review Layer** must cross-check outputs across SMT and MCTS, run sanity checks against proof scripts (e.g., detecting `sorry`), and log verification audit records.

6. **R10 (Monorepo Integration, FastAPI, Test Plan, Prize Alignment)**:
   - *Observation*: Requirements call for unified microservice routes, monorepo placement, tests, and documentation.
   - *Deduction*: Implement `/mde/*` FastAPI endpoints, unit and integration tests across target domains, and a prize alignment report at `docs/mde_prize_alignment.md`.

---

## 3. Detailed Specifications for Requirements

### 3.1 Requirement R4: Autonomous Conjecture Generation & Hypothesis Scorer (Team D)

#### API Endpoint: `POST /mde/conjectures/generate`

#### 1. Generation Strategies & Pattern Mining
- **Generalization**: Extend finite bound or index $n=k$ to arbitrary $n \in \mathbb{N}$ or $\mathbb{R}$.
- **Duality**: Swap quantifiers ($\forall \leftrightarrow \exists$) and invert implications ($P \implies Q \to Q \implies P$).
- **Bound Refinement**: Tighten asymptotic bounds ($O(n) \to O(\log n)$) or inequality constants ($C \to C/2$).
- **Domain Translation**: Extend real/integer claims to complex domain $\mathbb{C}$ (e.g., polynomial roots $\to$ complex zeros).
- **Pair Composition**: Combine two verified theorems $A$ and $B$ to conjecture joint invariant $C$.
- **Structural Analogy**: Map group/ring properties to analogous structures.

#### 2. Mathematical Novelty Score Formula
Each candidate conjecture $C$ is assigned a novelty score $N(C) \in [0.0, 1.0]$:
$$N(C) = w_1 \cdot \text{Complexity}(C) + w_2 \cdot \text{GraphDistance}(C) + w_3 \cdot \text{NonTriviality}(C) - w_4 \cdot \text{Redundancy}(C)$$
Where:
- $\text{Complexity}(C)$: Normalized AST depth and operator count.
- $\text{GraphDistance}(C)$: Shortest path in EGS graph between origin claim nodes (further distance $\implies$ higher novelty).
- $\text{NonTriviality}(C)$: Ratio of non-tautological terms (evaluated via SymPy simplification).
- $\text{Redundancy}(C)$: Maximum cosine/syntactic similarity against existing EGS claims.
- Default weights: $w_1 = 0.25, w_2 = 0.35, w_3 = 0.30, w_4 = 0.40$.

#### 3. Weak & Trivial Conjecture Filtering
Discards claims if:
- SymPy reduces expression to `True` or $x = x$ (Tautology filter).
- Syntactic fingerprint matches an existing node in EGS (Duplicate filter).
- Novelty score $N(C) < \tau_{\text{novelty}}$ (default threshold $0.40$).

#### 4. Data Models (Pydantic)
```python
class ConjectureGenerationRequest(BaseModel):
    domain: Optional[str] = "number_theory"
    target_node_ids: Optional[List[str]] = None
    max_conjectures: int = 5
    min_novelty_threshold: float = 0.40
    generation_strategies: Optional[List[str]] = ["DUAL", "BOUND", "COMPLEX", "GENERAL", "COMPOSE"]

class GeneratedConjecture(BaseModel):
    id: str
    name: str
    statement_latex: str
    statement_lean: str
    novelty_score: float
    complexity_score: float
    origin_strategy: str
    origin_claim_ids: List[str]
    status: str = "CONJECTURED"
    reasoning_rationale: str

class ConjectureGenerationResponse(BaseModel):
    count: int
    conjectures: List[GeneratedConjecture]
```

---

### 3.2 Requirement R5: Counterexample Search Gateway (Team E)

#### API Endpoint: `POST /mde/counterexample/search`

#### 1. Multi-Tier Search Gateway Architecture
1. **Tier 1: Computational & Fuzzing Parameter Sweep**
   - Evaluates claims over discrete parameter bounds ($n \in [1, 10000]$ or floating grids).
   - Fast probabilistic check (<5s).
2. **Tier 2: Z3 SMT Solver Gateway**
   - Formulates expression, sets variable bounds, and negates the claim $\neg P(\mathbf{x})$.
   - Solves for satisfiability with QF_LIA, QF_LRA, or QF_NRA solver.
   - Extracts satisfying assignment model when result is `sat`.
3. **Tier 3: SymPy Exact Symbolic Solver**
   - Computes exact symbolic roots, solving equations over $\mathbb{R}$ or $\mathbb{C}$.
   - Prevents floating-point precision issues using exact rational arithmetic (`sympy.Rational`).

#### 2. Timeout & Execution Control
- Total wall-clock execution time capped at **60.0 seconds** using `asyncio.wait_for` or threaded solver timeout handles.

#### 3. Knowledge Graph Status Update
- If a counterexample is found:
  - Return counterexample mapping (e.g. `{"n": 41}`).
  - Update target node in EGS SQLite store: `status = EpistemicStatus.REFUTED`, `tier = VerificationTier.TIER_0_CONJECTURE`.
  - Create a `COUNTEREXAMPLE_FOR` edge in EGS.

#### 4. Data Models (Pydantic)
```python
class VariableBound(BaseModel):
    name: str
    var_type: str = "int"  # "int", "real", "complex"
    min_val: Optional[float] = 0
    max_val: Optional[float] = 1000

class CounterexampleSearchRequest(BaseModel):
    claim_id: Optional[str] = None
    formula_latex: Optional[str] = None
    formula_smt: Optional[str] = None
    variables: List[VariableBound]
    search_depth: str = "comprehensive"  # "fast", "comprehensive"
    timeout_seconds: float = 60.0

class CounterexampleSearchResponse(BaseModel):
    claim_id: Optional[str]
    is_valid: bool
    counterexample_found: bool
    counterexample: Optional[Dict[str, Any]] = None
    tier_used: str  # "COMPUTATIONAL", "Z3_SMT", "SYMPY_EXACT"
    execution_time_ms: float
    egs_status_updated: str  # "REFUTED", "UNCHANGED", "VERIFIED_LOCAL"
```

---

### 3.3 Requirement R7: Research Strategy Planner (Team G)

#### API Endpoints: `POST /mde/strategy/plan` and `GET /mde/strategy/decompose`

#### 1. Hierarchical Open Problem Decomposition
Decomposes target open problems into a Directed Acyclic Graph (DAG) of intermediate sub-goals and lemmas.

**Concrete Case Study: Riemann Hypothesis Decomposition Tree**:
- **Root Goal ($G_0$)**: Proof of $\text{Re}(s) = 1/2$ for all non-trivial zeros of $\zeta(s)$.
  - **Sub-goal $L_1$ (Zero-Free Region)**: Prove $\zeta(s) \neq 0$ for $\sigma \ge 1 - \frac{c}{\log t}$.
    - *Dependencies*: Prime Number Theorem, Trigonometric Identity $3 + 4\cos\theta + \cos 2\theta \ge 0$.
  - **Sub-goal $L_2$ (Hardy Z-Function Zeros)**: Prove $Z(t) = e^{i\theta(t)}\zeta(1/2 + it)$ has infinitely many real zeros.
    - *Dependencies*: Gram Points, Euler-Maclaurin Summation.
  - **Sub-goal $L_3$ (Lindelöf Hypothesis Bounds)**: Prove $\zeta(1/2 + it) = O(t^\epsilon)$.
    - *Dependencies*: Weyl Differencing, Exponential Sum Estimates.
  - **Sub-goal $L_4$ (Dirichlet L-Function Generalization)**: Prove non-vanishing of $L(s, \chi)$ on $\text{Re}(s) = 1$.

#### 2. Lemma Prioritization Index Algorithm
Each open lemma $L_i$ in the decomposition tree is scored by Prioritization Index $P(L_i)$:
$$P(L_i) = \frac{\text{Impact}(L_i) \cdot \text{TacticConfidence}(L_i)}{\text{ProofComplexity}(L_i) + \text{FailedAttempts}(L_i) + 1.0}$$
Where:
- $\text{Impact}(L_i)$: Number of downstream lemmas depending on $L_i$.
- $\text{TacticConfidence}(L_i)$: Availability of matching Lean 4 Mathlib tactics (`ring_nf`, `linarith`, `positivity`).
- $\text{ProofComplexity}(L_i)$: Estimated AST size of sub-goal.
- $\text{FailedAttempts}(L_i)$: Count of previous failed MCTS/Lean attempts from mathematical memory.

#### 3. Data Models (Pydantic)
```python
class ProblemDecompositionNode(BaseModel):
    lemma_id: str
    title: str
    statement: str
    target_domain: str
    depth: int
    dependencies: List[str]
    status: str  # "UNPROVEN", "VERIFIED", "REFUTED", "IN_PROGRESS"
    priority_score: float

class StrategyPlanResponse(BaseModel):
    problem_id: str
    problem_name: str
    root_lemma_id: str
    total_lemmas: int
    prioritized_queue: List[ProblemDecompositionNode]
    recommended_next_attack: ProblemDecompositionNode
```

---

### 3.4 Requirement R8: Mathematical Memory & Snapshotting (Team H)

#### API Endpoints: `POST /mde/memory/snapshot`, `GET /mde/memory/snapshots`, `GET /mde/memory/failed-tactics`

#### 1. Persistent Database Schema Extension (`axiom/core/knowledge_graph/schema.py`)
Add persistent SQLite storage table `memory_snapshots`:
```sql
CREATE TABLE IF NOT EXISTS memory_snapshots (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    problem_context TEXT NOT NULL,
    snapshot_data TEXT NOT NULL, -- JSON blob containing active hypotheses, open questions, metadata
    timestamp REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS failed_proof_attempts (
    id TEXT PRIMARY KEY,
    goal_hash TEXT NOT NULL,
    expression TEXT NOT NULL,
    target TEXT NOT NULL,
    tactic_sequence TEXT NOT NULL, -- JSON array of tactics
    failure_reason TEXT NOT NULL, -- "TIMEOUT", "SYNTAX_ERROR", "TACTIC_FAILED"
    timestamp REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_failed_goal_hash ON failed_proof_attempts(goal_hash);
```

#### 2. Tactic Search Failure Guard Integration
During MCTS search expansion (`axiom/core/reasoning/mcts.py`):
1. Compute goal state AST hash $H = \text{SHA256}(\text{current\_state})$.
2. Query `failed_proof_attempts` where `goal_hash = H`.
3. Prune tactic actions that match previously recorded failed tactic sequences, preventing infinite loops or repeating dead ends.

#### 3. Useful Transformations & Equivalent Formulations Log
- Maintain persistent lookup table of verified equivalences ($A \iff B$) discovered during proof searches to serve as shortcut tactics in future search sessions.

---

### 3.5 Requirement R9: Independent Verification & Architecture Review (Team I & Team J)

#### API Endpoint: `POST /mde/verification/review`

#### 1. Verification Review & Cross-Checking Pipeline
Coordinates checks across multiple independent subsystems before promoting an EGS node to `VERIFIED`:

```
   +--------------------------------------------------------+
   |             Verification Review Controller             |
   +--------------------------------------------------------+
              /                  |                  \
             v                   v                   v
   +-------------------+ +---------------+ +-------------------+
   | 1. SMT Gateway    | | 2. Lean 4     | | 3. Script Sanity  |
   |    Counterexample | |    Subprocess | |    Guard          |
   |    Check (Z3)     | |    Compiler   | |    (No 'sorry')   |
   +-------------------+ +---------------+ +-------------------+
             \                   |                  /
              v                  v                 v
   +--------------------------------------------------------+
   |            Discrepancy Resolution & Audit Log          |
   +--------------------------------------------------------+
```

#### 2. Cross-Checking & Discrepancy Resolution Logic
- **Case 1: SMT SAT (Counterexample found)** AND **MCTS Proof Claimed**:
  - *Conflict detected!* Block status update. Set review verdict to `VERIFICATION_CONFLICT`. Flag for human review.
- **Case 2: SMT UNSAT (No counterexample)** AND **Lean Compiler Success (No `sorry`)**:
  - Verdict: `VERIFIED`. Promote node status in EGS to `VERIFIED` and tier to `TIER_2_PROVEN`.
- **Case 3: Lean Compiler Output Contains `sorry` / `admit`**:
  - Verdict: `REJECTED_INCOMPLETE`. Retain status as `CONJECTURED`.

#### 3. Data Models (Pydantic)
```python
class VerificationReviewRequest(BaseModel):
    claim_id: str
    lean_script: str
    smt_formula: Optional[str] = None
    variables: Dict[str, Any]

class VerificationReviewResponse(BaseModel):
    claim_id: str
    verdict: str  # "VERIFIED", "REFUTED", "VERIFICATION_CONFLICT", "REJECTED_INCOMPLETE"
    smt_passed: bool
    compiler_passed: bool
    script_clean: bool
    audit_notes: List[str]
    timestamp: float
```

---

### 3.6 Requirement R10: Monorepo Integration, FastAPI Routes, Test Plan, and Prize Alignment Structure

#### 1. Monorepo Package Integration Architecture
```
axiom/
├── core/
│   ├── conjecture/          # R4: Hypothesis Scorer & Pattern Miner
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   ├── novelty_scorer.py
│   │   └── filters.py
│   ├── counterexample/      # R5: Multi-tier Counterexample Search
│   │   ├── __init__.py
│   │   ├── gateway.py
│   │   ├── computational_sweep.py
│   │   └── sympy_solver.py
│   ├── strategy/           # R7: Research Strategy & Problem Decomposition
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   └── riemann_tree.py
│   ├── memory/             # R8: Persistent Memory & Snapshotting
│   │   ├── __init__.py
│   │   ├── working_memory.py
│   │   └── persistent_store.py
│   └── verification/       # R9: Independent Verification Review
│       ├── smt_gateway.py
│       ├── lean_exporter.py
│       └── review_controller.py
└── services/
    └── api_gateway/
        └── routes/
            └── mde.py       # FastAPI router for /mde/* endpoints
```

#### 2. FastAPI Route Specifications
- `POST /mde/conjectures/generate`: Generate and rank candidate conjectures.
- `POST /mde/counterexample/search`: Execute 3-tier counterexample search (<60s).
- `POST /mde/strategy/plan`: Generate prioritized lemma attack plan.
- `GET  /mde/strategy/decompose`: Retrieve problem decomposition DAG.
- `POST /mde/memory/snapshot`: Save research session snapshot to SQLite.
- `GET  /mde/memory/snapshots`: List historical snapshots.
- `POST /mde/verification/review`: Execute multi-verifier review check.

#### 3. Test Plan
- **Unit Tests**:
  - `tests/test_conjecture_generator.py`: Verify pattern generation, novelty formula output, and weak conjecture filtering.
  - `tests/test_counterexample_gateway.py`: Test Z3 parameter sweeps and SymPy exact root finding within 60s.
  - `tests/test_strategy_planner.py`: Verify DAG decomposition of Riemann Hypothesis and lemma scoring.
  - `tests/test_memory_snapshots.py`: Test SQLite snapshot persistence and failed tactic pruning.
  - `tests/test_verification_review.py`: Test discrepancy resolution (SMT SAT vs MCTS proof).
- **Integration Tests**:
  - `tests/test_mde_pipeline.py`: Full end-to-end execution from conjecture generation to verification review.

#### 4. Document Structure for `docs/mde_prize_alignment.md`
```markdown
# MDE Millennium Prize Alignment Report: Riemann Hypothesis & Zeta Zeros

## 1. Executive Summary
- Evaluation of AXIOM MDE capabilities against Clay Millennium Prize criteria.

## 2. Target Verification Domain Breakdown
- Basic Number Theory (Binomial expansion, prime factorization lemmas).
- Analytic Number Theory (Riemann Zeta function zero tracking, Dirichlet series).

## 3. Capability Gap Analysis
- Scorecard across Knowledge, Reasoning, Formal Verification, Hypothesis Generation, and Literature Coverage.

## 4. Architectural Contributions to the Riemann Hypothesis
- Zero-free region lemma decomposition.
- Numerical vs SMT formal verification of zeta zeros on the critical line $\text{Re}(s) = 1/2$.

## 5. Strategic Roadmap & Recommendations
- Next steps for expanding Mathlib Lean 4 tactic coverage for analytic number theory.
```

---

## 4. Caveats

1. **Local Compiler Binaries**: Lean 4 (`lean`), Coq (`coqc`), or Isabelle compilers may not be installed in all test environments. The execution architecture must include fallback simulation modes with clear warning diagnostics.
2. **Nonlinear Real Arithmetic (NRA) Complexity**: Z3 SMT checking for non-linear real inequalities in analytic number theory (e.g. transcendental functions like $\zeta(s)$) may return `unknown` or hit the 60s timeout limit; SymPy or numerical grid bounds serve as fallback tiers.

---

## 5. Conclusion

This design and specification report establishes a comprehensive blueprint for MDE requirements R4, R5, R7, R8, R9, and R10. It delivers complete mathematical formulas, Pydantic schemas, database migrations, multi-tier search algorithms, strategy decomposition trees (including the Riemann Hypothesis), and cross-verification review logic needed for downstream implementation.

---

## 6. Verification Method

To verify the implementation of this specification once coded:

1. **Run Pytest Suite**:
   ```bash
   pytest tests/test_conjecture_generator.py tests/test_counterexample_gateway.py tests/test_strategy_planner.py tests/test_memory_snapshots.py tests/test_verification_review.py -v
   ```
2. **Validate FastAPI Endpoint Schemas**:
   Inspect OpenAPI documentation at `http://localhost:8000/docs` to verify endpoints:
   - `POST /mde/conjectures/generate`
   - `POST /mde/counterexample/search`
   - `POST /mde/strategy/plan`
   - `POST /mde/memory/snapshot`
   - `POST /mde/verification/review`
3. **Verify Database Migrations**:
   Inspect SQLite database schema using:
   ```bash
   python -c "from axiom.core.knowledge_graph.db import EpistemicStore; store = EpistemicStore('axiom.db'); print(store.conn.execute(\"SELECT name FROM sqlite_master WHERE type='table';\").fetchall())"
   ```
   Confirm presence of `memory_snapshots` and `failed_proof_attempts` tables.
4. **Check Prize Alignment Document**:
   Verify creation and formatting of `docs/mde_prize_alignment.md`.
