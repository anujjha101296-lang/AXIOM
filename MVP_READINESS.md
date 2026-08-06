# MVP-0 Readiness Report

**Date:** 2026-08-06  
**Sprint:** MVP-0 Stabilization (feature freeze)  
**Scope:** Research Workspace end-to-end workflow for a first-time researcher

---

## Validation Summary

The complete researcher workflow was validated via automated tests and a CLI demo (`scripts/demo_mvp_workflow.sh`):

| Step | Status | Notes |
|------|--------|-------|
| Register | **Pass** | `POST /auth/register` — new UI at `/login` |
| Login | **Pass** | `POST /auth/login` — JWT stored in `localStorage` |
| Create Project | **Pass** | API + UI |
| Upload PDF | **Pass** | Text extracted on upload; char count surfaced in UI |
| Extract Text | **Pass** | Automatic via `pypdf`; shown as char count |
| Generate Summary | **Pass** | Heuristic summarizer (mock model gateway) |
| Create Notes | **Pass** | Tags, CRUD, linked to documents |
| Search | **Pass** | Full-text (FTS5 keyword), not vector semantic |
| Ask Questions | **Pass** | Saved conversations; requires uploaded PDF |
| Resume Session | **Pass** | Session + active conversation restored |

**Test evidence:** `166/166` core tests pass (`pytest tests/ --ignore=tests/e2e`).  
**Demo evidence:** `bash scripts/demo_mvp_workflow.sh` completes all 10 steps.

---

## Fixes Applied in MVP-0

### Authentication
- Added `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- JWT bearer tokens accepted on all protected endpoints (alongside static dev token)
- Fixed `AXIOM_API_TOKEN` env var not mapping to `settings.api_token` (auth silently ignored `.env` token)

### UI / UX
- New `/login` page with register/sign-in toggle
- Research workspace requires authentication; redirects to `/login` when unauthenticated
- Token + user profile persisted in `localStorage`
- Sign-out flow; user name shown in header
- Loading overlay, dismissible status toasts, empty states for projects/documents/notes/search
- API errors parsed from JSON `detail` field (no raw response dumps)
- Accessibility: `aria-live`, `aria-busy`, `aria-label`, section headings, keyboard search
- Mobile-responsive sidebar grid
- Landing page CTA routes to `/login`

### Documentation
- `docs/api.md` — Authentication section added
- `scripts/demo_mvp_workflow.sh` — full workflow demo including register/login

---

## Remaining Blockers Before Public Alpha

### P0 — Must fix before any external users

| # | Blocker | Impact |
|---|---------|--------|
| 1 | **No per-user data isolation** | All registered users share the same research project store. User A can see User B's projects. |
| 2 | **Default JWT secret in production** | `JWT_SECRET_KEY` must be set to a cryptographically random value; startup should fail if default is used in `production` environment. |
| 3 | **No HTTPS/TLS termination** | Credentials and tokens transmitted in cleartext without a reverse proxy. |
| 4 | **No password reset or email verification** | Users cannot recover accounts; registration accepts any email without confirmation. |
| 5 | **Q&A and summaries use mock model responses** | `ModelClient` returns heuristic text unless a real LLM API key is configured. Answers are not grounded in a production model. |

### P1 — High priority for daily researcher use

| # | Blocker | Impact |
|---|---------|--------|
| 6 | **Search is keyword FTS, not semantic** | User expectation of "semantic search" is not met; only SQLite FTS5 Porter stemming. |
| 7 | **Scanned/image-only PDFs rejected** | Common in legacy paper archives; no OCR pipeline. |
| 8 | **No document text preview in UI** | Extracted text is stored but not viewable in the UI (only char count). |
| 9 | **No rate limiting on auth endpoints** | Vulnerable to brute-force and registration spam. |
| 10 | **Waitlist form on landing page is non-functional** | Submit does nothing; damages trust for early-access signups. |
| 11 | **Graph workspace (`/workspace`) disconnected from research workspace** | Two separate UIs with no shared project context. |

### P2 — Important but deferrable for closed alpha

| # | Blocker | Impact |
|---|---------|--------|
| 12 | **26 e2e test failures** | MDE API surface gap (`tests/e2e`); does not block research workspace but indicates platform instability elsewhere. |
| 13 | **No account deletion or data export** | GDPR/privacy compliance gap. |
| 14 | **No collaborative sharing** | Single-user projects only. |
| 15 | **No file upload progress indicator** | Large PDFs appear frozen during upload. |
| 16 | **Session JWT expires after 60 minutes** | No refresh token; user must re-login with no warning. |
| 17 | **Production deployment not documented** | No Docker compose or hosted deployment guide for researchers. |

---

## Recommended Alpha Gate

Public alpha is **not recommended** until P0 items 1–5 are resolved. A **closed alpha** with trusted researchers is feasible after P0 #2 (secrets) and P0 #3 (HTTPS) if P0 #1 (data isolation) is explicitly disclosed as a known limitation.

---

## How to Run the MVP Demo

```bash
# Terminal 1 — API
AXIOM_API_TOKEN=axiom-dev-token python3 -m uvicorn axiom.services.api_gateway.main:app --port 8000

# Terminal 2 — UI
cd ui && npm install && npm run dev

# Terminal 3 — CLI workflow
bash scripts/demo_mvp_workflow.sh
```

Open `http://localhost:3000/login` to use the UI workflow.

---

## Files Changed (MVP-0)

- `axiom/services/api_gateway/auth.py` — JWT + static token; dynamic settings read
- `axiom/services/api_gateway/user_store.py` — user persistence
- `axiom/services/api_gateway/routes/auth_api.py` — register/login/me
- `axiom/config/settings.py` — `AXIOM_API_TOKEN` env alias fix
- `ui/src/app/login/page.tsx` — auth UI
- `ui/src/app/research/page.tsx` — auth guard + UX stabilization
- `ui/src/lib/api.ts` — shared API helpers
- `tests/test_mvp_auth.py` — auth test coverage
- `tests/conftest.py` — test env hardening
- `scripts/demo_mvp_workflow.sh` — complete workflow demo
- `docs/api.md` — auth documentation
