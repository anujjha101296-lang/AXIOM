# Scope: Milestone 1 — EGS Mathematical Ontology & Database Migrations

## Architecture
- `axiom/core/knowledge_graph/schema.py`: Extend Pydantic models with `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`, and edges (`EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`).
- `axiom/core/knowledge_graph/migrations.py`: Add `_v4_mathematical_ontology` migration creating `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`.
- `axiom/core/knowledge_graph/db.py`: Support node querying and FK relationships for new tables.

## Scope Items
1. Migration `v4`: Execute DDL for `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`.
2. Schema Models: Update `NodeType`, `EdgeType`, Pydantic models, and `ScientificNode` Union.
3. Unit Tests: Test migration execution and schema validation in `tests/test_mde_ontology.py`.

## Verification Criteria
- All SQLite tables created cleanly without FK errors.
- Schema models serialize/deserialize polymorphic JSON payload correctly.
- All tests in `tests/test_mde_ontology.py` pass.
