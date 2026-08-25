# AXIOM Competitive Pilot Matrix & Benchmarking

## Test Setup
- **Identical Test Question**: "Investigate bounded zero distribution for the Riemann Zeta function and verify finite domain counterexamples up to $N = 10,000,000$."

| Metric / Dimension | ChatGPT Deep Research | Claude 3.5 Sonnet | Perplexity Pro | AXIOM v0.1 |
| :--- | :--- | :--- | :--- | :--- |
| **Literature Search** | High (Web Text) | Medium (Prompt Text) | High (Web Text) | **High (arXiv + PDF Ingestion + Exact Chunk Provenance)** |
| **Computational Simulation** | None | None | None | **Real Sandboxed Python Subprocess (10,000,000 cases)** |
| **Counterexample Sweep** | None | None | None | **Automated Z3 SMT Solver Gateway** |
| **Formal Verification** | None (LLM Text) | None (LLM Text) | None | **Kernel-Level Lean 4 Formal Checker (`by rfl`)** |
| **Truthfulness Guarantee** | Low (Plausible Text) | Low (Plausible Text) | Low (Web Snippets) | **High (Never labels LLM text as verified proof)** |
| **Approach Memory** | None (Session) | None (Session) | None (Session) | **Persistent (Rejects repeated failed strategies)** |
| **Audit Trail & Control** | Low | Low | Low | **High (Domain Event Stream & Emergency Stop Overrides)** |

## Summary Verdict
AXIOM is uniquely positionable because existing AI platforms produce unverified natural language text summaries. AXIOM executes real sandboxed Python experiments, sweeps finite Z3 SMT counterexamples, and checks formal proofs against the Lean 4 kernel.
