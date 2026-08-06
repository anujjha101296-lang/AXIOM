# AXIOM API Reference

Base URL: `http://localhost:8000`

Authentication: `Authorization: Bearer <token>` on all protected endpoints.

---

## System

### `GET /health`
Liveness check. No auth required.
```json
{"status": "healthy", "version": "0.2.0", "timestamp": 1722800000.0}
```

### `GET /ready`
Readiness check — verifies database connectivity. No auth required.
```json
{"status": "ready", "database": "connected", "version": "0.2.0"}
```

### `GET /metrics`
Prometheus text-format metrics. No auth required.

### `GET /events`
Recent in-process event bus history.
- Query params: `topic` (optional filter), `limit` (default 20)

---

## Knowledge Graph

### `GET /graph`
Export the full epistemic graph as JSON.
```json
{"nodes": [...], "edges": [...]}
```

---

## Discovery

### `POST /ingest`
Ingest a paper from arXiv by ID.
```json
{"arxiv_id": "2312.00123"}
```
Response:
```json
{
  "status": "triggered",
  "arxiv_id": "2312.00123",
  "title": "...",
  "claims_extracted": 5,
  "concepts_extracted": 3,
  "edges_created": 8
}
```

### `POST /query`
Run a discovery query against the knowledge graph.
```json
{"query_string": "Riemann hypothesis zero distribution"}
```

### `POST /hypothesize`
Generate new mathematical conjectures from EGS verified claims.
```json
{"max_hypotheses": 5}
```
Response:
```json
{
  "status": "success",
  "hypotheses_generated": 5,
  "nodes": [{"id": "...", "name": "...", "statement": "...", "strategy": "DUAL"}]
}
```

---

## Verification

### `POST /verify/conjecture`
Run a Z3 SMT counterexample sweep on a modular arithmetic conjecture.
```json
{
  "conjecture_name": "Goldbach-like",
  "equation": "x + y == z",
  "modulus": 7,
  "variables": ["x", "y", "z"]
}
```

### `POST /verify/proof`
Run MCTS proof search and export Lean 4 file.
```json
{
  "theorem_name": "identity_add",
  "start_expression": "x + 0",
  "target_expression": "x",
  "variables": {"x": "Nat"}
}
```

---

## Memory

### `GET /memory/context`
Return the current session working memory snapshot.

### `POST /memory/reset`
Clear the working memory and begin a new research session.

### `POST /memory/problem`
Set the active research problem.
```json
{"problem": "Investigate zeros of the Riemann zeta function"}
```

---

## Benchmarks

### `GET /benchmark/prize-readiness`
Return AXIOM's current capability scores against Millennium Prize Problems.

---

## Research Workspace

Base path: `/research` — all endpoints require authentication.

### `POST /research/projects`
Create a research project.
```json
{"name": "RH Literature Review", "description": "Survey of zeta zero results"}
```

### `GET /research/projects`
List all projects (most recently active first).

### `GET /research/projects/{project_id}`
Get project detail including documents, notes, and current session.

### `POST /research/projects/{project_id}/documents/upload`
Upload a PDF (`multipart/form-data`, field `file`). Extracts text automatically.

### `POST /research/projects/{project_id}/documents/{document_id}/summarize`
Generate an LLM summary (or extractive fallback) for an uploaded document.

### `GET /research/projects/{project_id}/documents`
List documents in a project.

### `POST /research/projects/{project_id}/notes`
Create a structured note.
```json
{"title": "Key insight", "body": "...", "document_id": "optional-uuid", "tags": ["zeta"]}
```

### `PUT /research/projects/{project_id}/notes/{note_id}`
Update a note (`title`, `body`, `tags` — all optional).

### `GET /research/projects/{project_id}/notes`
List notes for a project.

### `GET /research/search?q=...&project_id=...`
Full-text search across documents and notes. Optional `project_id` scopes to one project.

### `POST /research/projects/{project_id}/sessions/resume`
Resume or create a research session. Query param: `active_document_id` (optional).

### `GET /research/projects/{project_id}/sessions/current`
Get the current session for a project (creates one if missing).

---

## System (Admin)

### `POST /self-improve`
Trigger the self-improvement audit. Regenerates `roadmap.md`.
Response includes weakest dimension, weakest problem, and top 3 priorities.
