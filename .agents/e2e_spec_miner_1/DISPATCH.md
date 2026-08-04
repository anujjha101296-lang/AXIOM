## 2026-08-04T16:15:56Z
You are the E2E Spec Miner for AXIOM.
Your working directory is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/e2e_spec_miner_1`.

Mandatory input documents to read:
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`
- `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md`

Your objective:
1. Mine specifications, module entrypoints, public functions/classes, API routes, and interface contracts across the AXIOM codebase (`axiom/`, `ui/`, `tests/`).
2. Examine the existing tests (`tests/test_api.py`, `tests/test_epistemic_layer.py`) and identify test invocation runners (`pytest`, python test runners, package setups).
3. Document how to invoke each feature programmatically or via CLI/HTTP/pytest, including schema models, parameters, expected return formats, and error conditions for all 11 features:
   - Feature 1: SQLite Graph Relational Storage & Schema
   - Feature 2: Circular Dependency Guard
   - Feature 3: LaTeX AST Math & Citation Ingestion
   - Feature 4: Epistemic JSON Graph Serializer
   - Feature 5: LaTeX-to-Lean 4 AST Exporter
   - Feature 6: SMT / Z3 Counterexample Gateway
   - Feature 7: Lean 4 Compiler Proof Checker
   - Feature 8: MCTS Proof Search Engine
   - Feature 9: Autonomous Discovery Loop
   - Feature 10: Spatial Canvas Next.js Frontend
   - Feature 11: FastAPI Graph & Proof API Gateway

Write your findings to `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/e2e_spec_miner_1/spec_report.md` and deliver `handoff.md`.
Send a completion message to parent (`da4a89d5-3d9a-4f99-bf9a-afbbba7214b7`) when finished.
