# AXIOM Control Plane & Research Operating System Architecture

## 1. Executive Summary
AXIOM Phase 20 consolidates all previously built engines (Real Model Runtime, Semantic Retrieval, External Research, Provenance Graph, Hypotheses, Sandbox Experiments, Lean 4 / SMT Formal Mathematics, Long-Horizon Research, Challenge Harness, and Autonomous Mission Control) into **One Authoritative Control Plane**.

---

## 2. Core Architectural Principles
1. **Single Source of Truth**: Database-backed mission and task states (`research_missions`, `mission_tasks`, `domain_events`) are authoritative across API workers, subagents, and Web UI.
2. **Strict Tool Policy Engine**: Every tool execution passes: User Auth $\rightarrow$ Mission Auth $\rightarrow$ Agent Auth $\rightarrow$ Tool Policy $\rightarrow$ Budget Check $\rightarrow$ Input Validation $\rightarrow$ Execution $\rightarrow$ Audit.
3. **Decoupled Worker Execution**: Web API request lifecycles are strictly synchronous (sub-second responses), while long-running research loops execute via background worker nodes.
4. **Append-Only Domain Event Log**: All state transitions and tool calls emit immutable domain events for auditability and observability.

---

## 3. Specialist Agent Registry
- `RESEARCH_PLANNER`: Formulates problem decomposition and task graphs.
- `LITERATURE_RESEARCHER`: Conducts semantic document retrieval and external source discovery.
- `MATHEMATICIAN`: Formulates lemmas, conjectures, and algebraic bounds.
- `FORMALIZER`: Converts natural language claims into Lean 4 / SMT Z3 formal statements.
- `PROOF_SEARCHER`: Executes interactive tactic search and automated SMT solving.
- `COUNTEREXAMPLE_RESEARCHER`: Searches finite domains for refuting witnesses.
- `EXPERIMENTALIST`: Executes safe sandboxed Python code.
- `CRITIC`: Audits research directions and recommends pivots/revisions.
- `SYNTHESIZER`: Compiles evidence-backed final research papers.

---

## 4. Production Deployment Topology
- **Web Tier (Vercel / Next.js)**: Host Web UI workspace and stateless HTTP API routes.
- **Worker Tier (Docker Stack)**: Persistent worker processes running long-horizon loops, sandboxed execution, and Lean 4 proof verification.
- **Database & Storage**: PostgreSQL (relational & JSONB state), SQLite/Chroma (Vector store), Redis (Worker locks & event broker).
