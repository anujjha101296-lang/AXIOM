# Scope: Milestone 1 — Graph Store & Ingestion (EGS & EIE)

## Architecture
Milestone 1 covers the core data storage and document parsing capabilities:
- `axiom/core/knowledge_graph`: SQLite Relational Store, NetworkX cycle detection DAG guard, Pydantic node/edge schema models (EGS).
- `axiom/core/parser`: LaTeX AST parser, math environment extraction (>95%), BibTeX citation resolution, epistemic JSON graph serializer (EIE).

## Feature Inventory (M1 Scope)
| # | Feature | Description | Target Code Paths | Status |
|---|---------|-------------|-------------------|--------|
| 1 | SQLite Graph Relational Storage & Schema | Relational SQLite database (`nodes`, `edges`, `verification_records`), indexes, CRUD operations | `axiom/core/knowledge_graph/db.py`, `schema.py` | PLANNED |
| 2 | Circular Dependency Guard | NetworkX DAG validation preventing cycles in logical edges (`PROVES`, `EXTENDS`, `USES_METHOD`) | `axiom/core/knowledge_graph/db.py` | PLANNED |
| 3 | LaTeX AST Math & Citation Ingestion | LaTeX AST parser extracting math environments (`theorem`, `lemma`, etc.) and citation keys | `axiom/core/parser/latex_ast_parser.py`, `arxiv_parser.py`, `semantic_tracker.py` | PLANNED |
| 4 | Epistemic JSON Graph Serializer | Transform parsed papers into structured epistemic node-edge JSON payload (`IngestedPaperGraphPayload`) | `axiom/core/parser/semantic_tracker.py` | PLANNED |

## Code Layout
- `axiom/core/knowledge_graph/db.py`
- `axiom/core/knowledge_graph/schema.py`
- `axiom/core/parser/latex_ast_parser.py`
- `axiom/core/parser/arxiv_parser.py`
- `axiom/core/parser/semantic_tracker.py`
- `tests/test_graph_store.py`
- `tests/test_parser.py`
