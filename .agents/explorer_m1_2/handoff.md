# Handoff Report — Explorer 2 (Milestone 1: Graph Store & Ingestion)

**Agent**: Explorer 2 (`explorer_m1_2`)  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_2`  
**Date**: 2026-08-04  

---

## 1. Observation

1. **Existing Parser Code**:
   - In `axiom/core/parser/arxiv_parser.py:107-110`:
     ```python
     env_pattern = re.compile(
         r"\\begin\{(theorem|lemma|definition|conjecture|proposition|corollary)\}(.*?)\\end\{\1\}",
         re.DOTALL
     )
     ```
   - In `axiom/core/parser/arxiv_parser.py:179`:
     ```python
     cite_pattern = re.compile(r"\\cite(?:[a-z]*)?\{([^}]+)\}")
     ```
   - In `axiom/core/parser/semantic_tracker.py:33-37`:
     ```python
     combined_pattern = re.compile(
         r"\\begin\{(theorem|lemma|proposition|corollary)\}(.*?)\\end\{\1\}(.*?)\\begin\{proof\}(.*?)\\end\{proof\}",
         re.DOTALL
     )
     ```
2. **Dependencies**:
   - `pyproject.toml:14`: `pylatexenc = "^2.10"` is declared in `[tool.poetry.dependencies]`.
   - `pyproject.toml:11`: `pydantic = "^2.5.0"` is declared.
3. **Schema & Database Interface**:
   - `axiom/core/knowledge_graph/schema.py`: Defines `PaperNode`, `MathematicalClaimNode`, `ConceptNode`, `Edge`, `KnowledgeGraph`.
   - `axiom/core/knowledge_graph/db.py:190-195`: Implements `load_knowledge_graph(self, kg: KnowledgeGraph)`.
4. **Missing Modules & Missing Artifacts**:
   - `axiom/core/parser/latex_ast_parser.py` does not yet exist.
   - `IngestedPaperGraphPayload` schema model is not yet implemented.
   - No test file `tests/test_parser.py` exists yet (only `tests/test_epistemic_layer.py` and `tests/test_api.py`).

---

## 2. Logic Chain

1. **Observation 1 & 4**: The current implementation in `arxiv_parser.py` relies on naive regex. It cannot handle custom theorem aliases (`\newtheorem{thm}{Theorem}`), commented LaTeX lines (`% \begin{theorem}`), nested environment blocks, optional environment headers (`\begin{theorem}[Header]`), or structured BibTeX databases (`.bib` or `\bibitem`).
2. **Observation 2**: `pylatexenc` is already included as a project dependency in `pyproject.toml`. Its `pylatexenc.latexwalker.LatexWalker` module converts LaTeX text into a full AST node tree (`LatexEnvironmentNode`, `LatexMacroNode`, `LatexMathNode`, `LatexCommentNode`), enabling clean, comment-aware parsing.
3. **Observation 3 & 4**: To satisfy Requirement R1 / Feature 4 ("Epistemic JSON Graph Serializer"), we must create `axiom/core/parser/latex_ast_parser.py` containing the 4-pass `LatexASTParser` and the `IngestedPaperGraphPayload` Pydantic model.
4. **Conclusion**: Implementing `LatexASTParser` using `pylatexenc` with `\newtheorem` alias discovery, comment filtering, BibTeX resolution, and `IngestedPaperGraphPayload` serialization will achieve >95% math environment extraction accuracy and deliver the required JSON graph payload format.

---

## 3. Caveats

- **Malformed LaTeX**: Some arXiv source files may contain severe unclosed LaTeX syntax errors. `pylatexenc.latexwalker` tolerates most formatting quirks, but fallback regex/error recovery logic should be included for extreme edge cases.
- **External BibTeX Files**: Some papers separate citations into `.bib` files while others use inline `\begin{thebibliography}` blocks. The parser must support both sources seamlessly.

---

## 4. Conclusion

The analysis and technical specification for Milestone 1 Feature 3 (LaTeX AST Math & Citation Ingestion) and Feature 4 (Epistemic JSON Graph Serializer) are complete.
We recommend creating `axiom/core/parser/latex_ast_parser.py` with `LatexASTParser` and `IngestedPaperGraphPayload`, updating `arxiv_parser.py` and `semantic_tracker.py`, and adding `tests/test_parser.py` to achieve >95% extraction accuracy and 100% test coverage.

Detailed architectural specifications and proposed patch blueprints are available in:
`/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m1_2/analysis.md`

---

## 5. Verification Method

To verify the proposed implementation once written by the Worker:

1. **Run Parser Unit & Integration Tests**:
   ```bash
   pytest tests/test_parser.py tests/test_epistemic_layer.py -v
   ```
2. **Inspect Files**:
   - `axiom/core/parser/latex_ast_parser.py`
   - `axiom/core/parser/arxiv_parser.py`
   - `axiom/core/parser/semantic_tracker.py`
   - `tests/test_parser.py`
3. **Invalidation Conditions**:
   - Extraction accuracy for math environments falls below 95% on test papers.
   - Commented LaTeX blocks (`% \begin{theorem}`) generate false positive nodes.
   - `\newtheorem` aliases are missed.
   - `IngestedPaperGraphPayload.to_json()` fails schema validation or cannot be converted to `KnowledgeGraph`.
