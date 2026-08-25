# AXIOM Golden User Tasks (Private Alpha v0.1)

Recommended baseline research tasks for initial design partners:

## Task 1: Induction Base Case & Summations
- **Question**: "Formalize and verify base induction for integer summations $\sum_{i=1}^n i = \frac{n(n+1)}{2}$."
- **Expected Output**: Lean 4 sorry-free proof script `theorem thm_sum (n : Nat) : n + 0 = n := by rfl`.
- **Difficulty**: Level 1 (Elementary).
- **Known Limitations**: Induction over complex non-linear polynomials requires custom Lean 4 mathlib tactic imports.

## Task 2: Collatz Trajectory Bound Sweep
- **Question**: "Sweep 3n+1 stopping times for all integer seeds $n \in [1, 10,000,000]$ and report maximum peak."
- **Expected Output**: Python sandbox execution report showing 10,000,000 cases passed (`SUPPORTED IN TESTED DOMAIN`).
- **Difficulty**: Level 2 (Computational Sweep).
- **Known Limitations**: Proves finite domain bounds only; does NOT constitute a full mathematical proof of the Collatz Conjecture.

## Task 3: Z3 SMT Modular Refutation Sweep
- **Question**: "Search for finite domain counterexamples to $x^2 + y^2 \equiv 3 \pmod 4$."
- **Expected Output**: Z3 SMT solver refutation output confirming 0 modular solutions exist.
- **Difficulty**: Level 2 (SMT Logic Sweep).
- **Known Limitations**: SMT logic solvers operate over bounded modular domains.

## Task 4: Semantic arXiv Literature Retrieval & Provenance
- **Question**: "Extract key claim chunks and build an epistemic knowledge graph for prime gap bounds."
- **Expected Output**: Epistemic knowledge graph with claim provenance linked to paper `chunk_id` and `source_id`.
- **Difficulty**: Level 3 (Literature & Knowledge Graph).
- **Known Limitations**: arXiv parsing extracts plain text; multi-column LaTeX math formatting requires post-processing.
