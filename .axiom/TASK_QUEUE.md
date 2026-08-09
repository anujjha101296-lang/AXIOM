# Prioritized Task Queue

Read `CONSTITUTION.md`, `MASTER_DIRECTIVE.md`, `../AXIOM_STATE.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`.

Agents select the **first unblocked** task and continue without waiting for “next”.

## Ranking method

P0 safety / integrity / false-claim / supported-build failures always win. Prefer work that lands on GitHub `main` and advances the YC-ready MVP.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | INTEGRATE-1 | Tip-integrate research stack + MASTER-OS + P0-WEB + MVP-AUTH | VFACTORY tip + master-os | Single PR to main; tests green | **Ready for founder merge** |
| 2 | LAND-MAIN | Merge integration PR to `main` | INTEGRATE-1 | `main` contains research loops + product | **Founder: merge PR #29** |
| 3–10 | MVP product gaps through Docker/ownership | Tip | Evidence in gap matrix | **Done** |
| 11 | MVP-WEB-RESEARCH | Controlled internet research polish | Tip | fetch/cite/store UNTRUSTED | **Done** |
| 12 | DISCOVERY-ENGINE-0 | Scientific Discovery Engine core + benchmarks | Tip | cycle + FDR=0 + API/UI | **Done (v0.1)** |
| 13 | MVP-CI-SCEP | Fix remaining SCEP CI doc failures | Tip | CI green on required checks | **Done** |
| 14 | DISCOVERY-ENGINE-1 | External novelty search + formal bridge in cycle | DISCOVERY-ENGINE-0 | broader novelty ≠ INSUFFICIENT_SEARCH only | **Partial** |
| 15 | ARENA-0 | Research Benchmark Arena v1 (60 cases + baseline) | Tip | 60-case run + readiness + UI | **Done** |
| 16 | ARENA-1 | Long-horizon + dedicated security suite (Tier 8+) | ARENA-0 | unlock Tier 8 with measured long-horizon evidence | **Done** |
| 17 | DISCOVERY-ENGINE-1b | Broader novelty / allowlisted literature search | DISCOVERY-ENGINE-1 | novelty beyond local-only | **Queued** |
| 18 | OPLAB-0 | Open Problem Research Lab v1 | Arena+Discovery+FRCE | intake→map→strategies→campaign cycle + Level-1 | **Done** |
| 19 | OPLAB-1 | Literature enrichment + Level-2/3 staged campaigns | OPLAB-0 | SKAI+formal library maps; Level-2 run | **Partial** (L3 next) |
| 20 | OPLAB-2 | Level-3 historical conjecture reproduction | OPLAB-1 | measured stage gate + report | **Next autonomous** |
| 20 | GCP-2 | First Tier 1 campaign | Stack on main + Layer 1 approval | Bounded campaign journal | **Founder gate** |

## Historical (complete on tip)

… MVP-DOCKER-SMOKE, MVP-OWNER-FRCE-SEC, MVP-WEB-RESEARCH (`/skai/acquire-url`, `/sources`), MVP journey test.

## Queue protocol

Select the first unblocked task. Prefer improving the integration tip / main while LAND-MAIN is unresolved.
