# Prioritized Task Queue

Read `CONSTITUTION.md`, `MASTER_DIRECTIVE.md`, `../AXIOM_STATE.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`.

Agents select the **first unblocked** task and continue without waiting for “next”.

## Ranking method

P0 safety / integrity / false-claim / supported-build failures always win. Otherwise score by impact, dependency unlock, scientific value, engineering value, prize-readiness, confidence, reversibility, effort (`DECISION_FRAMEWORK.md`). Prefer work that lands on GitHub `main` and advances the YC-ready MVP.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | MASTER-OS | Install AXIOM-MASTER-001; wire AGENTS/CONSTITUTION; create AXIOM_STATE | — | Directive readable; sessions start with continuous loop | **Complete** |
| 2 | LAND-1 | Land P0-WEB + Master OS on `main`; document merge order for research stack | MASTER-OS | Honest `/` on mainline path; merge order published | **Partial** — on branch; awaiting merge to main |
| 3 | FOUNDER-MERGE | Authorize bottom-up merge of draft PRs #17→#26 (or squash tip) | LAND-1 | `main` contains research loops or explicit decline | **Founder gate** |
| 4 | MVP-AUTH | Real user signup/login + session for research workspace | LAND-1 | User can create account and own projects | **Partial** — signup/login/JWT done; project ownership isolation next |
| 5 | MVP-EVIDENCE | Show evidence/citations in research Q&A UI (no fake sources) | MVP-AUTH or workspace | Answers display provenance when available | Ready |
| 6 | S0-E4 | EPIC-002 evidence gate integration | S0-E3 | Evidence state on eval APIs documented + tested | Ready on main; also on draft stacks |
| 7 | R0-PLAN | Researcher workflow + benchmark program + monthly evidence review | Existing evidence | Plan names measurement and non-claims | In progress |
| 8 | C0-PMO | Daily/weekly PMO cadence | AOS | Operating answers for priorities/blockers | In progress |
| 9 | GCP-2 | First Tier 1 campaign | Research stack on main + Layer 1 approval | Bounded campaign journal | **Founder gate** |

## Historical (complete on main or prior)

| ID | Status |
|----|--------|
| S0-E2 | Complete (core) |
| S0-E3 | Complete |
| EM-001 | Complete on main |
| P0-WEB | **Complete** on this branch / draft #27 — land via merge to main |

## Queue protocol

Select the first unblocked task. If blocked, record the blocker in `CURRENT_STATE.md` / `AXIOM_STATE.md`, choose the next independent safe task, and preserve rank. Do not open new speculative research-loop PRs while LAND-1 / FOUNDER-MERGE are unresolved.
