# Product Differentiation: Why AXIOM?

**Why not ChatGPT or Claude?**
General-purpose LLMs are probabilistic text generators. They lack interactive formal verification. AXIOM does not trust the LLM; it uses the LLM to propose hypotheses and then uses deterministic tools (Z3 SMT solver, Python sandboxes) to verify them. 

**Why not Perplexity?**
Perplexity is excellent at web retrieval and summarization but does not perform experimental verification or mathematical proofs. AXIOM builds an epistemic knowledge graph and explicitly verifies claims via computational kernels, rather than just citing a web page.

**Why not Cursor?**
Cursor is an AI code editor for software engineering. While excellent for writing code, it does not autonomously orchestrate long-horizon research missions, run formal theorem provers, or structure knowledge into an epistemic graph of scientific claims.

**Why not a collection of Python scripts?**
Managing VectorStores, LLM routing (with fallbacks/timeouts), secure AST-evaluated Python sandboxing, Z3 bindings, Lean 4 exporters, and a Next.js observability UI requires massive boilerplate. AXIOM provides this as an integrated, reliable Operating System.

# Vision vs Current Product

### TODAY
AXIOM is an integrated research environment. It retrieves local documents, generates structured hypotheses, and verifies bounded modular arithmetic conjectures using Z3 and safe Python sandboxing. The results are tracked in a verifiable Knowledge Graph.

### CURRENTLY BUILDING
We are expanding the verification layer to support interactive Lean 4 tactic execution (beyond just exporting scripts) and implementing persistent background workers for multi-hour research tasks.

### LONG-TERM VISION
AXIOM aims to be a fully autonomous research scientist capable of long-horizon formal reasoning, multi-agent investigation, and novel scientific discovery.
