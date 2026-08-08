# AXIOM Research Readiness

**Verification date:** 2026-08-07  
**Audience:** Internal scientific capability evaluation  
**Scope:** Verified research infrastructure, benchmarks, and limitations only.

---

## Readiness Verdict

| Dimension | Score (governance) | Verified assessment |
|-----------|-------------------:|---------------------|
| **Overall research readiness** | 20.4/100 | **Early-stage — strong measurement, limited discovery depth** |
| Benchmark infrastructure | — | **Ready for internal use** |
| Formal proof pipeline | — | **Simulated only** (no Lean/Coq/Isabelle) |
| Autonomous discovery loop | — | **Not present on branch** |
| Known-answer validation | — | **Operational** (96.2% pass rate) |
| Evidence honesty (S0-E4) | — | **Implemented and tested** |

**Bottom line:** AXIOM has credible internal instrumentation to measure scientific capability (EPIC-002 + RVP) with explicit evidence states and limitations. It does not yet demonstrate research-active autonomous discovery at the level implied by marketing copy. Formal verification is simulated in the current environment.

---

## Research Measurement Systems (Verified)

### EPIC-002 — Scientific Capability Evaluation Platform

**Status:** Fully implemented and demonstrated.

| Component | Verified |
|-----------|----------|
| 8 capability dimensions (L0–L5) | ✅ |
| S0-E4 evidence gate (`evidence_state`, `benchmark_count`, `limitations`) | ✅ 5 dedicated tests |
| Benchmark execution | ✅ `POST /eval/run` |
| Prize readiness (6 Millennium problems) | ✅ |
| Run history persistence | ✅ SQLite `eval_runs` |
| Delta reporting | ✅ `benchmark_results.json` |

**Latest verified scores (2026-08-07):**

| Dimension | Score | evidence_state |
|-----------|------:|----------------|
| mathematical_reasoning | 1.0 | measured |
| proof_verification | 1.0 | measured |
| conjecture_generation | 1.0 | measured |
| knowledge_quality | 0.8 | measured |
| counterexample_search | 1.0 | measured |
| research_planning | 1.0 | measured |
| literature_synthesis | 0.6 | measured |
| research_productivity | 1.0 | measured |
| **Composite** | **0.944** | |

**Regressions detected:** knowledge_quality (−15%), literature_synthesis (−35%) vs prior snapshot.

**Stated limitations (from evidence gate, verified on API response):**
- Benchmarks use symbolic/heuristic checks, not competition-level problem solving
- Proof verification simulates when formal compilers absent
- Conjecture quality degrades on empty knowledge graph
- Counterexample search is bounded heuristic enumeration

**Tests:** 37 passing across `test_eval_api`, `test_evaluation_platform`, `test_s0_e4_evidence_gate`, `test_scep_e2e`, `test_benchmark`

---

### Research Validation Program (RVP)

**Status:** Fully implemented and demonstrated.

| Component | Verified |
|-----------|----------|
| Stages 0–6 framework | ✅ `GET /rvp/stages` |
| Known-answer dataset | ✅ **266 problems** |
| Stage execution | ✅ `POST /rvp/runs` |
| 10-dimension Research Capability Score | ✅ `CAPABILITY_SCORE.md` |
| Dashboard API | ✅ `GET /rvp/dashboard` |
| Config-hash replay | ✅ `POST /rvp/runs/replay` |
| Report generation | ✅ `make research-validation` |

**Latest verified benchmark results:**

| Metric | Value |
|--------|------:|
| Overall pass rate | 96.2% (52 runs) |
| Stage 0 mean answer score | 1.000 |
| Stage 1 mean answer score | 0.651 |
| Failures | 2 (`answer_score_below_threshold`) |
| Capability composite | 0.705 |

**10-dimension scores (aggregate):**

| Dimension | Score |
|-----------|------:|
| Problem Understanding | 0.920 |
| Reasoning | 0.893 |
| Verification | 0.866 |
| Reproducibility | 0.900 |
| Evidence Quality | 0.750 |
| Knowledge Integration | 0.793 |
| Planning | 0.700 |
| Literature Retrieval | 0.600 |
| Recovery From Failure | 0.408 |
| Human Intervention Required | 0.219 (inverted) |

**Tests:** 6 passing in `tests/test_research_validation.py`

**Known limitations:**
- Dashboard requires `rvp_runs` table — fails on uninitialized DB until first run
- Stage 1 underperforms Stage 0
- LLM-backed improvement not verified in this environment

---

## Mathematical Research Infrastructure (Verified)

### MIP — Mathematical Intelligence Platform

**Status:** Fully implemented (API); formal tools simulated.

| Subsystem | Endpoints | Tests |
|-----------|-----------|------:|
| Knowledge ontology | 3 | ✅ |
| Formal proof generation | 2 | ✅ (simulated compile) |
| Conjecture generation | 2 | ✅ |
| Strategy & planning | 3 | ✅ |
| Memory | 3 | ✅ |
| Verification consensus | 1 | ✅ |

**Verification demo:**
```
POST /mip/conjecture/generate → 200 (conjectures returned)
GET  /mip/knowledge/domain/algebra → 200 (empty on fresh DB)
```

**Tests:** 64/64 in `tests/mip/test_mip_all.py`

**Limitations:**
- Lean 4, Coq, Isabelle not installed — all formal compile paths simulate
- `mip_conjectures` table not created on fresh DB — persistence warnings

---

### Core Reasoning & Verification

| Capability | Status | Evidence |
|------------|--------|----------|
| SMT counterexample (Z3) | ✅ Implemented | `test_verification_truthfulness` |
| MCTS algebraic proof search | ✅ Implemented | `test_reasoning_pipeline` |
| Truthfulness assignments (S0-E3) | ✅ Implemented | 10 tests — simulated never marked formal |
| Hypothesis generation | ✅ Implemented | Returns 0 on empty graph (verified) |
| SymPy engine | ✅ Present | E2E partial |

**Formal proof honesty (verified):**
- `assign_from_proof_search` with simulated compiler → `formally_proven: false`, `TIER_1_SIMULATED`
- SMT modular → never `TIER_2_PROVEN`

---

### MDE — Mathematical Discovery Engine

**Status:** Partially implemented.

| Item | Verified |
|------|----------|
| Theorem retrieval engine | ✅ `GET /mde/retrieval` returns matches |
| Full MDE API (problems, claims, snapshots) | ❌ Not mounted |
| Ontology tests | ✅ 18 tests in `test_mde_ontology.py` |
| E2E MDE scenarios | ❌ 26 failures include MDE surface gaps |

**Demo:**
```
GET /mde/retrieval?query_formula=x^2+y^2=z^2 → 200 (matched theorems)
```

---

### Epistemic Knowledge Graph

**Status:** Implemented; empty by default.

- Schema, migrations, and export API verified
- Population requires successful ingest or manual node creation
- `POST /ingest` failed in live demo (arXiv 404 for test paper ID)

---

## Research Loops & Automation (Verified Absent)

| System | Branch status | HTTP | Tests |
|--------|--------------|------|------:|
| Research loop | ❌ No source directory | 404 | 0 |
| Workflow engine | 📐 Code exists | 404 (not mounted) | 0 |
| Autonomous discovery e2e | — | — | 8 tier3/tier4 failures |

**Implication:** Long-horizon autonomous research loops cannot be evaluated on this branch.

---

## Research Product Integration

### Research Workspace (scientific utility)

| Feature | Research value | Verified |
|---------|---------------|----------|
| PDF ingestion for Q&A | Literature grounding | ⚠️ API + unit tests; PDF required |
| Document summarization | Literature synthesis input | ⚠️ Requires PDF + ModelClient |
| Project-scoped search | Knowledge retrieval | ✅ Endpoint works |
| arXiv parser | Literature ingestion | ⚠️ Network-dependent; demo failed |

### Model Gateway

- `axiom/services/model_gateway/client.py` exists
- Used by `PaperQA` and `DocumentSummarizer`
- Live LLM quality **not verified** in this review (no API key/config demonstrated)

---

## Benchmark Regression Status

From `RESEARCH_HEALTH.md` and `benchmark_results.json`:

| Regression | Delta |
|------------|-------|
| knowledge_quality | 0.95 → 0.8 (−15%) |
| literature_synthesis | 0.95 → 0.6 (−35%) |

Governance reports **2 benchmark regressions**, **0 improvements** in latest cycle.

---

## What Research Evaluators Can Trust Today

| Trust level | Finding |
|-------------|---------|
| **High** | EPIC-002 scores include explicit `evidence_state` and `limitations` |
| **High** | S0-E3 truthfulness prevents simulated proofs being labeled formal |
| **High** | RVP known-answer dataset and replay via config hash |
| **High** | MIP unit test suite (64 tests) |
| **Medium** | EPIC-002 composite 0.944 — measured but heuristic benchmarks |
| **Medium** | RVP 96.2% pass — Stage 1 weaker than Stage 0 |
| **Low** | Formal proof claims without installed provers |
| **Low** | Literature synthesis score (0.6) with no live LLM verification |
| **None** | Autonomous discovery loop (not on branch) |

---

## Demonstrated Research Workflows

| Workflow | Command / API | Result |
|----------|--------------|--------|
| Full capability benchmark | `POST /eval/run` | ✅ composite 0.944 |
| Prize readiness ranking | `GET /eval/prize-readiness` | ✅ P vs NP top |
| RVP infrastructure stage | `make research-validation` | ✅ 10/10 Stage 0 |
| RVP API stage run | `POST /rvp/runs` stages=[0] | ✅ 10 runs |
| MIP conjecture batch | `POST /mip/conjecture/generate` | ✅ 5 conjectures |
| MDE formula retrieval | `GET /mde/retrieval` | ✅ matches returned |
| SMT verify (unit tests) | pytest verification suite | ✅ 10/10 |
| arXiv ingest (live) | `POST /ingest` | ❌ arXiv 404 |
| Research Q&A (live) | `POST .../ask` | ❌ 422 without PDF |

---

## Scientific Honesty Assessment

AXIOM's verified research infrastructure prioritizes measurement transparency:

1. **S0-E4 evidence gate** — every eval dimension exposes `evidence_state`, `benchmark_count`, and `limitations` (verified on live API response).
2. **S0-E3 truthfulness** — simulated compiler output cannot be labeled `formally_proven: true` (10 regression tests).
3. **RVP staged validation** — separates infrastructure (Stage 0) from known-answer problems (Stage 1+).
4. **Governance research health** — explicitly scores research capability at 20.4/100, not marketing-inflated.

**Gap:** Marketing UI (`ui/src/app/page.tsx`) describes capabilities (autonomous discovery, interactive graph canvas) that are not verified as working end-to-end on this branch.

---

## Readiness by Research Phase

| Phase | Ready? | Notes |
|-------|--------|-------|
| Instrumentation & benchmarking | ✅ Yes | EPIC-002 + RVP operational |
| Known-answer regression testing | ✅ Yes | 266 problems, replay |
| Heuristic reasoning benchmarks | ✅ Yes | Composite 0.944 |
| Formal verification (real provers) | ❌ No | Simulated in env |
| LLM-backed literature synthesis | ⚠️ Unverified | Score 0.6; no live demo |
| Autonomous discovery loops | ❌ No | Not on branch |
| Prize-problem attack surface | ⚠️ Early | Readiness scores exist; no verified progress |

---

## Recommended Internal Evaluation Protocol

1. Run `make research-validation` and archive the four generated reports.
2. Run `POST /eval/run` and inspect `evidence_state` per dimension in response.
3. Run `pytest tests/test_s0_e4_evidence_gate.py tests/test_verification_truthfulness.py` — confirm honesty gates.
4. Run `pytest tests/mip/test_mip_all.py` — confirm MIP regression suite.
5. Exercise `GET /mde/retrieval` with domain-relevant formulas.
6. **Do not** treat UI marketing copy as evidence of working research loops.
7. **Do not** treat simulated formal compile as mathematical proof.

---

## Governance Cross-Reference

Automated research capability score: **20.4/100** (`RESEARCH_HEALTH.md`, 2026-08-07)

Council recommendation (verified as still applicable): wire ModelClient to research workers; complete provenance records (H1-OBS) linking RVP and SCEP runs.

---

*Research readiness reflects verified benchmarks, tests, and API demonstrations only. Formal proof claims require installed provers and independent audit beyond this report.*
