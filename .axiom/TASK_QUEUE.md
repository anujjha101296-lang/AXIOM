# Prioritized Task Queue

Read `CONSTITUTION.md`, `MASTER_DIRECTIVE.md`, `../AXIOM_STATE.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`.

Agents select the **first unblocked** task and continue without waiting for “next”.

## Ranking method

P0 safety / integrity / false-claim / supported-build failures always win. Prefer work that lands on GitHub `main` and advances the YC-ready MVP.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | INTEGRATE-1 | Tip-integrate research stack + MASTER-OS + P0-WEB + MVP-AUTH | VFACTORY tip + master-os | Single PR to main; tests green | **Ready for founder merge** |
| 2 | LAND-MAIN | Merge integration PR to `main` | INTEGRATE-1 | `main` contains research loops + product | **Founder: merge PR #29** |
| 3 | MVP-AUTH | Project ownership isolation for research workspace | Tip | Users only see own projects | **Done** |
| 4 | MVP-EVIDENCE | Show evidence/citations in research Q&A UI | MVP-AUTH | Provenance visible when available | **Done** |
| 5 | MVP-CAMPAIGN-UI | Campaign create/scope/plan/cycle UI | FRCE API | `/campaigns` wired | **Done** |
| 6 | MVP-AGENTS-UI | Agent activity visibility | MVP-CAMPAIGN-UI | User sees what/why/found/uncertain | **Done** |
| 7 | MVP-PERSIST-SMOKE | Logout/login preserves research state | Tip | `test_mvp_persistence` green + Log out UI | **Done** |
| 8 | MVP-EXPERIMENTS-UI | Experiments create/run UI | SEC API | `/experiments` wired | **Done** |
| 9 | MVP-DOCKER-SMOKE | Docker compose health on tip | Tip | `scripts/docker_smoke.sh` passes | **Done** |
| 10 | MVP-OWNER-FRCE-SEC | Per-user FRCE/SEC ownership | Tip | isolation tests green | **Done** |
| 11 | MVP-WEB-RESEARCH | Controlled internet research polish | Tip | fetch/cite/store with untrusted marking | **Next autonomous** |
| 12 | GCP-2 | First Tier 1 campaign | Stack on main + Layer 1 approval | Bounded campaign journal | **Founder gate** |

## Historical (complete on tip)

S0-E2 … VFACTORY-1, MASTER-OS, P0-WEB, MVP-AUTH, MVP-EVIDENCE, MVP-CAMPAIGN-UI, MVP-AGENTS-UI, MVP-PERSIST-SMOKE, MVP-EXPERIMENTS-UI, MVP-DOCKER-SMOKE, MVP-OWNER-FRCE-SEC, MVP journey test.

## Queue protocol

Select the first unblocked task. Do not open new research-loop feature PRs while LAND-MAIN is unresolved. Prefer improving the integration tip / main.
