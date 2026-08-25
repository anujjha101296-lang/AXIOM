# AXIOM Pilot Baseline & Technical Specification

## 1. System Versions
- **Frontend Version**: Next.js 16.3.0 (App Router, TypeScript 5.x, Webpack fallback)
- **Backend Version**: Python 3.13.9, FastAPI 0.110+, Uvicorn 0.28+
- **Database Version**: SQLite (local dev), Alembic schema migration `e5f66185a747`
- **Primary LLM Provider**: OpenAI (`gpt-4o`, `gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`, `claude-3-5-haiku`)
- **Embedding Provider**: Cosine KNN over SQLite (`axiom.research.vector_store`)
- **Formal Verification Backends**: Lean 4 Interactive Prover (v4.3), Z3 SMT Solver Gateway (v4.12)
- **Sandboxed Execution**: Python 3.13 Subprocess Sandbox with RAM/CPU and AST safety traps

## 2. Research Tools Allowlist
- `discover_sources`: Query candidates for external evidence
- `fetch_source`: SSRF-safe HTTP fetching, script stripping, prompt injection sanitization
- `search_evidence` / `search_project_knowledge`: Vector store KNN search over ingested PDFs
- `read_document_evidence`: Chunk-level exact text retrieval with source provenance
- `formulate_lemma` & `to_lean4`: Auto-formalization to Lean 4 code
- `verify_lean4`: Kernel-level Lean 4 proof checker
- `solve_smt`: Z3 SMT finite domain counterexample solver
- `execute_sandbox`: Sandboxed Python numerical simulation engine

## 3. Known Technical Limitations
1. **Search Discovery**: Candidate discovery uses candidate stubs unless live Google/Bing Search API keys are configured in environment variables (`fetch_source` is 100% real HTTP).
2. **Host Lean 4 Binary**: Host OS must have `elan` / `lean` binary in PATH for Lean 4 verification (handled automatically inside Docker container).
3. **PDF Math OCR**: Text parser extracts plain text; complex multi-column LaTeX equations require OCR post-processing.
