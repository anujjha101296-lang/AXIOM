## 2026-08-05T13:17:10Z
Task:
Read:
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_mde_m1/SCOPE.md

Your scope is Milestone 1: EGS Mathematical Ontology & Database Migrations (R1 & R8-Schema).
Scope items:
1. Write migration `v4_mathematical_ontology` in `axiom/core/knowledge_graph/migrations.py` creating tables: `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`.
2. Update Pydantic schema models in `axiom/core/knowledge_graph/schema.py` (`MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`, `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES` edges, and `ScientificNode` Union).
3. Ensure `EpistemicStore` in `axiom/core/knowledge_graph/db.py` handles querying and FK operations for new tables.
4. Write unit tests in `tests/test_mde_ontology.py` and run verification.

Follow the iteration loop: Explorer -> Worker -> Reviewer -> Challenger -> Auditor -> Gate check.
Once verified and complete, update your status and send a completion message to parent.
