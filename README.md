# AXIOM — Epistemic Scientific Research & Formal Proof Engine (v0.1.0 Founder Release)

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/anujjha101296-lang/AXIOM)
[![Release](https://img.shields.io/badge/version-0.1.0--founder-blue.svg)](https://github.com/anujjha101296-lang/AXIOM/releases/tag/v0.1.0)

**AXIOM** is an autonomous scientific research, hypothesis formulation, computational experiment, and formal proof verification engine. AXIOM combines semantic retrieval, claim graphs, hypothesis reasoning, sandboxed numerical simulation, and interactive theorem proving (Lean 4 / SMT Z3) into a single production-ready platform.

---

## 🌟 Key Capabilities

### 1. Scientific Knowledge Graph & Claim Graph (Phase 13)
- Provenance chain: $\text{CLAIM} \rightarrow \text{EVIDENCE} \rightarrow \text{CHUNK} \rightarrow \text{SOURCE} \rightarrow \text{DOCUMENT/URL}$
- Conservative entity resolution with multi-tier matching.
- Explicit disagreement & contradiction detection (`Claim A CONTRADICTS Claim B`).

### 2. Hypothesis & Scientific Reasoning Engine (Phase 14)
- Controlled status lifecycle: `PROPOSED`, `UNDER_REVIEW`, `SUPPORTED`, `WEAKLY_SUPPORTED`, `CONTRADICTED`, `FALSIFIED`, `INCONCLUSIVE`, `RETIRED`.
- Scientific critique engine evaluating logical consistency, circular reasoning, and unfalsifiability.
- Observable predictions with explicit falsifiers.

### 3. Computational Experiment & Verification Engine (Phase 15)
- Sandboxed Python computational execution with AST safety validation and `sys.settrace()` runtime limits (5s timeout, 128MB RAM limit, 50KB output limit).
- Dual-run reproducibility testing & independent analytical/numerical verifiers.
- **Epistemic Principle**: Finite computational observation $\neq$ mathematical proof.

### 4. Formal Mathematics & Proof Verification Engine (Phase 16)
- **Lean 4 Integration**: Theorem skeleton generation, syntax checking, and `sorry`-free proof verification.
- **SMT Z3 Gateway**: Propositional & predicate logic satisfiability (`SAT`, `UNSAT`, `UNKNOWN`).
- **Counterexample Hunter**: Finite domain witness search.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.12+ / 3.13+
- Node.js 20+

### Local Setup
```bash
# 1. Clone repository
git clone git@github.com:anujjha101296-lang/AXIOM.git
cd AXIOM

# 2. Set up Python virtual environment
python3 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt # or poetry install

# 3. Apply database migrations
alembic upgrade head

# 4. Start FastAPI backend
uvicorn axiom.services.api_gateway.main:app --reload --port 8000

# 5. Start Next.js frontend (in separate terminal)
cd ui
npm install
npm run build --webpack
npm run dev --webpack
```

---

## 🐳 One-Command Docker Deployment

```bash
docker-compose up --build -d
```
- **Backend API**: `http://localhost:8000/docs`
- **Frontend Workspace**: `http://localhost:3000`

---

## 🧪 Benchmark & Test Verification

```bash
# Run 100% full regression test suite across all phases
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python -m pytest tests/ -v

# Run Phase 16 Formal Mathematics Benchmarks (12/12 Passed)
.venv312/bin/python benchmarks/phase16_formal_benchmark.py
```

---

## 📄 License
Licensed under the [MIT License](LICENSE).
