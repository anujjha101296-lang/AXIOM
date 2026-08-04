# Handoff Report — Explorer 2: Functional Requirements Breakdown & Module Mapping

**Agent**: Explorer 2 (Survey Phase)  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/teamwork_preview_explorer_survey_2`  
**Target Handoff File**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/teamwork_preview_explorer_survey_2/handoff.md`  
**Parent Agent**: `da4a89d5-3d9a-4f99-bf9a-afbbba7214b7`

---

## 1. Observation

### Source Requirements
From `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`:
- **System Description**: "A continuously improving AI Scientific Discovery Platform (AXIOM) capable of parsing mathematical papers, exporting proof templates, executing SMT checks, running MCTS proof searches, and displaying results in an interactive Next.js dashboard." (lines 6-7)
- **Integrity Mode**: `development` (line 9)
- **Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom` (line 8)

### Requirements & Acceptance Criteria Map
- **R1. Epistemic Ingest & Parser (EIE)**: Ingest LaTeX archives from arXiv, parsing theorem statements, lemmas, definitions, and bibliographic citations into a structured JSON graph format.
  - *Criteria*: Parse LaTeX source documents correctly, extracting >95% of math environments and citation keys.
- **R2. Logical Reasoning & Proof Exporter (LRK)**: Automatically translate parsed LaTeX theorem/lemma statements and concept definitions into compilable Lean 4 theorem declarations.
  - *Criteria*: Translate extracted claims into Lean 4 format, compiling declarations with 0 syntax errors.
- **R3. Verification & SMT Gateway (AVT)**: Integrate with Z3/SMT solvers to run parameter sweeps seeking counterexamples for conjectures, and local Lean 4 compilers to check proof script correctness.
  - *Criteria*: (1) Identify and flag counterexamples for invalid parameter boundaries inside claims within 60 seconds; (2) Ensure that only proofs that compile successfully in the Lean 4 compiler are designated as verified.
- **R4. Graph Store & Storage (EGS)**: SQLite-backed database service storing entities and logical dependency edges with circular reference checks.
- **R5. Autonomous Discovery Loop & MCTS Proof Search (DRSP)**: Implement Monte Carlo Tree Search (MCTS) to explore Lean proof tactics and run continuous loop cycles managing candidate evaluations.
  - *Criteria*: Run MCTS proof searches to compile valid proofs for simple algebra lemmas.
- **R6. Spatial Canvas Dashboard (UI)**: Build a Next.js/React frontend application displaying the scientific knowledge graph, nodes, citation lineages, and verification statuses on an interactive spatial canvas.
  - *Criteria*: Launch a Next.js frontend showing an interactive node-link representation of the SQLite knowledge graph.

### Existing Codebase Inspection
- `pyproject.toml` currently defines:
  - Python dependencies: `pydantic ^2.5.0`, `networkx ^3.0`, `sympy ^1.12`, `pylatexenc ^2.10`, `requests ^2.31.0`, `fastapi ^0.100.0`, `uvicorn ^0.22.0`, `pydantic-settings ^2.0.0`.
  - Dev dependencies: `pytest ^7.4.0`.
- Existing package structure: `axiom/core/knowledge_graph`, `axiom/core/parser`, `axiom/services/api_gateway`, `axiom/services/model_gateway`.

---

## 2. Logic Chain

From the high-level original requirements and existing project scaffolding, we deduce the required module boundaries, concrete sub-components, data structures, external packages, API specifications, and acceptance criteria for each requirement R1 through R6.

### R1. Epistemic Ingest & Parser (EIE)
- **Module Boundary**: `axiom.core.parser` / `axiom.services.ingest`
- **Sub-components**:
  1. `ArxivFetcher`: Fetches paper source archives (`.tar.gz` / `.tex`) via arXiv ID or API, unpacks and expands LaTeX inclusion trees (`\input`, `\include`).
  2. `LatexParser`: Leverages `pylatexenc` / AST parser to tokenize LaTeX and isolate math environments (`theorem`, `lemma`, `definition`, `proposition`, `corollary`, `equation`, `align`, inline/display math).
  3. `CitationExtractor`: Extracts BibTeX references (`\cite{...}`, `\bibitem`) and `.bib` metadata using `bibtexparser`.
  4. `GraphJsonSerializer`: Transforms parsed AST entities and citation relationships into a standardized Pydantic `EpistemicGraphSchema` JSON object.
- **Required Packages & APIs**:
  - `pylatexenc`, `bibtexparser`, `requests`/`httpx`, `pydantic`.
- **Verifiable Acceptance Criteria**:
  - `test_ingest_latex_extraction`: Given sample LaTeX document with $N$ math environments and $M$ citation keys, extract $\ge 0.95 \times (N + M)$ entities accurately.
  - Validated JSON structure adhering to `Node` and `Edge` schemas.

### R2. Logical Reasoning & Proof Exporter (LRK)
- **Module Boundary**: `axiom.core.exporter` / `axiom.services.lean_exporter`
- **Sub-components**:
  1. `LatexToFormalAST`: Converts LaTeX math AST expressions into formal symbolic expressions (e.g. mapping $\forall x \in \mathbb{R}$ to Lean type signature `(x : Real)`).
  2. `Lean4CodeGenerator`: Formats formal expressions into complete, syntactically clean Lean 4 module code (`import Mathlib`, `def`, `theorem <name> ... := by sorry`).
  3. `LeanProjectManager`: Manages Lean workspace environment (`lakefile.lean`, `lean-toolchain`).
- **Required Packages & APIs**:
  - `sympy`, `pydantic`, Lean 4 CLI toolchain (`lake`, `lean`).
- **Verifiable Acceptance Criteria**:
  - `test_lean_export_syntax`: Translate parsed claims into `.lean` files and execute `lean --check` or `lake build`, producing 0 syntax/parsing errors.

### R3. Verification & SMT Gateway (AVT)
- **Module Boundary**: `axiom.core.verification` / `axiom.services.smt_gateway`
- **Sub-components**:
  1. `Z3Gateway`: Translates conjectures into SMT-LIB2 formulas or direct Python `z3` solver objects. Performs parameter sweeps over variable bounds to detect counterexamples.
  2. `LeanCompilerChecker`: Executes `lean` subprocess with proof scripts, parses output diagnostics, verifies absence of `sorry` tactics and type errors.
  3. `VerificationOrchestrator`: Updates node state to `VERIFIED`, `COUNTEREXAMPLE_FOUND`, or `FAILED`.
- **Required Packages & APIs**:
  - `z3-solver`, `asyncio`/`subprocess` for CLI runner, `pydantic`.
- **Verifiable Acceptance Criteria**:
  - `test_z3_counterexample_detection`: Detect counterexample for invalid claim (e.g., $\forall x \in \mathbb{R}, x^2 - 4 > 0$) within $<60$ seconds, returning specific bound violation (e.g. $x=0$).
  - `test_lean_verification`: Ensure status `VERIFIED` is granted ONLY if Lean 4 compiler exits with code 0 and 0 errors.

### R4. Graph Store & Storage (EGS)
- **Module Boundary**: `axiom.core.knowledge_graph` / `axiom.services.graph_store`
- **Sub-components**:
  1. `SqliteDatabase`: SQLite database manager managing `nodes` and `edges` tables with index optimizations.
  2. `CircularDependencyGuard`: Uses `networkx` directed graph algorithms to detect and reject edges that create cycles in logical dependency trees.
  3. `GraphQueryAPI`: Provides topological sorting, lineage tree traversal, and sub-graph filter queries.
- **Required Packages & APIs**:
  - `sqlite3` (or `aiosqlite`), `networkx`, `pydantic`.
- **Verifiable Acceptance Criteria**:
  - `test_cycle_prevention`: Attempting to insert an edge $(B \to A)$ when path $(A \to B)$ exists raises `CircularDependencyError` and aborts transaction.

### R5. Autonomous Discovery Loop & MCTS Proof Search (DRSP)
- **Module Boundary**: `axiom.core.discovery` / `axiom.services.mcts_search`
- **Sub-components**:
  1. `MCTSNode`: Represents proof state (remaining goals, tactic path, visit count $N$, score $Q$).
  2. `MCTSProofSearchEngine`: Implements UCT selection, tactic expansion (`rfl`, `simp`, `ring`, `linarith`, `rw`), simulation/rollout, and backpropagation.
  3. `AutonomousDiscoveryLoop`: Continuous background runner selecting unproved lemmas, running MCTS search, and registering discovered proofs.
- **Required Packages & APIs**:
  - `math`, `random`, integration with Lean compiler service (R3).
- **Verifiable Acceptance Criteria**:
  - `test_mcts_algebra_proof`: Run MCTS to automatically generate valid Lean 4 tactic proof for simple algebra lemma (e.g., $a + b = b + a$) that successfully compiles without `sorry`.

### R6. Spatial Canvas Dashboard (UI)
- **Module Boundary**: `ui/` (Next.js App)
- **Sub-components**:
  1. `SpatialCanvas`: Interactive React Flow (`@xyflow/react`) or 2D canvas component rendering nodes and citation lineage edges with zooming/panning.
  2. `NodeInspector`: Panel displaying LaTeX math rendering (KaTeX), Lean 4 source code, Z3 counterexamples, and lineage trees.
  3. `BackendAPIClient`: Next.js REST API routes / fetchers connecting UI to Python FastAPI backend services.
- **Required Packages & APIs**:
  - Next.js 14+ (App Router), React 18+, TypeScript, `@xyflow/react`, `katex`, `tailwindcss`.
- **Verifiable Acceptance Criteria**:
  - `test_ui_canvas_render`: Launch Next.js application, fetch graph nodes from backend, and render interactive spatial node-link graph canvas.

---

## 3. Caveats

- **Lean 4 Compiler Availability**: Local verification (R2, R3, R5) requires the Lean 4 executable (`lean` / `lake`). In environments where Lean 4 binary is not installed, mock subprocess wrappers or fallback syntax checkers must be provided for unit testing.
- **Network Boundaries for arXiv**: Remote arXiv fetching (R1) relies on external HTTP requests. Tests should include local mock `.tex` archive fixtures to operate offline reliably.
- **SMT Translator Scope**: Full LaTeX-to-Z3 translation for arbitrary higher-order math is undecidable; SMT solver parameter sweeps are bounded to first-order real/integer polynomial and predicate domains.

---

## 4. Conclusion

The AXIOM platform architecture cleanly segregates into 6 modular Python/TypeScript services matching requirements R1-R6:
- `axiom/core/parser` (R1 - Epistemic Ingest)
- `axiom/core/exporter` (R2 - Lean Exporter)
- `axiom/core/verification` (R3 - SMT/Z3 & Lean Gateway)
- `axiom/core/knowledge_graph` (R4 - SQLite Graph Store & Cycle Guard)
- `axiom/core/discovery` (R5 - MCTS Proof Search Engine & Autonomous Loop)
- `ui/` (R6 - Next.js Spatial Canvas Dashboard)

All 6 requirements have concrete sub-component specifications, package dependencies, and explicit testable acceptance criteria.

---

## 5. Verification Method

To verify this survey report and its downstream implementation:
1. **Directory Structure Verification**: Ensure modules correspond to `axiom/core/parser`, `exporter`, `verification`, `knowledge_graph`, `discovery`, and `ui/`.
2. **Python Test Suite Execution**:
   - `poetry run pytest tests/`
   - Run unit tests for R1 (`test_parser`), R2 (`test_exporter`), R3 (`test_smt_lean`), R4 (`test_graph_store`), R5 (`test_mcts`).
3. **Z3 Solver & Lean 4 Check**:
   - Verify `python -c "import z3; print(z3.__version__)"`
   - Verify `lean --version` or mock runner fallback.
4. **UI Build Verification**:
   - `cd ui && npm run build` or `npm run dev` to verify Next.js spatial canvas dashboard compilation.
