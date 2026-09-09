# AXIOM — Epistemic Scientific Research & Formal Proof Engine (v0.2.0)

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Release](https://img.shields.io/badge/version-0.2.0--scientific-runtime-blue.svg)](https://github.com/anujjha101296-lang/AXIOM/releases)

**AXIOM** is an evidence-first scientific research platform. Its current wedge is computational physics and mathematical intelligence: bounded hypotheses, deterministic experiments, provenance, numerical critique, reproducibility, and formal verification paths.

> **Design principle:** agents propose and investigate; deterministic scientific systems establish computational evidence.

## Current capabilities

### Scientific runtime
- Deterministic Lorenz simulation and paired-trajectory sensitivity experiments.
- Parameter sweeps and timestep-convergence checks.
- Independent midpoint-integrator cross-check.
- Explicit evidence tier `NUMERICAL_OBSERVATION`.
- Provenance metadata, content hashing, and Markdown/JSON evidence reports.
- Deterministic scientific critic with explicit acceptance/rejection gates.
- Fixed `lorenz-evidence-v1` benchmark contract.
- Bounded research loop: planner → hypothesis → experiment design → execution → critic → verification/repeat → completion/failure.

### Existing research platform
- Scientific knowledge/claim graph.
- Research workspace for projects, documents, notes, search, and paper Q&A.
- Hypothesis reasoning and experiment APIs.
- SMT/Z3 and Lean-oriented verification infrastructure.
- Research pipeline, mission control, control plane, evaluation, and observability components.

## Epistemic safety

AXIOM deliberately distinguishes:

```text
GENERATED
   ↓
NUMERICAL_OBSERVATION
   ↓
NUMERICALLY_ROBUST
   ↓
INDEPENDENTLY_CHECKED
   ↓
SYMBOLICALLY_VERIFIED
   ↓
FORMALLY_VERIFIED
```

A numerical observation is never presented as a mathematical proof merely because an AI model says so.

## Local quickstart

```bash
git clone git@github.com:anujjha101296-lang/AXIOM.git
cd AXIOM
python3 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt  # or: poetry install
```

Run the deterministic scientific runtime:

```bash
python -m axiom.science_runtime.cli --rho 28
python -m axiom.science_runtime.cli --sweep
python -m axiom.science_runtime.cli --evidence --rho 28 --json-out axiom_lorenz_evidence.json --report-out axiom_lorenz_report.md
```

Run the bounded research loop from Python:

```python
from axiom.science_runtime import ResearchQuestion, run_research

run = run_research(ResearchQuestion(
    text="Investigate robust sensitivity in the Lorenz system.",
    max_experiments=1,
    allowed_rho=(28.0,),
))
print(run.stage)
print(run.conclusion)
```

Optional local planning is available through Ollama. No paid API is required for the deterministic scientific runtime.

## API / UI

The broader platform uses FastAPI and Next.js. The intended product object is a **Research Run** with an evidence timeline, experiment artifacts, verification state, and provenance inspector—not a generic chat transcript.

```bash
alembic upgrade head
uvicorn axiom.services.api_gateway.main:app --reload --port 8000

cd ui
npm install
npm run build
npm run dev
```

## Verification status

Do not infer green status from this README. The authoritative signal is the current CI run and independently executed local tests. The latest development environment has not independently executed the new scientific test suite, so this repository does not claim a fresh local pass here.

## Architecture

See [`docs/AXIOM_TECHNICAL_EVOLUTION.md`](docs/AXIOM_TECHNICAL_EVOLUTION.md) for the target architecture covering agent orchestration, scientific tools, PostgreSQL/JSONB/pgvector, backend jobs, frontend research runs, observability, security, and evaluation.

## Two-month target

The near-term objective is a reproducible end-to-end workflow:

**scientific question → falsifiable hypothesis → bounded experiment → deterministic execution → critique → independent verification → reproducible report**

The longer-term goal is to evaluate whether this architecture can produce genuinely useful scientific progress beyond a plain LLM plus scripts.

## License

Licensed under the [MIT License](LICENSE).
