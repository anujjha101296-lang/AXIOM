# AXIOM Master Progress Report

**Checkpoint date:** 2026-08-06  
**Branch analyzed:** `cursor/milestone-005-research-loop-dc7e` @ `70bfc70`  
**Tag:** `v0.3.0-research-loop`  
**Scope:** Repository-wide engineering status (no new capabilities built during this checkpoint)

---

## Executive Summary

AXIOM has a **working researcher wedge** (Research Workspace + auth + demo scripts) and a **first closed-loop research orchestration slice** (Milestone 005) with heuristic workers, failure memory, benchmarks, API, and UI. The **Sprint 0 engineering baseline is ~75% complete** — runtime, core tests, and verification truthfulness are green; the **EPIC-002 integration gate (S0-E4) remains open**.

The platform is **demo-ready for internal/trusted use** but **not production-ready** for external users. Core test evidence: **182/182 pass** (`pytest tests/ --ignore=tests/e2e`). Full e2e: **200 pass / 26 fail** (MDE API surface gap).

| Lens | Completion | Notes |
|------|------------|-------|
| **Research Workspace product wedge** | **~72%** | End-to-end workflow works; P0 isolation, LLM, deploy gaps |
| **Autonomous Research Loop (M005 scope)** | **~85%** of v1 spec | Orchestration complete; intelligence is heuristic, not LLM |
| **Autonomous research vision (true AI)** | **~30%** | Keyword benchmarks, template hypotheses, no model-backed reasoning |
| **Sprint 0 engineering baseline** | **~75%** | S0-E1–E3 done; S0-E4 open |
| **Full platform (MIP + MDE + SCEP + workflow)** | **~45%** | Many subsystems partial or unrouted |
| **Overall repository toward stated vision** | **~46%** | Weighted across product, platform, research, company tracks |

**Production readiness:** **Not ready** — classified as **Development / Demo** (TRL ~4 for product wedge, TRL ~3 for autonomous loop).

---

## 1. Overall Completion Percentage

**Composite estimate: 46%** toward the full AXIOM vision documented in `VISION.md`, `.axiom/ROADMAP.md`, and root `roadmap.md`.

Breakdown by major workstream:

| Workstream | Weight | % Complete | Evidence |
|------------|--------|------------|----------|
| Operating system & contracts | 5% | 90% | `.axiom/*`, `ENGINEERING.md`, `ARCHITECTURE.md` |
| Sprint 0 baseline | 10% | 75% | S0-E2/E3 green; S0-E4 open |
| Research Workspace (EM-001, MVP-0) | 25% | 72% | `MVP_READINESS.md`, 166→182 core tests, demos |
| MIP / core math intelligence | 15% | 55% | MIP routes + tests; prover simulation fallbacks |
| MDE discovery engine | 10% | 25% | Only `GET /mde/retrieval` mounted; 26 e2e failures |
| SCEP / evaluation (EPIC-002) | 10% | 50% | Framework + `/eval/*`; no S0-E4 evidence gate |
| Workflow engine | 5% | 40% | Engine + HTTP router; zero dedicated core tests |
| Research Loop (M005) | 15% | 85% (v1) / 30% (vision) | `axiom/research_loop/`, UI, 16 tests |
| Deployment & ops | 5% | 35% | API Dockerfile + CI/CD; broken compose for UI/Grafana |

---

## 2. Production Readiness

| Dimension | Status | Score (0–5) |
|-----------|--------|-------------|
| Functional completeness (workspace wedge) | Demo-ready | 3.5 |
| Security & tenancy | **Critical gaps** | 1.5 |
| Reliability & observability | Partial logging/metrics | 2.0 |
| Test confidence | Core strong; e2e/platform weak | 3.0 |
| Deployability | API image only; compose incomplete | 2.0 |
| Documentation honesty | Good (`MVP_READINESS.md`, M005 limits) | 4.0 |
| AI/LLM production path | Mock fallback default | 1.5 |

**Verdict:** Suitable for **local demos**, **internal dogfooding**, and **trusted closed pilots with written limitations**. Not suitable for **public alpha**, **paid SaaS**, or **unsupervised external access** without resolving P0 blockers in `MVP_READINESS.md`.

---

## 3. Milestones — Fully Implemented

| ID | Milestone | Evidence |
|----|-----------|----------|
| S0-E1 | Engineering contract | `VISION.md`, `ENGINEERING.md`, `ARCHITECTURE.md`, `.axiom/CONSTITUTION.md` |
| S0-E2 | Supported runtime & core test baseline | CI Python 3.11; **182/182** core tests |
| S0-E3 | Verification truthfulness audit | `axiom/core/verification/truthfulness.py`, regression tests |
| EM-001 | Research Workspace production slice | `/research` API + UI, PDF ingest, notes, FTS, Q&A, sessions |
| MVP-0 | Stabilization sprint | Auth, UX, `MVP_READINESS.md`, `scripts/demo_mvp_workflow.sh` |
| M005 | Autonomous Research Loop v1 (as scoped) | `axiom/research_loop/`, `/research-loop/*`, `/research/runs`, tag `v0.3.0-research-loop` |

---

## 4. Milestones — Partially Implemented

| ID | Milestone | Done | Remaining |
|----|-----------|------|-----------|
| S0-E4 | EPIC-002 integration gate | Eval framework committed; `/eval/run` works | No `evidence_state`/`limitations` on scores; hardcoded `/eval/scores` fallback |
| P0-WEB | Public landing | Responsive landing, CTA to login | Waitlist non-functional; capability claims need ongoing sync |
| EPIC-001 (MIP) | Mathematical Intelligence Platform | Knowledge ingest, conjecture, strategy, verify routes | Corpus-scale quality unmeasured; prover adapters simulate when compilers absent |
| MDE | Mathematical Discovery Engine | `TheoremRetrievalEngine`, `GET /mde/retrieval` | Conjecture, counterexample, strategy routes exist in e2e stubs but not production router |
| Workflow | Generic workflow engine | `axiom/workflow/engine.py`, `/workflows/*` mounted | No core tests; workflow router lacks auth |
| Auth | User authentication | Register/login/JWT | No per-user data isolation; no reset/verification |
| H1-OBS | Provenance records | Logging, eval run IDs | No unified provenance linking loop inputs, config, evidence tier |
| Track C PMO | Operating cadence | AOS documents exist | C0-PMO marked in progress |

---

## 5. Milestones — Architecture Only

| Area | Status | Notes |
|------|--------|-------|
| EPIC-003+ | Referenced in capability deltas only | No committed implementation path |
| Full MDE HTTP surface | E2e tests define expected API; production has 1 route | `tests/e2e/test_m4_m5_e2e.py` etc. |
| Semantic / vector search | Documented aspiration | FTS5 keyword only |
| LLM-backed research loop | ModelClient exists | Not wired to loop workers |
| Prize-track autonomous discovery | `PRIZE_TRACK.md` constraints | No verified novel contributions |
| Grafana observability stack | `docker-compose.yml` references provisioning | `deploy/grafana/provisioning/` missing |
| UI containerized deploy | Compose expects `ui/Dockerfile` | File does not exist |
| Multi-tenant SaaS | — | Single shared SQLite store |
| Institution SSO / billing | — | Not started |

---

## 6–12. Gap Analysis

### 6. Missing Infrastructure

- Per-user tenancy and row-level isolation on `ResearchStore`
- Production secret enforcement (`JWT_SECRET_KEY` default unsafe)
- TLS termination and reverse-proxy documentation
- `ui/Dockerfile` and validated full-stack `docker-compose up`
- `deploy/grafana/provisioning/` dashboards
- Rate limiting on auth endpoints
- Email service (verification, password reset)
- CI runs core tests only — e2e not in CI gate
- Unified provenance / run-record store (H1-OBS)

### 7. Missing UI

- Document extracted-text preview (char count only)
- Functional waitlist on landing page
- Integration between `/workspace` graph canvas and `/research` projects
- Research loop navigation from main research workspace
- Upload progress indicator for large PDFs
- Eval/capability score dashboard
- Session expiry / refresh UX
- Component/E2E UI tests (none)

### 8. Missing Backend

- `user_id` scoping on all research CRUD
- MDE routes: conjecture generation, counterexample search, strategy, memory snapshot (beyond retrieval)
- Password reset and email verification APIs
- JWT refresh token flow
- OCR pipeline for scanned PDFs
- Auth on `/workflows/*`
- Semantic embedding index
- Account deletion and data export (GDPR)

### 9. Missing AI Functionality

- `ModelClient` wired to research loop workers (currently keyword templates)
- Production LLM configuration path with grounded citations for Q&A
- Vector RAG over uploaded papers
- LLM-based literature synthesis in loop
- Formal proof checking in benchmark scoring (keyword match only)
- Hypothesis engine / MCTS integration into loop (listed as future in M005 doc)

### 10. Missing Testing

- **26 e2e failures** — MDE API surface not implemented
- Zero dedicated tests for `axiom/workflow/`
- S0-E4 acceptance tests (evidence state, limitations on all scores)
- UI/component test suite
- Load tests for long research loops (>20 iterations)
- Integration tests for docker-compose stack

### 11. Missing Deployment

- Production deployment guide for researchers
- UI image build and CD pipeline (API-only CD exists)
- Environment matrix (dev/staging/prod) documentation
- Secrets management runbook
- Database backup/migration ops for SQLite → scalable store (future)

### 12. Missing Documentation

- Production hosting guide (called out in `MVP_READINESS.md` P2 #17)
- Stale blocker in `ARCHITECTURE.md` (Python 3.9 — resolved)
- MDE API gap documentation (e2e expects routes not in `mde.py`)
- User onboarding / researcher quickstart beyond demo scripts
- Operational runbook for monitoring (Prometheus exists; Grafana incomplete)

---

## 13–17. Stage Gate Blockers

### 13. Public Alpha

All **P0** items from `MVP_READINESS.md`:

1. No per-user data isolation
2. Default JWT secret in production
3. No HTTPS/TLS termination
4. No password reset or email verification
5. Q&A and summaries use mock model unless API keys configured

**Gate:** Public alpha **not recommended** until P0 #1–#5 resolved.

### 14. Closed Beta (trusted researchers)

**Minimum:**

- P0 #2 (secrets) and #3 (HTTPS)
- Explicit disclosure of P0 #1 (shared data) OR implement isolation
- Demo script + `MVP_READINESS.md` shared with participants

**Ideal add-ons:** P0 #5 (real LLM), rate limiting, basic deploy guide

**Estimate to minimum gate:** **2–3 weeks**

### 15. First Paying Customer

**Requires everything in public alpha plus:**

- Per-user isolation and data export/deletion
- Billing integration and usage metering
- SLA/uptime monitoring (complete observability stack)
- Support channel and incident response
- Production LLM with cost controls
- Legal (ToS, privacy policy, DPA)
- Hardened auth (MFA option, account recovery)

**Estimate:** **8–12 weeks** after closed beta learnings

### 16. Research Lab Pilot

**Requires:**

- S0-E4 complete (honest capability scores with evidence state)
- H1-OBS provenance records for runs and evaluations
- Written pilot scope with explicit non-claims (`PRIZE_TRACK.md` alignment)
- Reproducible benchmark artifacts exportable to lab
- Optional: institution-friendly deploy (on-prem or VPC)

**Estimate:** **3–5 weeks** (S0-E4 + H1-OBS + pilot packaging)

### 17. Autonomous Research Demonstration

**Requires:**

- Research loop workers backed by real reasoning (LLM + tools) OR substantially expanded heuristic domain
- Benchmark scoring beyond keyword matching
- Provenance chain from objective → evidence → claim status → report
- Human approval gates tested under realistic scenarios
- Demo narrative with honest limitation disclosure (`docs/MILESTONE_005.md`)

**Current state:** Orchestration demo works; **scientific autonomy demo does not**.

**Estimate:** **6–10 weeks** for a credible staged demo (heuristic → LLM-assisted)

---

## Time & Risk Estimates

### Weeks Remaining (engineering-focused)

| Target | Estimate | Assumptions |
|--------|----------|-------------|
| S0-E4 integration gate | **1–2 weeks** | Focused eng; no new features |
| H1-OBS provenance | **2–3 weeks** | After S0-E4 |
| Closed beta (minimum) | **2–3 weeks** | Secrets, HTTPS, disclosure |
| Public alpha | **4–6 weeks** | All P0 + deploy docs |
| Credible autonomous research demo | **6–10 weeks** | LLM wiring + provenance + benchmarks |
| Full platform maturity (roadmap M3) | **6–12+ months** | MDE surface, e2e green, measured capabilities |

### Largest Technical Risks

1. **Shared data store without tenancy** — data leak between users; blocks any external launch
2. **EPIC-002 scores without evidence gate** — overstated capability claims in `/eval/scores` fallback
3. **MDE API divergence** — 26 failing e2e tests signal large unrouted backend surface
4. **Heuristic research loop presented as AI** — reputational risk if demos oversell
5. **SQLite single-node limits** — concurrency and scale ceiling for pilots

### Largest Product Risks

1. **Mock LLM default** — researchers get low-quality Q&A/summaries out of the box
2. **Disconnected UIs** — `/workspace` vs `/research` confuses value proposition
3. **Keyword search vs semantic expectation** — mismatch with "AI research workspace" positioning
4. **No production deploy path** — friction kills early adopter conversion
5. **Waitlist broken** — damages trust on landing page

### Largest Research Risks

1. **Keyword benchmark scoring** — cannot validate scientific reasoning quality
2. **No formal proof linkage in loop** — verification tier may be misinterpreted
3. **Failure memory without cross-run learning** — limited generalization
4. **Prize-readiness scores** — internal hypotheses without independent review (`PRIZE_TRACK.md`)
5. **Simulation fallbacks in provers** — risk of conflating heuristic with formal results (mitigated by S0-E3 for labeled routes)

---

## Recommended Next Milestone

### **S0-E4 — EPIC-002 Integration Gate**

**Why this milestone (repository evidence, not original roadmap order):**

1. **Explicitly queued** as rank 6, "Ready — highest priority" in `.axiom/TASK_QUEUE.md`
2. **Blocks H1-OBS** (rank 7), which Milestone 005 and `CURRENT_STATE.md` identify as the next capability unlock
3. **`/eval/scores` returns hardcoded baseline** when DB empty — no `evidence_state`, `benchmark_count`, or `limitations` on API responses per S0-E4 acceptance criteria
4. **Aligns with checkpoint directive** — finish engineering baseline before more feature surface
5. **Lower risk than public alpha P0** — no new user-facing scope; strengthens integrity of all downstream demos and pilots

**Acceptance signal:** All capability and prize-readiness scores exposed via API include evidence state, benchmark count, and stated limitations; focused regression tests green.

**Immediately after S0-E4:** **H1-OBS** — reproducible provenance records linking research loop runs, SCEP evaluations, and evidence tiers.

---

## Test Evidence Snapshot

```
Core:  pytest tests/ --ignore=tests/e2e  →  182 passed
E2E:   pytest tests/e2e                 →  200 passed, 26 failed
CI:    .github/workflows/ci.yml         →  core only, coverage ≥50%
Tag:   v0.3.0-research-loop
```

## Key Artifacts

| Artifact | Path |
|----------|------|
| MVP readiness & P0 blockers | `MVP_READINESS.md` |
| Research loop limitations | `docs/MILESTONE_005.md` |
| Operational truth | `.axiom/CURRENT_STATE.md`, `.axiom/TASK_QUEUE.md` |
| Roadmap | `.axiom/ROADMAP.md`, `roadmap.md` |
| Demo scripts | `scripts/demo_mvp_workflow.sh`, `scripts/demo_research_loop.sh` |
| Roadmap status detail | `ROADMAP_STATUS.md` |
| Scored dimensions | `ENGINEERING_SCORECARD.md` |

---

*Generated during AXIOM Engineering Checkpoint — feature development frozen; analysis only.*
