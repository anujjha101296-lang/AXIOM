## 2026-08-04T21:47:27Z
You are Worker 1 for Milestone 1 (Graph Store & Ingestion: EGS & EIE).
Your working directory is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m1_1`.

You MUST read:
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_m1/SCOPE.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Tasks:
1. Knowledge Graph Store & Circular Guard (`axiom/core/knowledge_graph/`):
   - Edit `schema.py`: Define `CircularDependencyError(Exception)`, `VerificationRecord(BaseModel)`, `MCTSSearchRun(BaseModel)`.
   - Edit `db.py`:
     - Update `_init_db()` DDL to create 4 tables (`nodes`, `edges`, `verification_records`, `mcts_search_runs`) with performance indexes (`idx_nodes_type`, `idx_edges_source`, `idx_edges_target`, `idx_verif_claim`, `idx_mcts_claim`).
     - Update `add_edge(edge: Edge, check_cycles: bool = True)` to perform pre-insertion NetworkX cycle check on logical edge types (`PROVES`, `EXTENDS`, `USES_METHOD`). Raise `CircularDependencyError` if adding the edge would introduce a directed cycle. Non-logical edges (`CITES`) are exempt.
     - Implement CRUD methods: `delete_node`, `delete_edge`, `list_nodes`, `list_edges`, `add_verification_record`, `get_verification_records`, `add_mcts_search_run`, `get_mcts_search_runs`.
     - Implement `load_paper_payload(payload: IngestedPaperGraphPayload)` in `db.py` wrapped in transaction context.

2. LaTeX AST Parser & JSON Serializer (`axiom/core/parser/`):
   - Create `axiom/core/parser/latex_ast_parser.py`:
     - Implement `LatexASTParser` using `pylatexenc.latexwalker` for AST processing. Handle `\newtheorem` aliases, comment filtering (`%`), starred variants, optional headers, clean statement extraction (>95% extraction accuracy on theorem, lemma, definition, claim, proposition, corollary, proof).
     - Implement BibTeX key resolution from `.bib` files and `\thebibliography`/`\bibitem` blocks into `PaperNode` objects and `CITES`/`USES_METHOD` edges.
     - Define `IngestedPaperGraphPayload` Pydantic model with `to_json()`, `from_json()`, and `to_knowledge_graph()` methods.
   - Update `axiom/core/parser/arxiv_parser.py` and `axiom/core/parser/semantic_tracker.py` to integrate with `LatexASTParser`.

3. Test Suite Implementation & Verification (`tests/`):
   - Create `tests/test_graph_store.py`: Unit tests for schema models, table creation, CRUD, and direct/indirect cycle prevention with `CircularDependencyError`.
   - Create `tests/test_parser.py`: Unit tests for AST parser, >95% math environment extraction accuracy, BibTeX key resolution, and `IngestedPaperGraphPayload` serialization/deserialization.
   - Run tests using pytest (e.g. `pytest tests/test_graph_store.py tests/test_parser.py tests/test_epistemic_layer.py -v`). Verify 100% pass rate.

4. Documentation & Handoff:
   - Document changes in `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m1_1/changes.md`.
   - Deliver handoff report to `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m1_1/handoff.md` with build & test execution results.
   - Send a message to your parent when complete.
