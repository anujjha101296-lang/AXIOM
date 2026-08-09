# Prioritized Task Queue

Read `CONSTITUTION.md`, `MASTER_DIRECTIVE.md`, `../AXIOM_STATE.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`.

Agents select the **first unblocked** task and continue without waiting for “next”.

## Ranking method

P0 safety / integrity / false-claim / supported-build failures always win. Prefer work that lands on GitHub `main` and advances the YC-ready MVP.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | INTEGRATE-1 | Tip-integrate research stack + MASTER-OS + P0-WEB + MVP-AUTH | VFACTORY tip + master-os | Single PR to main; tests green | **In progress** |
| 2 | LAND-MAIN | Merge integration PR to `main` | INTEGRATE-1 | `main` contains research loops + product | **Founder: merge PR** |
| 3 | MVP-AUTH | Project ownership isolation for research workspace | LAND-MAIN or tip | Users only see own projects | **Next autonomous** |
| 4 | MVP-EVIDENCE | Show evidence/citations in research Q&A UI | MVP-AUTH | Provenance visible when available | Ready |
| 5 | R0-PLAN | Researcher workflow + benchmark program | Existing evidence | Plan names measurement and non-claims | In progress |
| 6 | C0-PMO | Daily/weekly PMO cadence | AOS | Operating answers for priorities/blockers | In progress |
| 7 | GCP-2 | First Tier 1 campaign | Stack on main + Layer 1 approval | Bounded campaign journal | **Founder gate** |

## Historical (complete on tip)

S0-E2, S0-E3, S0-E4, EM-001, GCP-1, OS-1, CEL-1, H1-OBS, TSS-1, E&R-1, SIMR-1, FMTP-1, SEC-1, FRCE-1, SKAI-1, MASTER-1, VFACTORY-1, MASTER-OS, P0-WEB, MVP-AUTH (signup/login).

## Queue protocol

Select the first unblocked task. Do not open new research-loop feature PRs while LAND-MAIN is unresolved. Prefer improving the integration tip / main.
