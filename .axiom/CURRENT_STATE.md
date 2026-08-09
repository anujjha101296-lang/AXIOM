# Current State

Read `CONSTITUTION.md`, `MASTER_DIRECTIVE.md`, `OPERATING_SYSTEM.md`, `../AXIOM_STATE.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first.

**Last updated:** 2026-08-09 (integrate-mainline: research tip + MASTER-OS + P0-WEB + MVP-AUTH)  
**Active horizon:** Continuous execution under Master Directive — land integrated tip on `main`

## Where we are today

This integration branch combines:

1. Full research-loop stack (VFACTORY tip: OS → TSS → E&R → SIMR → FMTP → SEC → FRCE → SKAI → MASTER → VFACTORY)
2. AXIOM-MASTER-001 continuous operating law
3. Honest public landing (P0-WEB)
4. MVP signup/login JWT (MVP-AUTH partial)

AXIOM operates as a self-improving research organization. Prompts do not advance the mission; evidence, benchmarks, and state updates do.

## Operating system

| Layer | Artifact |
|------:|----------|
| Master execution law | `.axiom/MASTER_DIRECTIVE.md` |
| Continuous Evolution Loop | `.axiom/OPERATING_SYSTEM.md` |
| Honest snapshot | `AXIOM_STATE.md` |
| Daily queue | `.axiom/TASK_QUEUE.md` |

## Completed (on this integration tip)

- Research Workspace EM-001, S0-E2/E3/E4, GCP, CEL, H1-OBS
- TSS, E&R, SIMR, FMTP, SEC, FRCE, SKAI, MASTER audit, VFACTORY
- **AXIOM-MASTER-001** continuous directive
- **P0-WEB** honest landing
- **MVP-AUTH (partial)** signup/login/JWT; projects not yet owner-scoped

## Blocked / founder gates

- **Merge this integration PR to `main`** (chosen strategy: tip integration, not bottom-up)
- **GCP-2** Tier 1 campaign — Layer 1 strategic approval
- Public deploy / publication

## Highest priority (autonomous after land)

1. Verify core tests + key health gates on this tip
2. Merge to `main` (founder: merge the PR)
3. **MVP-AUTH continue** — project ownership isolation
4. **MVP-EVIDENCE** — citations in research Q&A UI

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
