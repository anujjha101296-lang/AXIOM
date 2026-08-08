# AXIOM Session Entry Point

AXIOM is a **self-improving research organization**. Do not work in "prompt → done → next" mode. Work inside the **Continuous Evolution Loop** defined in `.axiom/OPERATING_SYSTEM.md`.

Before starting any task in this repository:

1. Read `.axiom/CONSTITUTION.md`
2. Read `.axiom/OPERATING_SYSTEM.md` — master loop and seven layers
3. Read `.axiom/CURRENT_STATE.md` and `.axiom/TASK_QUEUE.md`
4. Read the relevant domain contract (`ENGINEERING.md`, `RESEARCH.md`, `PRODUCT.md`, etc.)

After completing meaningful work:

1. Run tests and benchmarks (if capability-affecting)
2. Update `CURRENT_STATE.md`, `TASK_QUEUE.md`, and `MEMORY.md` as appropriate
3. Commit focused changes and push

Treat `.axiom/CURRENT_STATE.md` and `.axiom/TASK_QUEUE.md` as the current operational source of truth. Human approval is required for the external or irreversible actions specified in `.axiom/CONSTITUTION.md`.

Do not overwrite unrelated uncommitted work.

## Cursor Cloud specific instructions

- **Bootstrap:** `bash scripts/cloud-agent-install.sh` (also runs on environment install). Creates `.venv`, installs Python + UI deps, copies `.env`, and `pip install -e .`.
- **API:** `source .venv/bin/activate && make dev` → http://localhost:8000 (Swagger at `/docs`). Default bearer token: `axiom-dev-token` (`AXIOM_API_TOKEN` in `.env`).
- **UI:** `cd ui && npm run dev -- --hostname 0.0.0.0 --port 3000` → workspace at http://localhost:3000/workspace (landing `/` may error on Next.js 16 server-component interactivity).
- **Tests:** Run from outside the repo root to avoid shadowing by `./pytest.py`: `cd /tmp && pytest /workspace/tests/ -q` (or `make test` after `pip install -e .` if `pytest.py` is renamed). CI env vars are documented in `.github/workflows/ci.yml`.
- **Lint:** `source .venv/bin/activate && ruff check axiom/ tests/` (root `ruff.toml` uses pyproject-style sections; use `pyproject.toml` or fix `ruff.toml` if ruff errors on config load).
- **Core API smoke:** `curl -H "Authorization: Bearer axiom-dev-token" http://localhost:8000/health` and `POST /verify/proof` with a simple identity proof.
