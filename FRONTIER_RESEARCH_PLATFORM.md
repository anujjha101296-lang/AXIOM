# AXIOM Frontier Research Platform Initiative

**Date:** 2026-08-07  
**Mission:** Transform AXIOM from an AI research assistant into a scientific discovery platform capable of credible participation in frontier research.

This document identifies verified gaps (from `VERIFIED_CAPABILITIES.md`) and groups missing work into seven major programs. **Implemented in this cycle:** H1-OBS Evaluation Provenance Records (Program 6).

---

## Program Overview

| # | Program | Current state | Gap severity | Implemented this cycle |
|---|---------|---------------|-------------|------------------------|
| 1 | Scientific Reasoning | Partial | High | — |
| 2 | Formal Mathematics | Partial (simulated) | High | — |
| 3 | Autonomous Research | Architecture only | Critical | — |
| 4 | Experimentation | Partial | Medium | — |
| 5 | Verification | Partial | High | — |
| 6 | Evaluation | **Strong** | Low (provenance was gap) | **H1-OBS** |
| 7 | Human Collaboration | Minimal | High | — |

---

## 1. Scientific Reasoning

### Current implementation
- MCTS algebraic proof search (`axiom/core/reasoning/mcts.py`)
- Hypothesis engine (`hypothesis_engine.py`)
- SymPy symbolic engine (`axiom/core/symbolic/`)
- MIP conjecture generation (`axiom/mip/conjecture/`)
- EPIC-002 mathematical_reasoning dimension (score 1.0, measured)

### Missing capabilities
- Competition-level problem solving (IMO, Putnam benchmarks)
- Multi-step deductive reasoning with backtracking and memory
- Cross-domain reasoning (algebra ↔ analysis ↔ topology)
- LLM-backed reasoning integrated with symbolic tools
- Research loop workers (not on branch)

### Dependencies
- Model gateway configuration
- Populated knowledge graph
- Formal verification feedback loop

### Risks
- Heuristic benchmarks inflate capability scores without frontier utility
- MCTS scope limited to algebraic identities

### Required infrastructure
- Reasoning benchmark suite beyond symbolic checks
- Tool-use orchestration (SymPy + Z3 + LLM)
- Long-horizon context (working memory persistence)

### Research benchmarks
- EPIC-002 mathematical_reasoning (10 cases)
- RVP Stage 1 known-answer (mean 0.651)
- No IMO/Putnam/FrontierMath benchmark

### Acceptance criteria
- Score ≥0.7 on held-out competition subset with measured evidence
- Reasoning traces auditable via provenance records
- Regression suite passes with no simulated formal claims

---

## 2. Formal Mathematics

### Current implementation
- Lean 4, Coq, Isabelle adapters (`axiom/mip/formal/`)
- Lean exporter for MCTS proofs (`lean_exporter.py`)
- MIP formal generate/compile API (`/mip/formal/*`)
- S0-E3 truthfulness gate (simulated ≠ formal)

### Missing capabilities
- Installed provers in CI/production (currently simulated)
- End-to-end formal proof of non-trivial theorems
- Proof certificate storage and replay
- Integration between MIP formal scripts and EGS nodes
- Mathlib/standard library awareness

### Dependencies
- Lean 4 / Coq toolchain in environment
- Populated `mip_conjectures` table on fresh DB
- Verification consensus wired to real compilers

### Risks
- Simulated compile success misread as capability by users ignoring evidence tier
- Formal adapters untested against real proof obligations

### Required infrastructure
- Docker image with Lean 4 + Mathlib
- Formal proof CI job (compile-on-push)
- Proof artifact store linked to provenance

### Research benchmarks
- EPIC-002 proof_verification (simulated, evidence_state=simulated)
- No real-prover benchmark suite

### Acceptance criteria
- ≥5 theorems compile with actual Lean/Coq in CI
- `evidence_state: measured` only when compiler returns success
- Formal proofs linked to EGS nodes with dependency edges

---

## 3. Autonomous Research

### Current implementation
- Workflow engine code (`axiom/workflow/`) — **not mounted**
- Research validation stages 0–6 framework
- Self-improvement loop (`self_improvement.py`)
- arXiv parser (network-dependent)

### Missing capabilities
- Research loop (`axiom/research_loop/` absent on branch)
- HTTP workflow API (`/workflows` → 404)
- Autonomous discovery loop (tier3/tier4 e2e failures)
- Paper reproduction pipeline (RVP Stage 2+)
- Literature-driven hypothesis generation

### Dependencies
- Workflow router mounted in `main.py`
- ModelClient wired to workers
- H1-OBS provenance (now available)
- Per-user research isolation

### Risks
- Autonomous loops without provenance produce un-auditable claims
- Workflow engine untested via HTTP

### Required infrastructure
- Mounted workflow API with checkpoint/replay
- Research loop orchestrator
- Event-driven task scheduling
- Human approval gates for irreversible actions

### Research benchmarks
- RVP Stages 2–6 (not routinely executed)
- E2E tier3/tier4 (8 failures)
- No autonomous discovery benchmark

### Acceptance criteria
- `POST /workflows` creates and runs a multi-step research workflow
- Workflow artifacts link to provenance records
- Stage 2 paper reproduction: ≥3/5 pilot papers reproduced

---

## 4. Experimentation

### Current implementation
- RVP known-answer dataset (266 problems)
- RVP staged execution with config-hash replay
- Research workspace (projects, PDF upload, Q&A)
- arXiv ingestion endpoint

### Missing capabilities
- Controlled experiment design (hypothesis, control, treatment)
- Paper reproduction experiments (RVP Stage 2)
- A/B comparison of reasoning strategies
- Experiment registry with pre-registration
- PDF Q&A with verified LLM backend

### Dependencies
- Model gateway production config
- Experiment provenance (extends H1-OBS)
- Per-user data isolation

### Risks
- Heuristic RVP scoring masks real experimental variance
- arXiv ingest fragile (live network)

### Required infrastructure
- Experiment registry table
- Pre-registration API
- Offline fixture mode for arXiv ingest

### Research benchmarks
- RVP 96.2% overall pass (Stage 0: 1.0, Stage 1: 0.651)
- No controlled A/B benchmark

### Acceptance criteria
- Experiment record includes hypothesis, method, inputs, stop condition
- Results link to H1-OBS provenance by run_id
- Stage 1 batch n≥50 with documented trend

---

## 5. Verification

### Current implementation
- SMT counterexample search (Z3)
- S0-E3 truthfulness assignments
- MIP verification consensus endpoint
- Epistemic status on EGS nodes

### Missing capabilities
- Independent verification of LLM-generated claims
- Cross-prover consensus (Lean + Coq agreement)
- Counterexample certificates stored and linked
- Human expert review workflow
- Verification tier on RVP runs (config flag unused)

### Dependencies
- Formal mathematics program (real provers)
- Verification invoked in RVP engine when `enable_verification=True`

### Risks
- Bounded SMT search presented as exhaustive
- No external auditor interface

### Required infrastructure
- Verification certificate store
- Expert review queue API
- RVP `enable_verification` wired to SMT/formal checks

### Research benchmarks
- EPIC-002 counterexample_search (1.0, measured)
- `test_verification_truthfulness.py` (10 tests)

### Acceptance criteria
- Every claim in EGS has explicit verification tier
- RVP runs with verification show `verification_invoked: true` in provenance
- No `formally_proven: true` without compiler success

---

## 6. Evaluation

### Current implementation
- EPIC-002 SCEP (8 dimensions, composite 0.944)
- S0-E4 evidence gate (`evidence_state`, `benchmark_count`, `limitations`)
- RVP (10-dimension Research Capability Score, 266 problems)
- Engineering governance (`make engineering-health`)
- **H1-OBS provenance records** (implemented this cycle)

### Missing capabilities
- ~~Unified provenance linking SCEP and RVP runs~~ ✅ H1-OBS
- Cross-run provenance queries at scale
- External benchmark import (FrontierMath, MATH, etc.)
- Eval regression CI gate on every PR
- Dashboard UI for scores and provenance

### Dependencies
- H1-OBS (complete)
- UI build fix for dashboards

### Risks
- Literature synthesis regression (−35%) undetected without CI gate
- Provenance without external benchmarks still internal-only

### Required infrastructure
- ✅ `run_provenance` table
- ✅ `/provenance/*` API
- CI benchmark regression job
- Grafana dashboard for eval metrics

### Research benchmarks
- EPIC-002: composite 0.944
- RVP: composite 0.705
- Governance research capability: 20.4/100

### Acceptance criteria
- [x] Every SCEP run has provenance with inputs, runtime, config, evidence tier
- [x] Every RVP run has provenance with config_hash and environment
- [x] `GET /provenance/runs/{type}/{id}` returns full envelope
- [ ] CI fails on capability regression >10%

---

## 7. Human Collaboration

### Current implementation
- Research workspace (projects, notes, conversations, sessions)
- Bearer token auth (static)
- Workflow approval gate in code (unmounted)

### Missing capabilities
- User accounts and login (`/auth/*` → 404)
- Per-user data isolation
- Collaborative graph editing
- Expert review assignment
- Research session sharing between users
- UI wired to API (build fails)

### Dependencies
- Auth endpoints
- `user_id` scoping in research store
- UI production build fix

### Risks
- Shared SQLite store prevents multi-researcher use
- No audit trail for human decisions

### Required infrastructure
- JWT auth with user registry
- Row-level tenancy in research tables
- Working Next.js UI with API integration

### Research benchmarks
- No collaboration benchmark
- Product health: 31/100

### Acceptance criteria
- Two users cannot access each other's projects
- Login/register flow functional
- UI displays eval scores and provenance for shared runs

---

## Selected Initiative: H1-OBS Evaluation Provenance Records

### Why this capability

| Criterion | Assessment |
|-----------|------------|
| Impact | Unlocks independent audit of all scientific claims |
| Dependency unlock | Required before autonomous research, external validation, publication |
| Scientific value | Makes RVP and SCEP results reproducible and citable |
| Engineering value | Single thin layer; reuses existing stores |
| Confidence | High — clear acceptance criteria, no new ML required |
| Reversibility | Additive table; no migration of existing blobs |

H1-OBS was rank 7 in `TASK_QUEUE.md` and the ONE recommended initiative in `NEXT_RESEARCH_TARGETS.md`. It is prerequisite infrastructure for every other program — without provenance, frontier research participation lacks credibility.

### What was implemented

| Component | Path |
|-----------|------|
| Provenance module | `axiom/observability/run_provenance.py` |
| Provenance API | `axiom/services/api_gateway/routes/provenance_api.py` |
| SCEP integration | `eval_api.py`, `run_benchmarks.py` |
| RVP integration | `research_validation/engine.py` |
| Tests | `tests/test_run_provenance.py` (13 tests) |
| Documentation | `docs/H1-OBS_run_provenance.md` |

### Verification

```
189/189 core tests pass
POST /eval/run → provenance recorded
POST /rvp/runs → provenance recorded per problem
GET /provenance/runs/scep/{id} → full envelope
GET /eval/history → duration_ms + evidence_tier
```

---

## Recommended Next Programs (sequenced)

1. **Mount workflow API** — unlocks Program 3 with minimal diff
2. **Merge research loop branch** — autonomous research orchestration
3. **Formal prover CI** — converts Program 2 from simulated to measured
4. **Auth + tenancy** — unlocks Program 7 for external validators
5. **Stage 1 RVP batch (n≥50)** — Program 4 experimentation at scale

---

*This initiative document reflects verified implementation as of 2026-08-07. See `VERIFIED_CAPABILITIES.md` for per-capability evidence.*
