# AXIOM Execution Gap Matrix

**Updated:** 2026-08-09  
**Branch:** `cursor/integrate-mainline-dc7e`  
**Method:** Executable code audit + tests (not documentation)

Legend: GREEN = works with evidence · YELLOW = partial · RED = missing/broken · GRAY = deferred

| Subsystem | State | Status | Missing / broken | Priority | Blocking MVP? |
|-----------|-------|--------|------------------|----------|---------------|
| Clean build / API start | GREEN | Tests run; API importable | — | P0 | No |
| Auth signup/login JWT | GREEN | `/auth/*` + `/login` + tests | — | P0 | No |
| Project ownership | GREEN | `owner_id` + JWT isolation test | Legacy NULL rows visible to `dev` token only | P0 | No |
| Research project CRUD | GREEN | API + `/research` UI | — | P1 | No |
| PDF upload/process | GREEN | Upload + extract + summarize | Mock summary without keys | P1 | No |
| Search | GREEN | FTS + owner-scoped cross-project | — | P1 | No |
| Q&A | YELLOW | Works; citations + provider_mode | Real LLM needs API key | P1 | Soft |
| Evidence in answers | GREEN | Citations + snippet + mode in API/UI | Not yet claim-registry linked | P1 | Soft |
| Campaign API (FRCE) | GREEN | `/frce/*` + owner_id | — | P4 | No |
| Campaign UI | GREEN | `/campaigns` create→scope→plan→cycle | Agent panel included | P1 | No |
| Agent visibility UI | GREEN | Campaign dashboard what/why/found/uncertain | Live streaming later | P3 | Soft |
| Experiments API | GREEN | `/experiments/*` + owner_id | — | P5 | No |
| Experiments UI | GREEN | `/experiments` create→run→inspect | — | P5 | Soft |
| FRCE/SEC ownership | GREEN | JWT isolation tests | anonymous/dev still broad | P4 | Soft |
| Formal math | YELLOW | API + compilation gate | Lean optional; no UI | P7 | No |
| Internet research | YELLOW | arXiv ingest exists | Controlled web search limited | P2 | Later |
| Docker compose | GREEN | `scripts/docker_smoke.sh` passed (api+ui healthy) | Observability profile optional; nested overlay may need vfs | P0 | No |
| CI | YELLOW | Runs; 3 SCEP doc fails | E2E not required check | P0 | Soft |
| E2E product journey | GREEN | journey + persistence tests | Playwright still pending | P1 | Soft |

## Build order (next cycle)

1. **P2** Controlled internet research polish  
2. **P1** Playwright browser E2E (optional)  
3. **P0** Fix remaining SCEP CI doc failures  

## Explicit mocks / limitations

- LLM Q&A / summarize: mock or extractive without `OPENAI_API_KEY` / `GEMINI_API_KEY` (labeled via `provider_mode`)  
- Lean formal verification: simulated when Lean absent  
- Graph workspace: prototype, not MVP path  
- Docker smoke in nested VMs may require vfs storage driver  
