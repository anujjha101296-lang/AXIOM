# Milestone 1 Handoff Report: Test Architecture, Ingestion Integration & Edge Case Analysis

**Author**: Explorer 3 (Milestone 1 — Graph Store & Ingestion: EGS & EIE)  
**Target Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_3`  
**Date**: 2026-08-04  

---

## 1. Observation

Direct observations from inspecting `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`:

1. **Missing Test Files**:
   - `SCOPE.md` specifies unit test suites `tests/test_graph_store.py` and `tests/test_parser.py`.
   - Inspection of `tests/` directory revealed only `tests/test_api.py` and `tests/test_epistemic_layer.py`. `test_graph_store.py` and `test_parser.py` do **not** exist in the repository.

2. **Database Cycle Guard Defect**:
   - `axiom/core/knowledge_graph/db.py` (lines 72-94): `EpistemicStore.add_edge()` currently performs foreign key checks and SQL upsert, but does **not** validate DAG acyclicity prior to edge insertion.
   - `SemanticTracker.detect_circular_dependencies()` in `axiom/core/parser/semantic_tracker.py` (lines 71-91) computes cycles post-hoc, but does not block transaction commits or raise `CircularDependencyError`.
   - `axiom/core/knowledge_graph/schema.py` does not currently define the `CircularDependencyError` exception class.

3. **Ingestion Integration Gap**:
   - `EpistemicStore.load_knowledge_graph()` in `db.py` (lines 190-195) iterates through nodes and edges without explicit `BEGIN TRANSACTION ... ROLLBACK` error handling for paper payload loading.

4. **Environment Execution Observation**:
   - `poetry run pytest` returned `zsh: command not found: poetry`.
   - `python3 -m pytest` returned `No module named pytest` (system python lacks pytest). Running test verification requires virtualenv creation (`python3 -m venv .venv`).

---

## 2. Logic Chain

1. **From Observation 1 (Missing Test Files)** -> `tests/test_graph_store.py` and `tests/test_parser.py` must be authored from scratch during Worker implementation. Detailed specifications with 15 test cases (8 for graph store, 7 for parser) have been formulated in `analysis.md`.
2. **From Observation 2 (Missing Cycle Guard)** -> To satisfy Feature 2 ("inserting cyclic logical edges raises `CircularDependencyError` and aborts transaction"), `CircularDependencyError` must be added to `schema.py`. `EpistemicStore.add_edge()` must build a directed graph of logical edges (`PROVES`, `EXTENDS`, `USES_METHOD`) using NetworkX, check DAG acyclicity before executing SQL `INSERT`, and raise `CircularDependencyError` if a cycle is detected. Non-logical edges (`CITES`) are exempt from cycle enforcement.
3. **From Observation 3 (Ingestion Integration Gap)** -> To safely ingest `IngestedPaperGraphPayload` into SQLite, `EpistemicStore` must provide `load_paper_payload(payload)`. This method must execute inside an explicit SQLite transaction block (`with self.conn:` or `BEGIN TRANSACTION`). If `add_edge()` raises `CircularDependencyError` or `ValueError` for any edge in the payload, the transaction automatically rolls back, keeping the database in a consistent state.
4. **From Observation 4 (Environment Setup)** -> Future worker/reviewer verification must execute pytest using `.venv` or direct python binary after dependency installation.

---

## 3. Caveats

- **Network Access**: Verification of arXiv PDF/LaTeX tarball download via live HTTP (`ArxivParser.download_source`) depends on external network connectivity. Offline unit tests should use mock TeX strings (`parse_tex_content`).
- **LaTeX AST Engine**: `pylatexenc.latexwalker` tolerates minor LaTeX syntax errors, but extremely malformed files with unbalanced raw macro braces may produce partial AST branches. The parser must wrap AST node iteration in safe exception guards.
- **SQLite Concurrency**: SQLite in-memory databases (`:memory:`) are connection-isolated. Disk-based testing should use temporary file paths (`tempfile.NamedTemporaryFile`).

---

## 4. Conclusion

Milestone 1's architecture is sound, but requires three concrete code additions to achieve compliance with `SCOPE.md` and `PROJECT.md`:
1. Add `CircularDependencyError` and pre-insertion cycle check in `EpistemicStore.add_edge()` with transaction rollback support in `load_paper_payload()`.
2. Create `axiom/core/parser/latex_ast_parser.py` containing `LatexASTParser` (4-pass AST processing) and `IngestedPaperGraphPayload`.
3. Create unit test suites `tests/test_graph_store.py` (8 test specs) and `tests/test_parser.py` (7 test specs, including >95% extraction accuracy benchmark).

---

## 5. Verification Method

To independently verify the implementation once completed by the Worker agent:

1. **Files to Inspect**:
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/knowledge_graph/schema.py` (verify `CircularDependencyError` definition)
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/knowledge_graph/db.py` (verify pre-insertion cycle check in `add_edge` and transaction rollback in `load_paper_payload`)
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/axiom/core/parser/latex_ast_parser.py` (verify `LatexASTParser` and `IngestedPaperGraphPayload`)
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/tests/test_graph_store.py` (verify graph store & cycle guard unit tests)
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/tests/test_parser.py` (verify parser & payload unit tests)

2. **Execution Commands**:
   ```bash
   cd /Users/itachiuchiha/.gemini/antigravity/scratch/axiom
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e . pytest
   pytest tests/test_graph_store.py tests/test_parser.py tests/test_epistemic_layer.py -v
   ```

3. **Pass Criteria**:
   - All tests in `test_graph_store.py`, `test_parser.py`, and `test_epistemic_layer.py` pass with 0 errors.
   - Inserting a cyclic logical edge raises `CircularDependencyError` and aborts transaction.
   - Math environment extraction accuracy benchmark achieves >= 95%.
