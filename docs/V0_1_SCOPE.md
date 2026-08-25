# AXIOM v0.1 Launch Candidate - Scope

## IN SCOPE
- **Research Graph Creation**: Ingestion of documents into a SQLite-backed VectorStore.
- **Autonomous Exploration Loop**: Multi-step hypothesis generation and validation using `ModelClient` (OpenAI/Gemini failover).
- **Knowledge Graph Representation**: `EpistemicStore` representing claims, entities, and evidence as directed acyclic nodes.
- **Formal Verification MVP**: Basic SMT modular checking using `z3` and deterministic Python fallback; Lean4 theorem script export.
- **Dashboard UI**: Next.js-based telemetry view of active research sessions and evidence nodes.

## OUT OF SCOPE
- Serverless worker orchestration for infinite-horizon research (currently runs synchronous local limits).
- Full interactive Lean4 server integration.
- Distributed production databases (currently using SQLite for Epistemic and Vector stores).
- Complex team-based multi-user RBAC.

## KNOWN LIMITATIONS
- Vector retrieval isexact cosine-similarity (Python-based), suitable only for small corpora.
- SMT solver falls back to Python iterative checking if `z3` dependencies are missing.
- LLM generation will fallback to deterministic mock text if API keys run out of budget or timeout repeatedly.
- Single-node architecture.
