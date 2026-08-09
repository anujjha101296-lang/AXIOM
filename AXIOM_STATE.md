# AXIOM State

**Last updated:** 2026-08-09  
**Directive:** AXIOM-MASTER-001 installed  
**Source branch for this snapshot:** `cursor/axiom-master-os-dc7e` (based on `main`)  
**`main` tip (verified):** `3431a65` — CI venv fix + Research Workspace on main

## One-line status

AXIOM has a **working research workspace on `main`**, an **honest landing page on a draft PR**, and a **large unmerged research-loop stack** (25+ draft PRs). The #1 organizational failure mode is **capability not landing on GitHub `main`**.

## What works (on `main` today)

| Capability | Evidence | Notes |
|------------|----------|-------|
| Research Workspace API `/research/*` | EM-001 on main | Projects, PDF upload, notes, FTS, Q&A, sessions |
| Research Workspace UI `/research` | `ui/src/app/research/` | Usable; LLM falls back to mock without keys |
| Graph Workspace UI `/workspace` | Prototype | Developer demo; hardcoded patterns |
| API Gateway `/health`, `/ready` | Core tests | Bearer token auth for many routes |
| Epistemic Graph Store | Knowledge graph + migrations | Core MIP path |
| Verification truthfulness (S0-E3) | Truthfulness module | Fallbacks cannot claim formal proof |
| Core pytest suite | CI on main | E2E suite historically flaky / excluded in later branches |

## What does not work / is incomplete on `main`

| Gap | Severity | Notes |
|-----|----------|-------|
| Research loops (E&R, SIMR, FMTP, SEC, FRCE, SKAI) | High | Implemented on draft PRs — **not on main** |
| Honest landing page (P0-WEB) | High (product) | Draft PR #27 — not on main |
| Verification Factory | Medium | Draft PR #26 — not on main |
| Signup / org / multi-tenant SaaS | High (YC MVP) | No real user accounts on main |
| Public waitlist / billing | Low (deferred) | Correctly not faked |
| Campaign / evidence / formal UIs | Medium | API-only on unmerged branches |
| Full E2E browser suite in CI | Medium | Harness debt |

## What is mocked / labeled

- LLM Q&A without API keys → mock responses
- Lean compilation without Lean installed → simulated / partial formalization
- Landing metrics prior to P0-WEB → **fake** (fixed on PR #27)

## Production-ready?

**No.** Local/dev deployable research workspace only. No production multi-tenant SaaS, no verified public deployment claim.

## Current MVP (honest)

```text
Open /research → create project → upload PDF → notes → search → Q&A (mock or live LLM)
```

Missing for YC-ready MVP: honest public entry (P0-WEB), real accounts/onboarding, evidence-visible answers, one end-to-end “research investigation” that is not mock theater.

## Deployed?

Not claimed. Local Docker/dev only unless founder has separately deployed.

## Tested?

Core suite on main: historically green for workspace + verification paths. Unmerged branches report ~280+ core tests — **not verified on main until merged**.

## Open PR stack (critical)

Draft PRs exist in dependency order (approximate):

```text
main
  ← OS/GCP/CEL (#17) ← TSS (#18) ← E&R (#19) ← SIMR (#20) ← FMTP (#21)
  ← SEC (#22) ← FRCE (#23) ← SKAI (#24) ← MASTER audit (#25)
  ← VFACTORY (#26)
P0-WEB (#27) — independent of research loops; can merge anytime
```

**Failure mode:** agents keep shipping new draft PRs while `main` stagnates.

## Blockers

1. **FOUNDER GATE:** Authorize merge strategy for the research-loop PR stack (bottom-up merge, or designate a single integration tip to squash).
2. No production secrets / hosting decision (founder gate for deploy).

## Next highest-value initiative

**LAND-1 — Land product + OS on `main`, then consolidate the research stack.**

Immediate autonomous work (no founder gate):

1. Install Master Directive (this cycle) ✅
2. Land P0-WEB honest landing onto the merge path
3. Prepare explicit merge order + stop creating parallel orphan feature PRs

Requires founder:

- Approve merging draft PR chain onto `main` (or authorize one squash integration branch)

## Why this is next

Under MASTER_DIRECTIVE product-first + “GitHub is source of truth”: unmerged work has near-zero company value. A usable MVP on `main` beats another unmerged research loop.

## Current commit

Recorded at end of this cycle in the PR / cycle report.
