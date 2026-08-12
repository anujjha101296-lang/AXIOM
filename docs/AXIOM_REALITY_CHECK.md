# AXIOM Reality Check

**CURRENT GIT COMMIT**: `3431a657925a6bf0d6f7f97178f7ed883b1c58f9`
**CURRENT BRANCH**: `main`

## PROJECT ARCHITECTURE
AXIOM is structured as a full-stack AI Scientific Discovery Platform. It comprises:
- **Frontend**: A Next.js application located in the `ui/` directory.
- **Backend API**: A FastAPI application in `axiom/` providing endpoints for the Mathematical Intelligence Platform (MIP), Scientific Capability Evaluation, Mathematical Discovery Engine (MDE), and Research Workspace.
- **Data Storage**: SQLite (`axiom.db`) based knowledge graph (`EpistemicStore`) and Working Memory.
- **Tooling**: Integrations for SMT solvers (Z3), Lean 4 exporter, and arXiv parsing.
- **Deployment**: Dockerized with `docker-compose.yml` supporting the API, UI, Prometheus, and Grafana.

---

## SUBSYSTEM CLASSIFICATION

1. **Frontend**: `SCAFFOLD_ONLY` / `PARTIALLY_IMPLEMENTED` (Next.js setup exists, but fails to build due to environment errors).
2. **Backend**: `SCAFFOLD_ONLY` (FastAPI routes exist, but underlying logic is largely mocked).
3. **Database**: `SCAFFOLD_ONLY` (SQLite connection exists, but migrations have `pass`).
4. **Authentication**: `PARTIALLY_IMPLEMENTED` (JWT token verification exists in `api_gateway/auth.py`).
5. **API routes**: `PARTIALLY_IMPLEMENTED` (Endpoints defined in `main.py`).
6. **AI/LLM integrations**: `MOCKED` (OpenAI client exists, but uses "mock-model" stubs across QA and summarizer).
7. **Agent systems**: `MOCKED` (Workflow reviewers and reporters are hardcoded stubs).
8. **Research workspace**: `MOCKED` (`research/store.py` has `pass`).
9. **Document upload/parsing**: `MOCKED` (`ArxivParser` has `pass`).
10. **Retrieval/RAG**: `MOCKED` (`engine.py` has basic regex alpha conversion, but core logic is `pass`).
11. **Memory**: `MOCKED` (`working_memory.py` / `episodic.py` largely empty/stubbed).
12. **Knowledge graph**: `MOCKED` (`store.py` and `migrations.py` are full of `pass`).
13. **Evidence/citation systems**: `NOT_IMPLEMENTED`.
14. **Benchmark systems**: `MOCKED` (`PrizeReadinessScorer` exists but appears stubbed).
15. **Research autonomy**: `MOCKED` (`self_improvement.py` is minimal/stubbed).
16. **Open problem research components**: `MOCKED` (`mip/conjecture/generator.py` has `pass`).
17. **Docker**: `VERIFIED_WORKING` (Configured, but cannot run locally due to missing Docker).
18. **Kubernetes**: `NOT_IMPLEMENTED`.
19. **CI/CD**: `VERIFIED_WORKING` (`.github/workflows` exists).
20. **Tests**: `SCAFFOLD_ONLY` (Tests exist in `tests/`, but fail to run due to missing environment tools).
21. **Security configuration**: `PARTIALLY_IMPLEMENTED` (CORS and JWT present).
22. **Environment variables**: `VERIFIED_WORKING` (`.env.example` is complete).
23. **Deployment configuration**: `VERIFIED_WORKING` (Prometheus/Grafana configs present).
24. **Mocked or placeholder functionality**: **HEAVILY PRESENT** (Extensive use of `pass`, `mock-model`, dummy algorithms).

---

## EXECUTION FAILURES & DEPENDENCY ISSUES

### 1. Backend Build & Test Failure
- **Exact Error**: `zsh:1: command not found: poetry` and `ModuleNotFoundError: No module named 'encodings'` when using `python3 -m venv`.
- **Root Cause**: Poetry is not installed on the system. Furthermore, the local Python installation is corrupted or missing its standard library (`encodings`).
- **Affected Files**: Backend testing workflow (`tests/`).
- **Recommended Fix**: Fix the host machine's Python installation and install `poetry` globally. Alternatively, use Docker.

### 2. Frontend Build Failure
- **Exact Error**: `npm error Exit handler never called!`
- **Root Cause**: Node/NPM environment instability on the host machine or sandbox constraint.
- **Affected Files**: `ui/package.json`
- **Recommended Fix**: Reinstall/Update Node.js on the host, or run the build inside a containerized Docker environment.

### 3. Docker Execution Failure
- **Exact Error**: `zsh:1: command not found: docker`
- **Root Cause**: Docker is not installed on the local system.
- **Affected Files**: `docker-compose.yml`, `Dockerfile`
- **Recommended Fix**: Install Docker Desktop or Docker Engine on the host machine.

---

## ACTUAL IMPLEMENTED FEATURES
- **Basic FastAPI Application Shell**: Endpoints, middleware (CORS, Logging), and configuration parsing.
- **Next.js UI Shell**: Basic package configuration.
- **Configuration Parsing**: Pydantic settings are correctly parsing environment variables.

## BROKEN FEATURES
- Local execution of Python tests and NPM builds.
- Lean 4 exporter relies on `lean` binary which is missing.

## MOCKED / MISSING FEATURES
- Almost all AI model interaction, retrieval, RAG, knowledge graph migrations, and reasoning systems (MCTS, SMT verifier) are stubbed with `pass` or hardcoded mock returns.

---

## TOP 10 BLOCKERS
1. Missing local Docker installation, preventing isolated testing.
2. Corrupted or misconfigured local Python environment (`encodings` missing).
3. Missing local `poetry` installation for dependency management.
4. Unstable Node.js/NPM installation causing build crashes.
5. Missing Lean 4 binary (`/usr/local/bin/lean`).
6. Core Epistemic Store logic (migrations, graph traversal) is mocked.
7. Verification Gateway (Z3 SMT solver) is completely mocked (`pass`).
8. Arxiv document parser is entirely mocked (`pass`).
9. MCTS solver returns dummy mathematical rules instead of actual proof steps.
10. AI Gateway heavily relies on `"mock-model"` without a real unified LLM connector.

## TOP 10 HIGHEST-VALUE NEXT TASKS
1. Fix local Python and Node environments (or strictly enforce Docker installation).
2. Implement core SQLite Epistemic Store schemas and migrations to replace `pass` blocks.
3. Replace the `mock-model` LLM integrations with a real LiteLLM or OpenAI client implementation.
4. Implement the ArxivParser to genuinely extract text/metadata from arXiv links.
5. Replace dummy Retrieval/RAG regex with actual semantic chunking and embedding logic.
6. Install Z3 and implement the SMT Gateway verification logic.
7. Implement proper JWT authentication logic in the UI and backend (currently just an environment variable).
8. Build a real frontend dashboard to interact with the API endpoints.
9. Implement the MCTS algebraic solver.
10. Setup proper testing infrastructure with GitHub Actions and realistic mock fixtures.
