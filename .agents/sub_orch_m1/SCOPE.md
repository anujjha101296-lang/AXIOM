# Scope: Milestone 1 — Graph Store & Ingestion (EGS & EIE)

## Original User Request
Path: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`

## Project Root
Path: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`

## Project Master Plan
Path: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md`

## Objectives & Scope
Implement Milestone 1 covering:
1. **Feature 1: SQLite Graph Relational Storage & Schema**: Relational SQLite database (`nodes`, `edges`, `verification_records`, `mcts_search_runs`), performance indexes, Pydantic node/edge schema models.
2. **Feature 2: Circular Dependency Guard**: NetworkX DAG validation preventing cyclic edges (`PROVES`, `EXTENDS`, `USES_METHOD`).
3. **Feature 3: LaTeX AST Math & Citation Ingestion**: LaTeX AST parser extracting >95% math environments (`theorem`, `lemma`, etc.) and citation keys.
4. **Feature 4: Epistemic JSON Graph Serializer**: Transform parsed papers into structured epistemic node-edge JSON payload (`IngestedPaperGraphPayload`).

## Verification & Acceptance Criteria
- Parse LaTeX source documents correctly, extracting >95% of math environments and citation keys.
- Cycle prevention: inserting cyclic logical edges raises `CircularDependencyError` and aborts transaction.
- Unit tests pass for `test_parser.py` and `test_graph_store.py`.

## Execution Protocol
Follow the Explorer -> Worker -> Reviewer -> Challenger -> Auditor iteration loop until gate passes.
- Explorer analyzes implementation approach and files.
- Worker writes code in `axiom/core/knowledge_graph/` and `axiom/core/parser/`, runs tests.
- Reviewer checks code quality, correctness, and adherence to contracts.
- Challenger runs stress tests and edge cases.
- Auditor checks code integrity (NO CHEATING / hardcoding).
