# Milestone 2 Requirement 1 Analysis: Symbolic Math Engine (`axiom/core/symbolic/sympy_engine.py`)

## Executive Summary
This report presents a comprehensive architectural specification and design analysis for `axiom/core/symbolic/sympy_engine.py`, which implements the `SymbolicMathEngine` for Axiom's Mathematical Discovery Engine (MDE). The engine guarantees exact mathematical computations by eliminating IEEE 754 floating-point precision drift through exact rational arithmetic (`sp.Rational`), symbolic identity verification (`sp.simplify(lhs - rhs) == 0`), exact integer counterexample grid solving, exact Riemann zeta zero evaluation (`sp.zeta(n)`), and finite Dirichlet series expansion ($\sum_{n=1}^k a_n / n^s$).

---

## 1. Architectural Design of `SymbolicMathEngine`

### 1.1 Module Location & Structure
- **Module File**: `axiom/core/symbolic/sympy_engine.py`
- **Package Init**: `axiom/core/symbolic/__init__.py`
- **Primary Class**: `SymbolicMathEngine`

### 1.2 Exception Hierarchy
```python
class SymbolicEngineError(Exception):
    """Base exception for symbolic math engine errors."""
    pass

class InvalidFormulaError(SymbolicEngineError):
    """Raised when formula string parsing fails or expression is syntactically invalid."""
    pass

class EvaluationError(SymbolicEngineError):
    """Raised when symbolic evaluation or simplification fails."""
    pass

class GridSearchTimeoutError(SymbolicEngineError):
    """Raised when integer grid counterexample search exceeds execution constraints."""
    pass
```

### 1.3 Result Data Transfer Models (Pydantic v2)
```python
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class IdentityVerificationResult(BaseModel):
    is_identical: bool = Field(..., description="True if LHS and RHS are symbolically identical (LHS - RHS == 0)")
    lhs_expr: str = Field(..., description="String representation of LHS")
    rhs_expr: str = Field(..., description="String representation of RHS")
    difference: str = Field(..., description="Exact difference LHS - RHS")
    difference_simplified: str = Field(..., description="Simplified difference sp.simplify(LHS - RHS)")
    variables: List[str] = Field(default_factory=list, description="Variables detected in formula")
    method: str = Field(default="sp.simplify", description="Simplification technique used")

class CounterexampleResult(BaseModel):
    found: bool = Field(..., description="True if a counterexample was found within grid bounds")
    claim_lhs: str = Field(..., description="LHS equation string")
    claim_rhs: str = Field(..., description="RHS equation string")
    assignment: Optional[Dict[str, int]] = Field(default=None, description="Variable integer assignment that violates claim")
    lhs_val: Optional[str] = Field(default=None, description="Exact rational LHS value at assignment")
    rhs_val: Optional[str] = Field(default=None, description="Exact rational RHS value at assignment")
    discrepancy: Optional[str] = Field(default=None, description="Exact difference LHS - RHS at assignment")
    searched_grid_size: int = Field(default=0, description="Total grid points evaluated")

class ZetaEvaluationResult(BaseModel):
    input_s: str = Field(..., description="String representation of input s")
    exact_value: str = Field(..., description="Exact SymPy expression result string")
    latex_value: str = Field(..., description="LaTeX representation of result")
    is_zero: bool = Field(..., description="True if zeta(s) evaluates to exactly 0")
    numeric_approximation: Optional[str] = Field(default=None, description="Arbitrary precision decimal approximation if precision requested")

class DirichletSeriesResult(BaseModel):
    terms_count: int = Field(..., description="Number of terms k in partial sum")
    expression: str = Field(..., description="SymPy string representation of sum")
    latex_expression: str = Field(..., description="LaTeX representation of sum")
    evaluated_value: Optional[str] = Field(default=None, description="Exact evaluated result if s was provided")
```

---

## 2. Detailed Technical Requirements & Feature Specifications

### 2.1 Precision Drift Elimination & Exact Rational Arithmetic (`sp.Rational`)
Standard floating-point representation leads to errors such as `0.1 + 0.2 != 0.3`. The `SymbolicMathEngine` must construct all numeric expressions using SymPy's exact `sp.Rational` or `sp.sympify(expr, rational=True)`.

#### Core Methods:
- `parse_exact(expr_input: Union[str, int, float, sp.Expr]) -> sp.Expr`:
  Converts inputs to exact SymPy expressions. String expressions like `"1/3"` or `"0.5"` are parsed with `rational=True` so floats become exact fractions (`sp.Rational(1, 2)`).
- `exact_rational(numerator: int, denominator: int = 1) -> sp.Rational`:
  Constructs exact rational fraction `p/q`.
- `evaluate_exact_rational(expr_str: str) -> sp.Rational`:
  Evaluates closed-form arithmetic string over rationals.

### 2.2 Symbolic Identity Verification (`sp.simplify(lhs - rhs) == 0`)
To check whether $LHS \equiv RHS$ universally:
1. Parse `lhs` and `rhs` into SymPy `Expr` objects.
2. Form the difference expression: $Diff = LHS - RHS$.
3. Compute simplified forms:
   - `sp.simplify(Diff)`
   - Fallback strategies if `sp.simplify` is inconclusive: `sp.trigsimp(Diff)`, `sp.expand(Diff)`, `sp.powsimp(Diff)`, or `Diff.equals(0)`.
4. Return `IdentityVerificationResult` with `is_identical = True` if the simplified difference evaluates to exact zero (`0` or `sp.S.Zero`).

### 2.3 Exact Integer Counterexample Grid Solver
To verify or falsify candidate claims (e.g. $(a+b)^2 \stackrel{?}{=} a^2 + b^2$) over discrete domains:
- Method signature:
  `find_integer_counterexample(claim_lhs: str, claim_rhs: str, variable_bounds: Dict[str, Tuple[int, int]]) -> CounterexampleResult`
- Algorithm:
  1. Extract variables from `claim_lhs` and `claim_rhs`.
  2. Generate Cartesian product of integer bounds for each variable (e.g. $a \in [1, 5], b \in [1, 5]$).
  3. For each assignment, evaluate `LHS` and `RHS` using exact rational arithmetic (`sp.Rational`).
  4. If `LHS != RHS`, construct and return `CounterexampleResult(found=True, assignment={...}, lhs_val=..., rhs_val=...)`.
  5. If grid search exhausts without discrepancy, return `CounterexampleResult(found=False)`.

### 2.4 Exact Riemann Zeta Zero Evaluator (`sp.zeta(n)`)
- Method signature:
  `evaluate_zeta(s: Union[int, float, str, sp.Expr], precision: Optional[int] = None) -> ZetaEvaluationResult`
- Behavior:
  - Exact Symbolic Values:
    - Trivial zeros: $\zeta(-2n) = 0$ for $n \ge 1$.
    - Positive even integers: $\zeta(2) = \frac{\pi^2}{6}$, $\zeta(4) = \frac{\pi^4}{90}$, $\zeta(6) = \frac{\pi^6}{945}$.
    - Special values: $\zeta(0) = -\frac{1}{2}$, $\zeta(-1) = -\frac{1}{12}$.
  - Arbitrary-Precision Float Evaluation:
    - When `precision` (number of decimal digits, e.g. 30 or 50) is specified, evaluate using `sp.N(sp.zeta(s), precision)` to avoid float precision drift.

### 2.5 Dirichlet Series Expansion ($\sum_{n=1}^k a_n / n^s$)
- Method signature:
  `expand_dirichlet_series(coefficients: Union[List[Union[int, float, str, sp.Expr]], str], k: int, s_val: Optional[Union[int, str, sp.Expr]] = None) -> DirichletSeriesResult`
- Behavior:
  - Constructs finite partial sum: $D(s) = \sum_{n=1}^k \frac{a_n}{n^s}$.
  - Supports constant lists (e.g. $[1, 1, 1, \dots]$ for partial Riemann zeta sums), alternating series ($[1, -1, 1, -1, \dots]$ for Dirichlet eta sums), or general numeric/symbolic coefficient lists.
  - Computes exact partial sums when $s$ is specified as an exact rational or integer (e.g. $s=2, k=3 \implies 1 + 1/4 + 1/9 = 49/36$).

---

## 3. Integration Analysis with Axiom & MDE Core

| Subsystem | Integration Point | Functional Interaction |
|---|---|---|
| **EGS Schema (`schema.py`)** | `MathematicalObjectNode.symbolic_representation` | `SymbolicMathEngine.parse_exact()` parses LaTeX/SymPy representation strings into exact symbolic tree nodes. |
| **EGS Schema (`schema.py`)** | `ConjectureNode` / `MathematicalClaimNode` | Counterexample solver updates node status to `REFUTED` when a counterexample assignment is discovered. |
| **Theorem Retrieval (`retrieval/engine.py`)** | `SemanticScore` | Retrieval engine calls `verify_identity(f1, f2)` to calculate exact semantic equivalence between query formula and knowledge graph theorems. |
| **SMT Gateway (`smt_gateway.py`)** | Hybrid SMT & Symbolic verification | Combines Z3 SMT solver results with exact SymPy algebraic simplifications for real and polynomial identities. |

---

## 4. Implementation Recommendations & Test Design (`tests/test_mde_symbolic.py`)

### 4.1 Recommended File Structure
```
axiom/core/symbolic/
├── __init__.py
└── sympy_engine.py

tests/
└── test_mde_symbolic.py
```

### 4.2 Comprehensive Test Cases Specification for `tests/test_mde_symbolic.py`

1. **`test_exact_rational_arithmetic_no_drift`**:
   - Assert `parse_exact("0.1") + parse_exact("0.2") == sp.Rational(3, 10)`.
   - Assert string fractions `"1/3" + "2/3" == 1`.
   - Assert exact division without IEEE float conversion.

2. **`test_algebraic_identity_verification`**:
   - Binomial expansion: `verify_identity("(a+b)^2", "a^2 + 2*a*b + b^2")` -> `is_identical=True`.
   - Difference of squares: `verify_identity("x^2 - y^2", "(x - y)*(x + y)")` -> `is_identical=True`.
   - Trigonometric identity: `verify_identity("sin(x)^2 + cos(x)^2", "1")` -> `is_identical=True`.
   - Non-identical claim: `verify_identity("(a+b)^2", "a^2 + b^2")` -> `is_identical=False`.

3. **`test_integer_counterexample_grid_solver`**:
   - False claim `(a+b)^2 == a^2 + b^2` for $a, b \in [1, 5]$:
     - Returns `found=True`, `assignment={"a": 1, "b": 1}`, `lhs_val="4"`, `rhs_val="2"`.
   - Valid identity `x^2 - y^2 == (x-y)*(x+y)` for $x, y \in [-5, 5]$:
     - Returns `found=False`, `assignment=None`.

4. **`test_exact_zeta_evaluator`**:
   - Trivial zero: `evaluate_zeta(-2)` -> `exact_value="0"`, `is_zero=True`.
   - Trivial zero: `evaluate_zeta(-4)` -> `exact_value="0"`, `is_zero=True`.
   - Basel problem: `evaluate_zeta(2)` -> `exact_value="pi**2/6"`.
   - Special value: `evaluate_zeta(0)` -> `exact_value="-1/2"`.
   - Arbitrary-precision evaluation at first non-trivial zero $s = 1/2 + 14.13472514173469379... i$.

5. **`test_dirichlet_series_expansion`**:
   - Partial sum $k=3, s=2, a_n = [1, 1, 1]$: $1 + 1/4 + 1/9 = 49/36$. Assert `evaluated_value == "49/36"`.
   - Partial sum $k=4, s=1, a_n = [1, -1, 1, -1]$: $1 - 1/2 + 1/3 - 1/4 = 7/12$. Assert `evaluated_value == "7/12"`.

6. **`test_error_handling_and_boundaries`**:
   - Invalid syntax string `"a + * b"` raises `InvalidFormulaError`.
   - Empty variable bounds in grid solver raises `InvalidFormulaError` or `SymbolicEngineError`.
