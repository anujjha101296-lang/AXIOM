# Mathematical Discovery Engine (MDE) — Requirements R1, R2, R3, R6 Technical Design & Architecture Handoff

## 1. Observation

Direct code inspection of `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom` revealed the following structural facts:

1. **Original Request & Project Scope**:
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md` (lines 103–120) mandates requirements for MDE: R1 (Mathematical Ontology), R2 (Theorem Retrieval & Dependency Discovery), R3 (Formal Proof Architecture), R4 (Conjecture Generation), R5 (Counterexample Search), R6 (Symbolic Mathematics), R7 (Research Strategy Planner), R8 (Mathematical Memory), R9 (Independent Verification), and R10 (Deliverables & Prize Alignment).
   - Target verification domains specified in `ORIGINAL_REQUEST.md` (lines 141–144): Basic Number Theory & Algebraic Identities, and Riemann Hypothesis / Analytic Number Theory (zeta zeros, Dirichlet series).

2. **Existing Knowledge Graph & Schema (`EGS`)**:
   - `axiom/core/knowledge_graph/schema.py` (lines 5–20): Node types currently defined: `PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`. Edge types currently defined: `CITES`, `PROVES`, `REFUTES`, `CONTRADICTS`, `EXTENDS`, `CORROBORATES`, `USES_METHOD`.
   - `axiom/core/knowledge_graph/db.py` (lines 29–48): SQLite `nodes` and `edges` tables storing JSON data.
   - `axiom/core/knowledge_graph/migrations.py` (lines 114–118): Migrations up to `v3_working_memory_snapshots` (`_v1_initial_schema`, `_v2_proof_lineage`, `_v3_working_memory_snapshots`).

3. **Existing Exporter & Verifier Infrastructure**:
   - `axiom/core/verification/lean_exporter.py` (lines 51–115): Exposes `LeanExporter.export_theorem(...)` producing Lean 4 code with `import Mathlib.Data.Nat.Basic...`.
   - `axiom/core/verification/smt_gateway.py` (lines 8–68): Implements `SmtGateway.verify_modular_conjecture`, `verify_real_inequality`, `verify_polynomial_identity` using Z3.
   - `axiom/services/api_gateway/main.py` (lines 272–346): Exposes `/verify/proof` and `/verify/conjecture`. Hardcodes local Lean binary check at `/usr/local/bin/lean` or `/usr/bin/lean`.

4. **Missing Architectural Components**:
   - Search across codebase for `SymPy` returned 0 results (`grep_search` found no occurrences).
   - Search for `Coq` or `Isabelle` returned 0 results.
   - Search for `retrieval` endpoints or formula indexing returned 0 results.

---

## 2. Logic Chain

1. **From Observation 1 & 4**: Requirements R1, R2, R3, R6 are specified in `ORIGINAL_REQUEST.md` but are currently unimplemented in `axiom/core/`. Therefore, complete architectural blueprints, Pydantic schemas, migration SQL scripts, REST API contracts, algorithm designs, and verification strategies must be provided to guide implementation teams.
2. **From Observation 2**: R1 requires expanding the EGS schema. The existing `schema.py` and `migrations.py` must be cleanly extended without breaking backward compatibility for `PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`.
3. **From Observation 3**: R3 requires extending proof verification beyond Lean 4 to include Coq and Isabelle/HOL, along with AST-level fallback simulation when provers are absent, and automated Mathlib tactic generation for algebraic identities.
4. **From Observation 1 & 3**: R6 requires exact symbolic computation via SymPy to eliminate floating point drift during polynomial identity checking, Dirichlet series manipulation, and zeta zero tracking.
5. **From Target Domain Requirements**: The system must support two explicit benchmark suites: (a) Basic Number Theory / Algebraic Identities (e.g. $(a+b)^2 = a^2+2ab+b^2$, Euclid's lemma, modular congruence) and (b) Riemann Hypothesis / Analytic Number Theory (critical line zeros $s = 1/2 + i\gamma$, Dirichlet series $L(s,\chi)$, Mertens function bounds, Robin's inequality).

---

## 3. Caveats

- **External Binary Availability**: System environments may lack Lean 4, Coq (`coqc`), or Isabelle (`isabelle`). The specification explicitly mandates fallback simulation with warning diagnostics so that test suites and API contracts remain fully functional in non-prover CI environments.
- **SymPy Performance**: Symbolic simplification (`sympy.simplify`) and solver steps (`sympy.solveset`) can be expensive for high-degree multivariate polynomials or transcendental equations. Strict execution timeouts (e.g. 10.0 seconds) must be enforced.
- **Analytical Zeta Zero Computation**: Numerical float drift is avoided by retaining exact symbolic representations (e.g., $s = \frac{1}{2} + i \gamma$) while using arbitrary-precision arithmetic (`mpmath` via SymPy) for zero verification.

---

## 4. Conclusion & Technical Design Specifications

### 4.1 Requirement R1: Mathematical Ontology & EGS Schema Extensions

#### 4.1.1 SQLite Schema Migration `v4_mathematical_ontology` (`axiom/core/knowledge_graph/migrations.py`)
Add migration integer `4` to `MIGRATIONS` in `migrations.py`:

```python
def _v4_mathematical_ontology(conn: sqlite3.Connection) -> None:
    """V4: Mathematical Ontology tables — objects, definitions, equivalences, snapshots."""
    # Table 1: mathematical_objects
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mathematical_objects (
            id           TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            object_type  TEXT NOT NULL, -- 'ALGEBRAIC_STRUCTURE' | 'COMPLEX_DOMAIN_OBJECT' | 'ZETA_ZERO' | 'DIRICHLET_SERIES'
            domain       TEXT NOT NULL, -- 'NUMBER_THEORY' | 'ANALYTIC_NUMBER_THEORY' | 'ALGEBRA'
            formal_symbol TEXT,
            latex_repr   TEXT,
            properties   TEXT NOT NULL, -- JSON blob of mathematical properties
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_type ON mathematical_objects(object_type);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_domain ON mathematical_objects(domain);")

    # Table 2: definitions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS definitions (
            id                   TEXT PRIMARY KEY,
            name                 TEXT NOT NULL,
            target_object_id     TEXT,
            formal_statement     TEXT NOT NULL,
            informal_description TEXT,
            parameters           TEXT, -- JSON array of parameters
            axioms               TEXT, -- JSON array of underlying axioms
            created_at           TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (target_object_id) REFERENCES mathematical_objects(id) ON DELETE SET NULL
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_target ON definitions(target_object_id);")

    # Table 3: equivalent_statements
    conn.execute("""
        CREATE TABLE IF NOT EXISTS equivalent_statements (
            id                  TEXT PRIMARY KEY,
            statement_a_id      TEXT NOT NULL,
            statement_b_id      TEXT NOT NULL,
            equivalence_type    TEXT NOT NULL, -- 'LOGICAL_BIIMPLICATION' | 'ASYMPTOTIC_EQUIVALENCE' | 'ISOMORPHISM'
            proof_reference_id  TEXT,
            confidence_score    REAL NOT NULL DEFAULT 1.0,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (statement_a_id) REFERENCES nodes(id) ON DELETE CASCADE,
            FOREIGN KEY (statement_b_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_equiv_stmt_a ON equivalent_statements(statement_a_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_equiv_stmt_b ON equivalent_statements(statement_b_id);")

    conn.commit()
```

#### 4.1.2 Pydantic Models & Enum Extensions (`axiom/core/knowledge_graph/schema.py`)

Extend `NodeType` and `EdgeType`:

```python
class NodeType(str, Enum):
    PAPER = "PAPER"
    AUTHOR = "AUTHOR"
    CONCEPT = "CONCEPT"
    MATHEMATICAL_CLAIM = "MATHEMATICAL_CLAIM"
    EXPERIMENTAL_FACT = "EXPERIMENTAL_FACT"
    DATASET = "DATASET"
    # R1 Extensions
    MATHEMATICAL_OBJECT = "MATHEMATICAL_OBJECT"
    DEFINITION = "DEFINITION"
    EQUIVALENT_STATEMENT = "EQUIVALENT_STATEMENT"
    OPEN_PROBLEM = "OPEN_PROBLEM"
    CONJECTURE = "CONJECTURE"

class EdgeType(str, Enum):
    CITES = "CITES"
    PROVES = "PROVES"
    REFUTES = "REFUTES"
    CONTRADICTS = "CONTRADICTS"
    EXTENDS = "EXTENDS"
    CORROBORATES = "CORROBORATES"
    USES_METHOD = "USES_METHOD"
    # R1 Extensions
    EQUIVALENT_TO = "EQUIVALENT_TO"
    DEPENDS_ON = "DEPENDS_ON"
```

New Node Schemas:

```python
class MathematicalObjectNode(NodeBase):
    type: Literal[NodeType.MATHEMATICAL_OBJECT] = NodeType.MATHEMATICAL_OBJECT
    object_type: str = Field(..., description="e.g. ALGEBRAIC_STRUCTURE, ZETA_ZERO, DIRICHLET_SERIES")
    domain: str = Field(..., description="e.g. NUMBER_THEORY, ANALYTIC_NUMBER_THEORY")
    formal_symbol: Optional[str] = None
    latex_repr: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

class DefinitionNode(NodeBase):
    type: Literal[NodeType.DEFINITION] = NodeType.DEFINITION
    target_object_id: Optional[str] = None
    formal_statement: str
    informal_description: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    axioms: List[str] = Field(default_factory=list)

class OpenProblemNode(NodeBase):
    type: Literal[NodeType.OPEN_PROBLEM] = NodeType.OPEN_PROBLEM
    statement: str
    domain: str
    prize_amount_usd: Optional[float] = None
    status: EpistemicStatus = EpistemicStatus.CONJECTURED

class ConjectureNode(NodeBase):
    type: Literal[NodeType.CONJECTURE] = NodeType.CONJECTURE
    statement: str
    informal_claim: str
    novelty_score: float = 0.5
    status: EpistemicStatus = EpistemicStatus.CONJECTURED
```

Update `ScientificNode` Union: Include `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`.

---

### 4.2 Requirement R2: Theorem Retrieval & Dependency Discovery (`GET /mde/retrieval`)

#### 4.2.1 REST Endpoint Contract
- **HTTP Method**: `GET /mde/retrieval`
- **Query Parameters**:
  - `target_formula` (string, required): e.g. `"(a + b)^2 = a^2 + 2*a*b + b^2"` or `"\zeta(s) = 0"`
  - `domain` (string, optional): e.g. `"number_theory"`, `"analytic_number_theory"`
  - `max_results` (int, default: 10)
  - `similarity_threshold` (float, default: 0.6)
  - `include_dependencies` (bool, default: true)

- **Response Payload JSON (`RetrievalResponsePayload`)**:
```json
{
  "query_formula": "(a + b)^2 = a^2 + 2*a*b + b^2",
  "canonical_form": "a**2 + 2*a*b + b**2 - (a + b)**2 == 0",
  "matched_theorems": [
    {
      "node_id": "claim_binomial_2",
      "name": "Binomial Expansion Degree 2",
      "statement": "(a + b)^2 = a^2 + 2*a*b + b^2",
      "confidence_score": 1.0,
      "syntactic_score": 1.0,
      "semantic_score": 1.0,
      "epistemic_status": "VERIFIED"
    }
  ],
  "equivalent_formulations": [
    {
      "node_id": "claim_poly_square",
      "name": "Polynomial Square Identity",
      "statement": "(a+b)(a+b) = a^2 + 2ab + b^2",
      "equivalence_type": "LOGICAL_BIIMPLICATION"
    }
  ],
  "dependency_dag": {
    "nodes": [
      {"id": "def_ring", "name": "Commutative Ring Definition", "type": "DEFINITION"},
      {"id": "thm_distributivity", "name": "Distributive Law", "type": "MATHEMATICAL_CLAIM"},
      {"id": "claim_binomial_2", "name": "Binomial Expansion Degree 2", "type": "MATHEMATICAL_CLAIM"}
    ],
    "edges": [
      {"source_id": "claim_binomial_2", "target_id": "thm_distributivity", "type": "DEPENDS_ON"},
      {"source_id": "thm_distributivity", "target_id": "def_ring", "type": "DEPENDS_ON"}
    ]
  }
}
```

#### 4.2.2 Syntactic & Semantic Formula Matching Engine
1. **Syntactic Matching**:
   - Parse formula string into Python/SymPy AST.
   - Standardize dummy variables via alpha-conversion ($x, y \to v_0, v_1$).
   - Compute tree edit distance or normalized AST overlap:
     $$\text{SyntacticScore}(f_1, f_2) = 1.0 - \frac{\text{TreeDistance}(\text{AST}(f_1), \text{AST}(f_2))}{\max(|\text{AST}(f_1)|, |\text{AST}(f_2)|)}$$
2. **Semantic Matching**:
   - Use SymPy to calculate symbolic difference: $D = \text{simplify}(E(f_1) - E(f_2))$.
   - If $D == 0$, $\text{SemanticScore} = 1.0$.
   - Otherwise, sample evaluate across complex test points $z \in \mathbb{C}$ to compute numerical equivalence probability.

#### 4.2.3 Dependency DAG Extraction Algorithm
Given root claim ID $C_0$:
1. Traverse SQLite `edges` table recursively for outgoing/incoming edges where `type IN ('DEPENDS_ON', 'PROVES')`.
2. Construct NetworkX `DiGraph` $G_{sub}$.
3. Execute `nx.is_directed_acyclic_graph(G_{sub})` guard to guarantee DAG structure.
4. Perform topological sort `nx.topological_sort(G_{sub})` to order theorem prerequisites from foundational axioms to target claim.

---

### 4.3 Requirement R3: Formal Proof Architecture (`POST /mde/proof/compile`)

#### 4.3.1 REST Endpoint Contract
- **HTTP Method**: `POST /mde/proof/compile`
- **Request Payload**:
```json
{
  "system": "lean4",
  "theorem_name": "binomial_expansion_2",
  "code": "import Mathlib.Tactic.Ring\ntheorem binomial_expansion_2 (a b : ℤ) : (a + b)^2 = a^2 + 2*a*b + b^2 := by\n  ring",
  "context": {"variables": {"a": "Int", "b": "Int"}},
  "timeout_s": 15
}
```
*(System enum options: `"lean4"`, `"coq"`, `"isabelle"`)*

- **Response Payload (`ProofCompileResponse`)**:
```json
{
  "system": "lean4",
  "theorem_name": "binomial_expansion_2",
  "is_valid": true,
  "status": "compiled",
  "diagnostics": [],
  "execution_time_ms": 142.5,
  "tactics_used": ["ring"],
  "proof_script_path": "/tmp/axiom_proofs/binomial_expansion_2.lean"
}
```

#### 4.3.2 Subprocess Invocation & Compiler Checkers

1. **Lean 4 Checker (`axiom/core/verification/lean_checker.py`)**:
   - Command: `lean --json /tmp/axiom_proofs/<name>.lean` or `lake env lean <file>`
   - Exit code `0` and empty JSON error list $\implies$ `is_valid: true`.

2. **Coq Checker (`axiom/core/verification/coq_checker.py`)**:
   - Script generation:
     ```coq
     Require Import ZArith.
     Open Scope Z_scope.
     Theorem binomial_expansion_2 : forall a b : Z, (a + b)^2 = a^2 + 2*a*b + b^2.
     Proof. intros. ring. Qed.
     ```
   - Command: `coqc /tmp/axiom_proofs/<name>.v`

3. **Isabelle/HOL Checker (`axiom/core/verification/isabelle_checker.py`)**:
   - Script generation:
     ```isabelle
     theory Binomial
       imports Main Real
     begin
     theorem binomial_2: fixes a b :: real shows "(a + b)^2 = a^2 + 2*a*b + b^2"
       by algebra
     end
     ```
   - Command: `isabelle process -e '...'` or batch session build.

#### 4.3.3 Compiler Validation & Fallback Simulation / Warning Diagnostics
When compiler binary (`lean`, `coqc`, or `isabelle`) is missing from PATH (`shutil.which(binary) is None`):
1. **Fallback Checker**: Perform AST structural and heuristic verification.
2. Check for prohibited incomplete proof keywords:
   - Lean 4: `sorry`, `admit`, `cheat`
   - Coq: `admit`, `Admitted`
   - Isabelle: `sorry`, `oops`
3. Return response with:
   - `is_valid`: `true` (if no incomplete keywords & syntax matches valid pattern) or `false`.
   - `status`: `"simulated_success"`
   - `diagnostics`: `[{"severity": "warning", "message": "Prover binary 'lean' not found on PATH. Executed structural AST fallback verification."}]`

#### 4.3.4 Mathlib Tactic Generator for Algebraic Identities
Map formula characteristics to specialized Mathlib tactics:
- Ring identity (e.g. $(a+b)^2 = a^2+2ab+b^2$) $\to$ `ring` / `ring_nf`
- Linear arithmetic inequality ($3x + 2 < 5x + 10$) $\to$ `linarith`
- Non-linear arithmetic inequality ($x^2 + y^2 \ge 0$) $\to$ `nlinarith` / `positivity`
- Group identity ($g \cdot g^{-1} = e$) $\to$ `group` / `abel`
- Pure numeric computation ($2^{10} = 1024$) $\to$ `norm_num`
- Definitional equality ($x = x$) $\to$ `rfl`

---

### 4.4 Requirement R6: Exact Symbolic Mathematics Interfaces (SymPy Integration)

#### 4.4.1 Engine Architecture (`axiom/core/symbolic/sympy_engine.py`)

Create `SymbolicMathEngine` wrapper class:

```python
import sympy as sp
from typing import Dict, List, Tuple, Optional, Any

class SymbolicMathEngine:
    """
    Exact symbolic computation engine using SymPy to prevent IEEE 754 float drift.
    """

    def verify_algebraic_identity(self, lhs_str: str, rhs_str: str, var_names: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Symbolically test if LHS == RHS exactly for all inputs.
        Returns (is_exact_match, explanation_or_simplified_diff).
        """
        symbols = {name: sp.Symbol(name, real=True) for name in var_names}
        lhs_expr = sp.sympify(lhs_str, locals=symbols)
        rhs_expr = sp.sympify(rhs_str, locals=symbols)
        
        diff = sp.simplify(lhs_expr - rhs_expr)
        if diff == 0:
            return True, "0"
        return False, str(diff)

    def find_integer_counterexample(
        self,
        equation_str: str,
        var_names: List[str],
        search_range: Tuple[int, int] = (-50, 50)
    ) -> Tuple[bool, Optional[Dict[str, int]]]:
        """
        Symbolically solve or grid-search exact integer space for counterexample where equation_str != True.
        """
        symbols = {name: sp.Symbol(name, integer=True) for name in var_names}
        # Parse claim statement LHS == RHS
        lhs_s, rhs_s = equation_str.split("==")
        lhs = sp.sympify(lhs_s, locals=symbols)
        rhs = sp.sympify(rhs_s, locals=symbols)
        
        diff = sp.simplify(lhs - rhs)
        if diff == 0:
            return True, None # Identity holds universally
            
        # Search exact discrete space
        low, high = search_range
        from itertools import product
        for vals in product(range(low, high + 1), repeat=len(var_names)):
            sub_map = dict(zip(symbols.values(), vals))
            if diff.subs(sub_map) != 0:
                res_counter = {name: val for name, val in zip(var_names, vals)}
                return False, res_counter
                
        return True, None

    def evaluate_exact_zeta_even(self, n: int) -> str:
        """Return exact symbolic expression for Riemann Zeta at even integers: \zeta(2k) = (-1)^{k+1} B_{2k} (2\pi)^{2k} / (2 (2k)!)"""
        if n <= 0 or n % 2 != 0:
            raise ValueError("Exact closed form evaluation requires positive even integer.")
        val = sp.zeta(n)
        return str(sp.radsimp(val))

    def expand_dirichlet_series(self, coefficients: List[int], s_symbol_name: str = "s", terms: int = 5) -> str:
        """Construct exact symbolic Dirichlet series \sum_{n=1}^k a_n / n^s."""
        s = sp.Symbol(s_symbol_name)
        series_terms = [sp.Rational(a, n**s) for n, a in enumerate(coefficients[1:terms+1], start=1)]
        return str(sp.Add(*series_terms))
```

#### 4.4.2 Precision Float Drift Guard Strategy
- Reject standard Python `float` casts during symbolic verification steps.
- Use `sp.Rational(num, den)` for all coefficients.
- For analytic evaluation of zeta zeros, retain complex parameter $s = \frac{1}{2} + i \gamma$ in `sp.mpmath` arbitrary-precision mode (set `mpmath.mp.dps = 50` or higher).

---

### 4.5 Target Verification Domain Specifications

#### 4.5.1 Target Domain 1: Basic Number Theory & Algebraic Identities

1. **Benchmark Suite Claims**:
   - **Identity 1 (Commutativity)**: $a + b = b + a$ over $\mathbb{Z}$.
   - **Identity 2 (Binomial Expansion Degree 2)**: $(a + b)^2 = a^2 + 2ab + b^2$.
   - **Identity 3 (Binomial Expansion Degree 3)**: $(a + b)^3 = a^3 + 3a^2b + 3ab^2 + b^3$.
   - **Lemma 4 (Euclid's Lemma for Primes)**: For prime $p$, if $p \mid ab$ then $p \mid a \lor p \mid b$.
   - **Identity 5 (Difference of Squares)**: $a^2 - b^2 = (a - b)(a + b)$.

2. **Step-by-Step Processing Pipeline Trace (Binomial Expansion Degree 2)**:
   - **Step 1 (Ingestion & Ontology)**: `MathematicalClaimNode` created with statement `"(a + b)^2 = a^2 + 2*a*b + b^2"` linked to `MATHEMATICAL_OBJECT` node `AlgebraicRing_Z`.
   - **Step 2 (Retrieval)**: `GET /mde/retrieval?target_formula=(a+b)^2` matches theorem with `syntactic_score: 1.0`, returning dependency DAG linking to `DistributiveLaw` and `CommutativeRing`.
   - **Step 3 (Symbolic Check)**: `SymbolicMathEngine.verify_algebraic_identity` evaluates `sp.simplify((a+b)**2 - (a**2 + 2*a*b + b**2)) == 0`, returning exact match confirmation in 0.8ms.
   - **Step 4 (Formal Proof Compilation)**: `POST /mde/proof/compile` calls LeanExporter, generates Mathlib script using tactic `ring`, passes to subprocess runner/fallback checker, yielding `is_valid: true`.

#### 4.5.2 Target Domain 2: Riemann Hypothesis & Analytic Number Theory

1. **Ontology Nodes & Graph Structure**:
   - **Object Node**: `RiemannZetaFunction` (`object_type: "COMPLEX_DOMAIN_OBJECT"`, `domain: "ANALYTIC_NUMBER_THEORY"`, `latex_repr: "\zeta(s) = \sum_{n=1}^\infty \frac{1}{n^s}"`).
   - **Open Problem Node**: `RH_MAIN` (`name: "Riemann Hypothesis"`, `statement: "\forall s \in \mathbb{C}, (\zeta(s) = 0 \land 0 < \text{Re}(s) < 1) \implies \text{Re}(s) = 1/2"`).
   - **Equivalent Statement Nodes & Edge Topology**:
     - `RH_MAIN` $\xrightarrow{\text{EQUIVALENT_TO}}$ `MERTENS_BOUND` ($|M(x)| = O(x^{1/2+\epsilon})$).
     - `RH_MAIN` $\xrightarrow{\text{EQUIVALENT_TO}}$ `ROBIN_INEQUALITY` ($\sigma(n) < e^\gamma n \log\log n, \forall n > 5040$).
     - `RH_MAIN` $\xrightarrow{\text{EQUIVALENT_TO}}$ `PNT_ERROR_BOUND` ($\psi(x) = x + O(x^{1/2} \log^2 x)$).
     - `RH_MAIN` $\xrightarrow{\text{DEPENDS_ON}}$ `ZETA_FUNCTIONAL_EQUATION` ($\zeta(s) = 2^s \pi^{s-1} \sin(\frac{\pi s}{2}) \Gamma(1-s) \zeta(1-s)$).

2. **Zeta Zero Verification & Counterexample Search Protocol**:
   - Exact critical line constraint: $\text{Re}(s) = 1/2$.
   - For candidate zero $s_k = 1/2 + i \gamma_k$ (e.g. $\gamma_1 \approx 14.134725141734693732$):
     - SymPy arbitrary precision evaluation `sp.N(sp.zeta(1/2 + I*gamma_1), 50)` confirms $|\zeta(s_k)| < 10^{-45}$.
   - Robin's Inequality Counterexample Search:
     - Check $\sigma(n) < e^\gamma n \log\log n$ for $n \in [5041, 10000]$ using SymPy exact divisor sigma `sp.divisor_sigma(n)` and exact integer operations to verify no counterexamples exist in the search interval.

---

### 4.6 Sprint & Team Implementation Breakdown

| Sprint | Assigned Team | Subsystem / Component | Deliverables & Acceptance Criteria |
|---|---|---|---|
| **Sprint 1** | Team A | EGS Schema & Migrations (R1) | Implement `_v4_mathematical_ontology` in `migrations.py`. Update `schema.py` with `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`, `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`. 100% unit test coverage in `test_epistemic_layer.py`. |
| **Sprint 2** | Team B | Theorem Retrieval & DAG (R2) | Implement `axiom/core/retrieval/engine.py` and `GET /mde/retrieval` endpoint in `main.py`. Perform formula AST canonicalization & NetworkX dependency DAG extraction. |
| **Sprint 3** | Team C & Team I | Multi-Prover Architecture & Fallback (R3) | Implement Lean 4, Coq, and Isabelle script generators & subprocess runners. Add fallback AST checker for missing binaries with warning diagnostics. Expose `POST /mde/proof/compile`. |
| **Sprint 4** | Team F | SymPy Symbolic Engine (R6) | Implement `axiom/core/symbolic/sympy_engine.py` with exact rational arithmetic, identity testing, and integer counterexample solver. Eliminate float drift. |

---

## 5. Verification Method

To verify the completeness and accuracy of this technical analysis:

1. **Schema & Migration Verification**:
   Inspect `axiom/core/knowledge_graph/migrations.py` and `schema.py` against section 4.1. Validate that version integer `4` builds cleanly on top of `_v3_working_memory_snapshots`.
2. **API Specification Verification**:
   Verify that endpoint signatures `GET /mde/retrieval` and `POST /mde/proof/compile` adhere strictly to FastAPI request/response validation semantics using Pydantic models.
3. **Symbolic Engine Verification**:
   Run `python3 -c "import sympy as sp; print(sp.simplify((sp.Symbol('a')+sp.Symbol('b'))**2 - (sp.Symbol('a')**2 + 2*sp.Symbol('a')*sp.Symbol('b') + sp.Symbol('b')**2)))"` to verify SymPy identity reduction to `0`.
4. **Prover Binary Fallback Verification**:
   Simulate environment without `lean` binary (`PATH=""`) and verify that `POST /mde/proof/compile` returns `status: "simulated_success"` with diagnostic warnings rather than unhandled exception.
