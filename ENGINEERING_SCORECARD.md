# AXIOM Engineering Scorecard

**Checkpoint date:** 2026-08-06  
**Version:** `0.3.0` / tag `v0.3.0-research-loop`  
**Method:** Evidence-based scoring from code, tests, docs, and operational artifacts. Scores are 0–100 unless noted.

---

## Overall Scores

| Category | Score | Grade | Trend |
|----------|-------|-------|-------|
| **Overall platform maturity** | **46** | D+ | ↑ (M005 shipped) |
| **Production readiness** | **32** | F | → (P0 blockers unchanged) |
| **Research workspace product** | **72** | C+ | ↑ (MVP-0) |
| **Autonomous research loop (v1)** | **85** | B | ↑ (new) |
| **Scientific / AI depth** | **28** | F | → (heuristic) |
| **Engineering discipline** | **78** | C+ | ↑ (S0-E2/E3) |

**Weighted composite: 46/100**

---

## Dimension Scorecard

### Infrastructure — 38/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| CI pipeline | 75 | 100 | Lint + core tests on push; no e2e |
| CD pipeline | 55 | 100 | API image to GHCR; no UI CD |
| Containerization | 45 | 100 | API Dockerfile ✅; `ui/Dockerfile` ❌ |
| Docker Compose full stack | 30 | 100 | Grafana provisioning path missing |
| Secrets management | 25 | 100 | Default JWT secret; no prod enforcement |
| Multi-tenancy | 10 | 100 | Shared SQLite store |
| Observability | 50 | 100 | Prometheus + structured logs; Grafana incomplete |
| Database migrations | 65 | 100 | Research + loop migrations exist |

**Top gaps:** tenancy, UI container, Grafana provisioning, prod secrets

---

### UI — 58/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Research Workspace UX | 75 | 100 | Auth guard, loading, empty states |
| Research Loop UI | 70 | 100 | `/research/runs` functional; polling only |
| Landing page | 55 | 100 | Responsive; waitlist broken |
| Auth UI | 70 | 100 | Register/login; no reset |
| Accessibility | 65 | 100 | aria-live, labels (MVP-0) |
| Mobile responsive | 60 | 100 | Sidebar grid |
| Graph workspace | 25 | 100 | Exists but disconnected |
| UI test coverage | 0 | 100 | No component/e2e UI tests |

**Pages shipped:** 5 (`/`, `/login`, `/research`, `/research/runs`, `/workspace`)

---

### Backend — 62/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| API Gateway structure | 80 | 100 | FastAPI, routers modular |
| Research API | 85 | 100 | Full CRUD + Q&A + sessions |
| Auth API | 60 | 100 | JWT works; no isolation |
| Research Loop API | 85 | 100 | Full lifecycle + benchmarks |
| MIP API | 70 | 100 | Broad surface; simulation fallbacks |
| MDE API | 20 | 100 | 1 of ~7 expected routes |
| Eval API | 55 | 100 | Runs work; fallback scores ungated |
| Workflow API | 50 | 100 | Mounted; no auth; no tests |
| Input validation | 75 | 100 | Pydantic models throughout |
| Error handling | 65 | 100 | HTTP exceptions; inconsistent depth |

**Python modules:** 110 files in `axiom/`  
**API route files:** 7 routers mounted in `main.py`

---

### AI Functionality — 25/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Model gateway | 40 | 100 | `ModelClient` with cache + mock fallback |
| Research Q&A | 45 | 100 | Works with mock; optional real LLM |
| Summarization | 40 | 100 | Heuristic via mock |
| Research loop intelligence | 15 | 100 | Keyword templates, not LLM |
| Hypothesis / MCTS engines | 35 | 100 | Code exists; not in loop |
| Semantic search | 0 | 100 | FTS only |
| RAG / citations | 10 | 100 | No embedding index |
| Benchmark AI quality | 20 | 100 | Keyword scoring |
| Formal reasoning integration | 45 | 100 | SMT in verifier worker |

**Critical path:** Wire `ModelClient` to loop workers; add embeddings for search.

---

### Testing — 68/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Core unit/integration | 90 | 100 | **182/182** pass |
| E2E platform tests | 55 | 100 | **200/226** pass (88%) |
| Coverage gate | 70 | 100 | CI `--cov-fail-under=50` |
| Verification regression | 95 | 100 | S0-E3 tests |
| Research workspace tests | 85 | 100 | Dedicated test file |
| Research loop tests | 85 | 100 | 16 tests |
| Workflow tests | 0 | 100 | None |
| S0-E4 acceptance tests | 0 | 100 | Not written |
| UI tests | 0 | 100 | None |
| Load / chaos tests | 0 | 100 | None |

**Test files:** 21 (17 core + 4 e2e modules)

```
Pass rate summary:
  Core:  100.0%  (182/182)
  E2E:    88.5%  (200/226)
  Combined (all): 89.4%  (382/408)
```

---

### Deployment — 35/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| API Docker image | 80 | 100 | Multi-stage, non-root user |
| UI Docker image | 0 | 100 | Missing `ui/Dockerfile` |
| Compose orchestration | 40 | 100 | API + UI + Prometheus + Grafana declared |
| CD to registry | 70 | 100 | GHCR on main/tags |
| Production docs | 15 | 100 | Local demo only |
| Environment matrix | 30 | 100 | `.env` example; no staging guide |
| Health checks | 75 | 100 | API healthcheck in compose |
| TLS / reverse proxy | 0 | 100 | Not documented |

---

### Documentation — 74/100

| Criterion | Score | Max | Notes |
|-----------|-------|-----|-------|
| Operating system (`.axiom/`) | 90 | 100 | Constitution, state, queue, roadmap |
| Engineering contract | 85 | 100 | `ENGINEERING.md`, `ARCHITECTURE.md` |
| API documentation | 70 | 100 | `docs/api.md`; MDE gap not documented |
| Milestone documentation | 85 | 100 | `MILESTONE_005.md`, `MVP_READINESS.md` |
| Demo scripts | 90 | 100 | MVP + research loop |
| User onboarding | 40 | 100 | No researcher quickstart |
| Deployment guide | 20 | 100 | Missing |
| Architecture freshness | 60 | 100 | Stale Python 3.9 blocker note |

---

## Milestone Scorecard

| Milestone | Spec completeness | Quality | Shippable | Overall |
|-----------|-------------------|---------|-----------|---------|
| S0-E1 Contract | 100% | A | ✅ | **A** |
| S0-E2 Baseline | 95% | A- | ✅ | **A-** |
| S0-E3 Truthfulness | 100% | A | ✅ | **A** |
| S0-E4 EPIC-002 gate | 40% | D | ❌ | **F** |
| EM-001 Workspace | 85% | B+ | ✅* | **B** |
| MVP-0 Stabilization | 90% | B+ | ✅* | **B+** |
| M005 Research Loop v1 | 85% | B | ✅ | **B** |
| M2 Public alpha | 10% | — | ❌ | **F** |
| MDE full surface | 25% | D | ❌ | **D-** |

*\* Shippable for trusted internal use with documented P0 limitations*

---

## Security Scorecard — 28/100

| Control | Status |
|---------|--------|
| Authentication | ⚠️ JWT + static token |
| Authorization | ❌ No per-resource ownership |
| Secret management | ❌ Default secrets |
| HTTPS | ❌ Not configured |
| Rate limiting | ❌ Missing on auth |
| Input sanitization | ✅ Pydantic validation |
| Non-root container | ✅ API Dockerfile |
| Dependency scanning | ⚠️ `security.yml` exists; coverage unknown |
| Audit logging | ⚠️ Structured logs; no audit trail |
| Data export/deletion | ❌ Missing |

---

## Integrity & Honesty Scorecard — 82/100

| Control | Status |
|---------|--------|
| Verification truthfulness (S0-E3) | ✅ Strong |
| Claim status in research loop | ✅ `ClaimStatus` enum |
| MVP readiness honest P0 list | ✅ `MVP_READINESS.md` |
| M005 limitation disclosure | ✅ `docs/MILESTONE_005.md` |
| Eval score evidence gate (S0-E4) | ❌ Open |
| Prize readiness non-claims | ✅ `PRIZE_TRACK.md` |
| Capability maturity model | ✅ `.axiom/CAPABILITIES.md` |

**Risk:** `/eval/scores` hardcoded fallback could be misread as measured capability.

---

## Stage Gate Readiness

| Gate | Readiness % | Score | Blocker count |
|------|-------------|-------|---------------|
| Internal demo | 90% | **A-** | 0 critical |
| Closed beta (min) | 45% | **D** | 3 (secrets, HTTPS, disclosure) |
| Public alpha | 25% | **F** | 5 P0 |
| First paying customer | 12% | **F** | 10+ |
| Research lab pilot | 40% | **D** | S0-E4, H1-OBS, packaging |
| Autonomous research demo | 30% | **F** | LLM, provenance, scoring |

---

## Risk Heatmap

| Risk | Likelihood | Impact | Severity |
|------|------------|--------|----------|
| Cross-user data leak | High | Critical | 🔴 |
| Overstated AI capability in demos | High | High | 🔴 |
| Ungated eval scores | Medium | High | 🟠 |
| MDE/e2e divergence | High | Medium | 🟠 |
| Mock LLM user disappointment | High | Medium | 🟠 |
| SQLite scale limits | Medium | Medium | 🟡 |
| Broken waitlist trust | Medium | Low | 🟡 |

---

## Time Estimates

| Milestone / Gate | Weeks | Confidence |
|------------------|-------|------------|
| S0-E4 complete | 1–2 | High |
| H1-OBS provenance | 2–3 | Medium |
| Closed beta (minimum) | 2–3 | Medium |
| Public alpha (all P0) | 4–6 | Medium |
| Autonomous research demo (credible) | 6–10 | Low |
| E2E suite green (MDE routes) | 3–5 | Medium |
| Full platform (roadmap M3) | 26–52 | Low |

---

## Recommended Next Milestone

### **S0-E4 — EPIC-002 Integration Gate**

| Factor | Assessment |
|--------|------------|
| Queue priority | Rank 6 — "Ready — highest priority" |
| Dependency unlock | Blocks H1-OBS, honest pilots |
| Effort | Small (1–2 weeks) |
| Risk reduction | High (integrity) |
| Feature freeze alignment | ✅ Engineering baseline, not new capability |

**Acceptance tests to add:**
- `/eval/scores` includes `evidence_state`, `benchmark_count`, `limitations`
- Hardcoded fallback labeled `estimated` with explicit limitations
- Regression: no score presented as measured without benchmark evidence

---

## Score History (checkpoint baseline)

| Date | Core tests | Version | Composite |
|------|------------|---------|-----------|
| 2026-08-05 | 134 | pre-MVP | ~38 |
| 2026-08-06 AM | 166 | MVP-0 | ~42 |
| 2026-08-06 PM | **182** | **0.3.0-research-loop** | **46** |

*Next checkpoint should re-score after S0-E4; expect integrity score → 90+, composite → 50+.*

---

*Scorecard generated at engineering checkpoint. Scores reflect repository evidence, not aspirations.*
