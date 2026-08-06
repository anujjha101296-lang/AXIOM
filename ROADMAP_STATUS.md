# AXIOM Roadmap Status

**Checkpoint date:** 2026-08-06  
**Sources:** `.axiom/ROADMAP.md`, `roadmap.md`, `.axiom/TASK_QUEUE.md`, `.axiom/CURRENT_STATE.md`, `MVP_READINESS.md`, `docs/MILESTONE_005.md`

This document maps roadmap items to implementation reality. Status labels:

| Label | Meaning |
|-------|---------|
| **Complete** | Acceptance criteria met with test/demo evidence |
| **Partial** | Substantial code exists; acceptance criteria not fully met |
| **In progress** | Active work or queued as next |
| **Architecture** | Documented/designed only; no production path |
| **Deferred** | Explicitly postponed with dependency |

---

## Track A — Research (Continuous)

### Horizon 0 — Trustworthy Baseline

| Item | Roadmap ref | Status | % | Evidence / Gap |
|------|-------------|--------|---|----------------|
| Python 3.10+ runtime | S0-E2 | **Complete** | 100% | CI uses 3.11; Docker `python:3.11-slim` |
| Reproducible test baseline | S0-E2 | **Complete** (core) | 90% | 182/182 core; 26 e2e fail |
| Verification truthfulness | S0-E3 | **Complete** | 100% | `truthfulness.py`, API `evidence_mode` |
| EPIC-002 integration | S0-E4 | **In progress** | 40% | Framework committed; evidence gate open |
| Operating contract | S0-E1 | **Complete** | 100% | Vision, engineering, architecture docs |

**Horizon 0 aggregate: ~75%**

### Horizon 1 — Measurable Research Capability

| Capability | Status | % | Notes |
|------------|--------|---|-------|
| Ingest & parsing | Partial | 50% | arXiv/LaTeX code; PDF via pypdf; no OCR |
| Knowledge representation | Partial | 55% | SQLite/NetworkX; completeness unmeasured |
| Hypothesis generation | Partial | 45% | MCTS/conjecture modules; loop uses templates |
| Counterexample search | Architecture | 20% | Core code; MDE route not mounted |
| Formal verification | Partial | 60% | Z3/SMT + prover adapters; simulation fallbacks |
| Evaluation & benchmarks | Partial | 55% | 8-dimension SCEP; S0-E4 gate incomplete |
| Provenance & metrics | Partial | 30% | Prometheus metrics; H1-OBS not done |

**Horizon 1 aggregate: ~45%**

---

## Track B — Product (Continuous)

### Milestone 1 — Researcher Workflow MVP

| Deliverable | Status | % | Evidence |
|-------------|--------|---|----------|
| End-to-end researcher workflow | **Complete** | 85% | EM-001 + MVP-0 |
| Project CRUD | Complete | 100% | `/research/projects` |
| PDF upload & text extract | Complete | 90% | pypdf; no OCR |
| Summaries | Partial | 60% | Heuristic/mock model |
| Notes & tags | Complete | 100% | CRUD + FTS |
| Search | Partial | 50% | FTS5 keyword only |
| Paper Q&A | Partial | 60% | Works; mock LLM default |
| Session resume | Complete | 100% | Sessions API + UI |
| Auth (register/login) | Partial | 70% | No isolation, no reset |
| Honest documentation | Complete | 95% | `MVP_READINESS.md` |
| Demo script | Complete | 100% | `demo_mvp_workflow.sh` |

**Milestone 1 aggregate: ~72%** (functional MVP with known P0 gaps)

### Milestone 005 — Autonomous Research Loop v1

| Deliverable | Status | % | Evidence |
|-------------|--------|---|----------|
| Problem decomposition | Complete | 90% | Planner worker |
| Evidence retrieval | Partial | 60% | FTS fallback when no docs |
| Hypothesis generation & ranking | Partial | 50% | Keyword templates |
| Criticism & verification | Partial | 65% | Critic + SMT verifier workers |
| Failure memory | Complete | 90% | `failure_memory.py` |
| Replanning across iterations | Complete | 85% | Engine loop |
| Evidence-classified report | Complete | 85% | Reporter + `ClaimStatus` |
| Historical benchmarks (4) | Complete | 80% | Keyword scoring |
| API `/research-loop/*` | Complete | 95% | Auth-protected |
| UI `/research/runs` | Complete | 85% | Poll-based, no WebSocket |
| Tests & demo | Complete | 90% | 16 tests, `demo_research_loop.sh` |
| Tag release | Complete | 100% | `v0.3.0-research-loop` |

**Milestone 005 (v1 spec): ~85% complete**  
**Milestone 005 (autonomous research vision): ~30%** (heuristic intelligence)

### Milestone 2 — Public Alpha & Pilots

| Deliverable | Status | % | Blocker |
|-------------|--------|---|---------|
| Public alpha readiness | **Not started** | 15% | All P0 in `MVP_READINESS.md` |
| Feedback instrumentation | Architecture | 10% | No analytics pipeline |
| Technical demo (polished) | Partial | 50% | CLI demos exist; no hosted demo |
| Institutional pilots | Deferred | 0% | Human authorization required |
| 10–20 early users | Not measured | 0% | No user tracking |

**Milestone 2 aggregate: ~10%**

### Milestone 3 — Validated Research Platform

| Deliverable | Status | % |
|-------------|--------|---|
| Repeat use & measured outcomes | Not started | 0% |
| Reproducible research features | Partial | 25% |
| Independent technical validation | Not started | 0% |
| Publication-ready evidence | Not started | 0% |

**Milestone 3 aggregate: ~5%**

---

## Track C — Company (Continuous)

### Foundation — Public Clarity & Operating Cadence

| Item | Status | % | Notes |
|------|--------|---|-------|
| Honest landing page | Partial | 70% | `/` exists; waitlist broken |
| Product documentation | Partial | 65% | `docs/api.md`, milestone docs |
| Demos / screenshots | Partial | 50% | Shell demos; no screenshot CI |
| Research roadmap | Complete | 90% | `.axiom/ROADMAP.md` maintained |
| Benchmark evidence | Partial | 55% | SCEP runs; S0-E4 incomplete |
| Weekly PMO reviews | In progress | 40% | C0-PMO queued |
| AXIOM Operating System | Complete | 85% | `.axiom/*` active |

**Foundation aggregate: ~60%**

### Horizon 2 — Evidence-Led Service Learning

**Status: Architecture only (~5%)** — No validated engagements recorded in repo.

### Horizon 3 — Compounding Discovery Organization

**Status: Architecture only (~0%)** — Prize-adjacent work explicitly deferred per `PRIZE_TRACK.md`.

---

## Sprint 0 Epic Status (root `roadmap.md`)

| Epic | Acceptance | Status | Test evidence |
|------|------------|--------|---------------|
| **S0-E1** Engineering contract | Vision + ranked roadmap | ✅ Complete | Docs committed |
| **S0-E2** Runtime baseline | Python 3.10+; collection errors eliminated | ✅ Complete (core) | 182/182 core |
| **S0-E3** Verification truthfulness | No fallback labeled formal proof | ✅ Complete | `test_verification_truthfulness.py` |
| **S0-E4** EPIC-002 gate | Scores include evidence state, benchmark count, limitations | ⏳ **Open** | No `evidence_state` in eval API |

---

## EPIC Status

| Epic | Description | Status | % |
|------|-------------|--------|---|
| **EPIC-001** | Mathematical Intelligence Platform (MIP) | Partial | 55% |
| **EPIC-002** | Scientific Capability Evaluation (SCEP) | Partial | 50% |
| **EPIC-003** | (Referenced in delta reports) | Architecture | 5% |

### EPIC-001 — MIP Route Coverage

| Route group | Mounted | Tested |
|-------------|---------|--------|
| `/mip/knowledge/*` | ✅ | ✅ (mip tests) |
| `/mip/formal/*` | ✅ | Partial |
| `/mip/conjecture/*` | ✅ | Partial |
| `/mip/strategy/*` | ✅ | Partial |
| `/mip/memory/*` | ✅ | Partial |
| `/mip/verify/claim` | ✅ | Partial |

### EPIC-002 — SCEP Coverage

| Component | Status |
|-----------|--------|
| 8-dimension benchmark suites | ✅ Implemented |
| `POST /eval/run` | ✅ Runs all suites, persists |
| `GET /eval/scores` | ⚠️ Hardcoded fallback when DB empty |
| `GET /eval/prize-readiness` | ✅ Computes from scores |
| Evidence state on all responses | ❌ S0-E4 not met |
| Stated limitations on scores | ❌ S0-E4 not met |

### MDE — Parallel Discovery Track

| Expected route (e2e) | Production (`mde.py`) |
|--------------------|----------------------|
| `GET /mde/retrieval` | ✅ |
| `POST /mde/conjectures/generate` | ❌ |
| `POST /mde/counterexample/search` | ❌ |
| `POST /mde/strategy/plan` | ❌ (exists under `/mip/strategy/plan`) |
| `GET /mde/strategy/decompose` | ❌ |
| `POST /mde/memory/snapshot` | ❌ |
| `POST /mde/verification/review` | ❌ |

**MDE roadmap completion: ~25%** (retrieval only)

---

## Task Queue Alignment

| Rank | ID | Task | Queue status | Repo reality |
|------|-----|------|--------------|--------------|
| 1 | S0-E2 | Runtime baseline | Complete | ✅ Matches |
| 2 | P0-WEB | Landing page | In progress | Partial — waitlist gap |
| 3 | R0-PLAN | Research plan | In progress | Docs exist; no formal artifact |
| 4 | C0-PMO | PMO cadence | In progress | AOS active |
| 5 | S0-E3 | Verification audit | Complete | ✅ Matches |
| 6 | **S0-E4** | EPIC-002 gate | **Ready — highest priority** | ❌ Not complete |
| 7 | H1-OBS | Provenance | Deferred (deps: S0-E4) | Not started |

**Note:** `.axiom/CURRENT_STATE.md` lists H1-OBS as highest priority; `TASK_QUEUE.md` correctly sequences it after S0-E4. Checkpoint reconciles: **execute S0-E4 first**.

---

## UI Surface Map

| Route | Purpose | Status |
|-------|---------|--------|
| `/` | Landing | Partial |
| `/login` | Auth | Complete |
| `/research` | Research Workspace | Complete (P0 gaps) |
| `/research/runs` | Research Loop monitor | Complete |
| `/workspace` | Graph canvas | Architecture (disconnected) |

**UI roadmap completion: ~55%** of planned researcher-facing surfaces.

---

## Release History

| Version / Tag | Milestone | Date |
|---------------|-----------|------|
| `v0.3.0-research-loop` | M005 Autonomous Research Loop v1 | 2026-08-06 |
| (prior) | EM-001 + MVP-0 | 2026-08-06 |

---

## Roadmap Velocity Summary

```
Sprint 0 baseline     [███████████████░░░░░] 75%
Product wedge (M1)    [██████████████░░░░░░] 72%
Research loop (M005)  [█████████████████░░░] 85% (v1 spec)
Platform (MIP+MDE+SCEP)[█████████░░░░░░░░░░░] 45%
Public alpha (M2)     [██░░░░░░░░░░░░░░░░░░] 10%
Company foundation    [████████████░░░░░░░░] 60%
```

---

## Single Recommended Next Milestone

**→ S0-E4: EPIC-002 Integration Gate**

See `MASTER_PROGRESS.md` for full rationale. This is the highest-ranked *unblocked engineering task* with clear acceptance criteria and direct dependency for H1-OBS, lab pilots, and honest capability reporting.

**Sequence after S0-E4:**

1. H1-OBS — provenance records  
2. MVP P0 #1 — per-user data isolation  
3. MVP P0 #5 — production LLM configuration path  
4. MDE route alignment (close 26 e2e failures) OR closed beta with disclosed limitations

---

*Roadmap status frozen at engineering checkpoint — no capability changes during this audit.*
