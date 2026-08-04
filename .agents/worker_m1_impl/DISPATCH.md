# DISPATCH — Worker (Milestone 1 Implementation)

## Context
Working Directory: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m1_impl
Project Root: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom

## Task Instructions
Implement Milestone 1 (Graph Store & Ingestion: EGS & EIE) components for project AXIOM according to PROJECT.md and SCOPE.md:

### Required Code Implementations:
1. `axiom/core/knowledge_graph/schema.py`:
   - Add `CircularDependencyError(Exception)`
   - Add Pydantic models `VerificationRecord` and `MCTSSearchRun`

2. `axiom/core/knowledge_graph/db.py`:
   - DDL for `verification_records` and `mcts_search_runs` tables & indexes in `_init_db()`
   - Pre-insertion cycle check in `add_edge()` using NetworkX: for logical edge types (`PROVES`, `EXTENDS`, `USES_METHOD`), if adding edge creates a directed cycle, raise `CircularDependencyError` and do not commit.
   - Add `load_paper_payload(payload)` with transaction rollback on cycle/validation error.
   - Complete CRUD methods: `delete_node`, `delete_edge`, `list_nodes`, `list_edges`, `add_verification_record`, `get_verification_records`, `add_mcts_search_run`, `get_mcts_search_runs`.

3. `axiom/core/parser/latex_ast_parser.py`:
   - Create `LatexASTParser` using `pylatexenc.latexwalker` (with regex fallback) handling comment stripping, custom `\newtheorem` aliases, math environment extraction (`theorem`, `lemma`, `definition`, etc. with >95% accuracy), and citation extraction (`\cite`, `\bibitem`).
   - Create `IngestedPaperGraphPayload` Pydantic model with `to_json()` and `to_knowledge_graph()`.

4. `axiom/core/parser/arxiv_parser.py` & `semantic_tracker.py`:
   - Integrate `LatexASTParser` into `ArxivParser` and `SemanticTracker`.

5. `tests/test_graph_store.py` & `tests/test_parser.py`:
   - Create comprehensive unit test suites covering database schema, CRUD, cycle guard prevention, LaTeX AST extraction (>95% accuracy), and JSON payload serialization.

### Verification Requirement:
You MUST run `pytest tests/test_graph_store.py tests/test_parser.py tests/test_epistemic_layer.py -v` (or via `python3 -m pytest`) and confirm all tests pass cleanly.

### Mandatory Integrity Warning:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
