# AXIOM Product Readiness

**Verification date:** 2026-08-07  
**Audience:** Internal evaluation — Research Workspace product wedge  
**Scope:** Verified implementation only; no roadmap or planned features.

---

## Readiness Verdict

| Dimension | Score (governance) | Verified assessment |
|-----------|-------------------:|---------------------|
| **Overall product readiness** | 31/100 | **Not ready for external users** |
| API backend (headless) | — | **Ready for internal API evaluation** |
| Web UI | — | **Not shippable** (build fails) |
| Security & tenancy | 26/100 | **Not ready** |
| Documentation honesty | — | **Adequate** (limitations documented in eval/RVP) |

**Bottom line:** AXIOM has a demonstrable headless API suitable for internal technical evaluation. It is not ready as a customer-facing product without resolving UI build failure, authentication flows, and multi-tenant data isolation.

---

## Product Wedge: Research Workspace

The documented product wedge is an authenticated research workspace: projects, PDF upload, summarization, Q&A, and search.

### What works (verified)

| Capability | Evidence |
|------------|----------|
| Create/list/update projects | `POST /research/projects` → 201; 15 unit tests pass |
| Bearer-token protection | 401 without token; `test_token` works in test env |
| Full-text search endpoint | `GET /research/search` → 200 |
| Notes, conversations, sessions | Routes implemented in `research.py` |
| PDF extraction library | `PdfExtractor` tested in unit tests |

### What is blocked (verified)

| Blocker | Evidence |
|---------|----------|
| PDF-only upload gate | Text upload → 400 `"Only PDF files are supported"` |
| Q&A requires PDF | `POST .../ask` without docs → 422 |
| No login/register UI or API | `GET /auth/login` → 404 |
| No per-user isolation | Governance: shared SQLite, no `user_id` scoping |
| UI does not call API | `npm run build` fails; no fetch calls verified in pages |
| Model responses may be mock | `ModelClient` used without verified LLM config |

### Demonstration result

Internal API workflow (2026-08-07):

```
✅ POST /research/projects          → 201 Created
❌ POST .../documents/upload (.txt) → 400 PDF required
❌ POST .../ask                     → 422 No PDF uploaded
✅ GET  /research/search            → 200 (empty results)
```

Unit-test workflow (with mocked PDF extractor) passes all 15 tests including upload, summarize, and ask.

---

## Secondary Product Surfaces

### Evaluation dashboard (headless)

| Item | Status |
|------|--------|
| `GET /eval/scores` | ✅ Public, no auth — usable for internal dashboards |
| `GET /eval/prize-readiness` | ✅ Working |
| `POST /eval/run` | ✅ Triggers full benchmark suite |
| UI for scores | ❌ None verified |

**Product implication:** Eval data can power internal dashboards or CLI reports today; no end-user UI exists.

### RVP dashboard (headless)

| Item | Status |
|------|--------|
| `GET /rvp/dashboard` | ✅ After first run initializes DB |
| `POST /rvp/runs` | ✅ Stage execution |
| UI | ❌ None |

---

## Web UI Readiness

| Check | Result |
|-------|--------|
| Pages present | 3 (`/`, `/research`, `/workspace`) |
| `npm run build` | **FAILED** |
| Error | `Event handlers cannot be passed to Client Component props` on `/` |
| API integration | Not verified |
| Auth flow in UI | Not present |
| E2E browser tests | None |

**Verdict:** UI is a marketing prototype, not a functional product shell.

---

## Security & Compliance Readiness

| Control | Verified state |
|---------|----------------|
| Authentication | Static bearer token only |
| User accounts | Not implemented |
| RBAC enforcement on routes | Not implemented (helpers exist) |
| JWT production config | Default insecure secret (warning logged) |
| Data isolation | None — shared DB |
| Dependency vulnerabilities (UI) | Governance reports 0 high/critical for npm |
| HTTPS/TLS termination | Not in scope of repo verification |

**Verdict:** Suitable only for trusted internal networks with shared dev token. Not suitable for multi-user or public deployment.

---

## Operational Readiness

| Item | Verified |
|------|----------|
| Health checks | `/health`, `/ready` — 200 |
| Metrics | `/metrics` Prometheus format |
| Structured logging | Configured via settings |
| Docker Compose | Present; full stack not verified in this review |
| CI governance workflow | File exists; not re-executed |
| `make test` | 176 core tests pass |
| `make engineering-health` | Produces reports |

---

## Test Evidence for Product Claims

| Claim | Supported? | Evidence |
|-------|------------|----------|
| "Upload and analyze research PDFs" | ⚠️ API only | Unit tests with mocked PDF; HTTP requires real PDF bytes |
| "Ask questions about your papers" | ⚠️ API only | 422 without PDF; passes in unit tests |
| "Interactive knowledge graph" | ❌ | No working UI; `GET /graph` is JSON only |
| "Scientific capability benchmarks" | ✅ | EPIC-002 fully operational |
| "Research validation program" | ✅ | RVP operational, 266 problems |
| "Workflow automation" | ❌ | Not mounted |
| "User login" | ❌ | 404 |

---

## P0 Blockers for Internal Alpha

Ordered by verification severity:

1. **Fix UI production build** — `ui/src/app/page.tsx` Client Component error
2. **Expose auth endpoints or document dev-token-only access** — no `/auth/login`
3. **Wire UI to research API** — pages are static
4. **Add user_id scoping to research store** — governance-identified gap
5. **Clarify ModelClient configuration** — Q&A quality depends on backend
6. **Mount or remove workflow API references** — 404 confuses evaluators

---

## P1 Items Before External Beta

1. Per-user tenancy and data isolation
2. Production JWT secret management
3. PDF upload edge cases (large files, scanned PDFs) — untested
4. Rate limiting and brute-force protection — not present
5. Honest demo vs research mode banners in UI

---

## What Internal Evaluators Can Do Today

| Activity | How |
|----------|-----|
| Run capability benchmarks | `POST /eval/run` or `make test` + eval tests |
| Run research validation | `make research-validation` |
| Run engineering health review | `make engineering-health` |
| Exercise MIP APIs | `POST /mip/conjecture/generate`, etc. |
| Exercise research API (headless) | Bearer token + PDF upload via curl/TestClient |
| Inspect OpenAPI | `GET /docs` |
| Review governance reports | Root-level `*_HEALTH.md` files |

---

## Governance Cross-Reference

Automated product health score: **31.1/100** (`PRODUCT_HEALTH.md`, 2026-08-07)

Key governance findings aligned with this verification:

- No per-user data isolation
- MDE API surface gap drives 26 e2e failures
- Landing waitlist form non-functional (UI build failure related)
- Workspace wedge is "demo-ready" in API unit tests, not production-ready

---

*Product readiness is assessed from verified tests, API demonstrations, and UI build results only. Re-verify after any merge to `main`.*
