# AXIOM API Reference

Base URL: `http://localhost:8000`

Authentication: `Authorization: Bearer <token>` on all protected endpoints.

---

## Authentication

### `POST /auth/register`
Create a new researcher account. Returns a JWT access token.

```json
{"email": "you@university.edu", "password": "your-secure-password", "name": "Your Name"}
```

Response `201`:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {"id": "...", "email": "...", "name": "...", "role": "RESEARCHER"}
}
```

### `POST /auth/login`
Sign in with email and password.

```json
{"email": "you@university.edu", "password": "your-secure-password"}
```

### `GET /auth/me`
Return the authenticated user profile. Requires bearer token (JWT or static dev token).

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

All verification responses include `evidence_mode` and `formally_proven` (or `formally_verified` for compile endpoints) so simulated, heuristic, and compiler-backed outcomes are never conflated.

| `evidence_mode` | Meaning |
|---|---|
| `formal_compiler` | Subprocess prover/compiler succeeded (exit code 0) |
| `smt_finite` | Exhaustive/bounded SMT check over a finite domain |
| `heuristic` | Pattern/sanity-based check |
| `simulated` | Structural simulation when prover binary is absent |
| `unverified` | Check failed or could not run |

`formally_proven: true` is returned **only** when `evidence_mode` is `formal_compiler` and the check succeeded.

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
Response includes `evidence_mode: "smt_finite"` and `formally_proven: false` even when `is_valid: true`.

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
When the Lean compiler is unavailable, `compiler_status` contains `simulated`, `formally_proven` is `false`, and `verification_tier` is `1` (not `2`).

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
Get project detail including documents, notes, conversations, active conversation messages, and current session.

### `PUT /research/projects/{project_id}`
Update project name and/or description.
```json
{"name": "Updated title", "description": "Updated description"}
```

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
List notes for a project. Query param `tag` filters by tag.

### `DELETE /research/projects/{project_id}/notes/{note_id}`
Delete a note.

### `POST /research/projects/{project_id}/ask`
Ask a question about uploaded papers. Creates or continues a saved conversation.
```json
{
  "question": "What is the main theorem?",
  "document_id": "optional-uuid",
  "conversation_id": "optional-uuid-to-continue"
}
```
Response:
```json
{
  "answer": "...",
  "conversation_id": "uuid",
  "message_id": "uuid",
  "sources": ["paper.pdf"]
}
```

### `GET /research/projects/{project_id}/conversations`
List saved Q&A conversations for a project.

### `GET /research/projects/{project_id}/conversations/{conversation_id}`
Get a conversation with full message history. Sets it as the active conversation.

### `GET /research/search?q=...&project_id=...`
Full-text search across documents and notes. Optional `project_id` scopes to one project.

### `POST /research/projects/{project_id}/sessions/resume`
Resume or create a research session. Query param: `active_document_id` (optional).

### `GET /research/projects/{project_id}/sessions/current`
Get the current session for a project (creates one if missing).

---

## Autonomous Research Loop (Milestone 005)

Base path: `/research-loop` — all endpoints require authentication.

### `GET /research-loop/roles`
List agent role specifications.

### `GET /research-loop/benchmarks`
List historical benchmark problems (solutions hidden during execution).

### `POST /research-loop/runs`
Create a research run.

### `POST /research-loop/benchmarks/run`
Start a benchmark run against a historical problem.

### `POST /research-loop/runs/{run_id}/start`
Start execution in background.

### `GET /research-loop/runs/{run_id}`
Full inspectable research state.

### Human control
- `POST /research-loop/runs/{id}/pause|resume|cancel`
- `POST /research-loop/runs/{id}/approve`
- `POST /research-loop/runs/{id}/hypotheses/{id}/reject`
- `POST /research-loop/runs/{id}/evidence`
- `PUT /research-loop/runs/{id}/objective`

Claim statuses: `KNOWN`, `SUPPORTED`, `SPECULATIVE`, `DISPROVED`, `UNVERIFIED`, `FORMALLY_VERIFIED`.

---

## System (Admin)

### `POST /self-improve`
Trigger the self-improvement audit. Regenerates `roadmap.md`.
Response includes weakest dimension, weakest problem, and top 3 priorities.
