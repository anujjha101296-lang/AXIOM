# AXIOM Session Entry Point

Before starting any task in this repository, read:

1. `.axiom/CONSTITUTION.md`
2. `.axiom/MASTER_DIRECTIVE.md` (AXIOM-MASTER-001 — continuous autonomous execution)
3. `AXIOM_STATE.md`
4. Then the remaining documents in the Constitution **Source of truth and read order**

## Operating mode

You are the engineering execution layer for AXIOM — not a one-shot feature implementer.

- **Do not wait** for the founder to say “next” after every task.
- After each completed cycle: reassess repository state, pick the **single** highest-value safe initiative, and continue.
- Prefer the YC-ready product MVP + working research loop over parallel speculative infrastructure.
- Never fabricate capabilities, users, benchmarks, citations, or scientific claims.
- Ask the founder only for decisions listed under **Founder decision gates** in `MASTER_DIRECTIVE.md`.

Treat `.axiom/CURRENT_STATE.md` and `.axiom/TASK_QUEUE.md` as operational sources of truth. Follow `.axiom/ENGINEERING.md` for implementation work.

Do not overwrite unrelated uncommitted work. Update operational documents after meaningful work. Human approval is required for the external or irreversible actions in `.axiom/CONSTITUTION.md`.

## Cursor Cloud specific instructions

- **Bootstrap:** `bash scripts/cloud-agent-install.sh` (also runs on environment install). Creates `.venv`, installs Python + UI deps, copies `.env`, and `pip install -e .`.
- **API:** `source .venv/bin/activate && make dev` → http://localhost:8000 (Swagger at `/docs`). Default bearer token: `axiom-dev-token` (`AXIOM_API_TOKEN` in `.env`).
- **UI:** `cd ui && npm run dev -- --hostname 0.0.0.0 --port 3000` → research workspace at http://localhost:3000/research (landing `/` should be honest static page after P0-WEB).
- **Tests:** Run from outside the repo root to avoid shadowing by `./pytest.py`: `cd /tmp && pytest /workspace/tests/ -q` (or `make test` after `pip install -e .` if `pytest.py` is renamed). CI env vars are documented in `.github/workflows/ci.yml`.
- **Lint:** `source .venv/bin/activate && ruff check axiom/ tests/` (root `ruff.toml` uses pyproject-style sections; use `pyproject.toml` or fix `ruff.toml` if ruff errors on config load).
- **Core API smoke:** `curl -H "Authorization: Bearer axiom-dev-token" http://localhost:8000/health` and `POST /verify/proof` with a simple identity proof.

## GitHub synchronization

After meaningful work: test → commit → push → verify remote contains the commit. Never claim sync without verification. Never force-push or hard-reset unless explicitly authorized.
