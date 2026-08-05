## 2026-08-05T13:18:37Z
You are Worker 1 for Milestone 1 (EGS Mathematical Ontology & Database Migrations).
Your working directory is: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_mde_m1_1
Project root: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom

Read:
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_mde_m1/SCOPE.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_mde_m1_1/handoff.md and analysis.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_mde_m1_2/handoff.md and analysis.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_mde_m1_3/handoff.md and analysis.md

Tasks:
1. Update `axiom/core/knowledge_graph/schema.py`:
   - Extend `NodeType` enum with `MATHEMATICAL_OBJECT`, `DEFINITION`, `OPEN_PROBLEM`, `CONJECTURE`.
   - Extend `EdgeType` enum with `EQUIVALENT_TO`, `DEPENDS_ON` (confirm `PROVES` is present).
   - Implement Pydantic node models: `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`.
   - Update `ScientificNode` discriminated union to include all 4 new node classes.
2. Update `axiom/core/knowledge_graph/migrations.py`:
   - Add `_v4_mathematical_ontology(conn)` migration creating tables: `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts` with proper PKs, FKs (`ON DELETE CASCADE`), indices, and safe schema handling for `memory_snapshots`.
   - Register version 4 `(4, "Mathematical ontology & memory schema", _v4_mathematical_ontology)` in `MIGRATIONS`.
3. Update `axiom/core/knowledge_graph/db.py`:
   - Update `EpistemicStore._init_db()` to invoke `run_migrations(self.conn)`.
   - Add typed query helper methods (`get_nodes_by_type`, `get_edges_by_type`, and direct table helper methods for v4 tables).
4. Create `tests/test_mde_ontology.py`:
   - Implement unit tests covering migration v4 execution, table creation, FK cascade deletion, polymorphic node serialization/deserialization, query methods, and NetworkX export.
5. Run test verification:
   - Run `pytest tests/test_mde_ontology.py -v` and `pytest tests/test_epistemic_layer.py -v` to ensure all tests pass cleanly without regression.

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write your changes and test execution results to `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_mde_m1_1/handoff.md`. Notify orchestrator via message when complete.
