## 2026-08-04T21:48:29Z
You are Worker Replacement 1 for Milestone 1 (Graph Store & Ingestion: EGS & EIE).
Your working directory is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m1_1_rep`.

Mandatory Input Documents:
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_m1/SCOPE.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_1/handoff.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_2/handoff.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_3/handoff.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Implementation Tasks:
1. Knowledge Graph Store & Cycle Guard (`axiom/core/knowledge_graph/`):
   - Edit `schema.py`: Define `CircularDependencyError(Exception)`, `VerificationRecord(BaseModel)`, `MCTSSearchRun(BaseModel)`.
   - Edit `db.py`:
     - Update DDL in `_init_db()` to create 4 tables (`nodes`, `edges`, `verification_records`, `mcts_search_runs`) and performance indexes (`idx_nodes_type`, `idx_edges_source`, `idx_edges_target`, `idx_verif_claim`, `idx_mcts_claim`).
     - Update `add_edge(edge: Edge, check_cycles: bool = True)` to check for directed cycles on logical edges (`PROVES`, `EXTENDS`, `USES_METHOD`) using NetworkX before inserting. Raise `CircularDependencyError` if cyclic and abort transaction. Exempt non-logical edges (`CITES`).
     - Add CRUD methods: `delete_node`, `delete_edge`, `list_nodes`, `list_edges`, `add_verification_record`, `get_verification_records`, `add_mcts_search_run`, `get_mcts_search_runs`.
     - Add `load_paper_payload(payload: IngestedPaperGraphPayload)` wrapped in transaction context.

2. LaTeX AST Parser & Epistemic Serializer (`axiom/core/parser/`):
   - Create `axiom/core/parser/latex_ast_parser.py`:
     - Implement `LatexASTParser` using `pylatexenc.latexwalker`. Process `\newtheorem` aliases, filter comments (`%`), handle starred variants & optional headers, extract math environments (theorem, lemma, definition, claim, proposition, corollary, proof) with >95% accuracy.
     - Resolve BibTeX keys from `.bib` files and `\thebibliography`/`\bibitem` blocks into `PaperNode` objects and `CITES`/`USES_METHOD` edges.
     - Define `IngestedPaperGraphPayload` Pydantic model with `to_json()`, `from_json()`, `to_knowledge_graph()`.
   - Update `arxiv_parser.py` and `semantic_tracker.py` to utilize `LatexASTParser`.

3. Test Suites & Verification (`tests/`):
   - Create `tests/test_graph_store.py`: Test schema, 4 DDL tables, CRUD operations, and direct/indirect cycle prevention raising `CircularDependencyError`.
   - Create `tests/test_parser.py`: Test AST parser, >95% math extraction accuracy, BibTeX key resolution, and `IngestedPaperGraphPayload` serialization.
   - Run tests: `pytest tests/test_graph_store.py tests/test_parser.py tests/test_epistemic_layer.py -v`. Confirm all pass.

4. Handoff:
   - Deliver report to `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m1_1_rep/handoff.md`.
   - Send a message to parent when done.
