# Current State

Read `CONSTITUTION.md`, `MASTER_DIRECTIVE.md`, `../AXIOM_STATE.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first.

**Last updated:** 2026-08-09 (AXIOM-MASTER-001 installed)  
**Active horizon:** Continuous execution under Master Directive — YC-ready MVP + research loop

## Where we are today

AXIOM on **`main`** has a production-quality **Research Workspace** vertical slice and verification truthfulness controls. A large stack of research-loop draft PRs (TSS → E&R → … → VFACTORY) and an honest landing page (P0-WEB) exist on GitHub but are **not merged**. Organizational priority is continuous autonomous execution under `.axiom/MASTER_DIRECTIVE.md`, not isolated feature prompts.

## Completed (on `main`)

- Operating contract + AXIOM OS foundation under `.axiom/`
- **S0-E2 (core):** Test toolchain restored; core suite green historically
- **S0-E3:** Verification truthfulness audit
- **EM-001 Research Workspace:** Projects, PDFs, notes, FTS, Q&A, sessions — API + UI
- **AXIOM-MASTER-001:** Continuous execution directive installed
- **P0-WEB:** Honest public landing (capability tiers; no fake metrics / dead waitlist) — on this branch
- **MVP-AUTH (partial):** Signup/login JWT (`/auth/*`), `/login` UI, JWT accepted by research API; static token still works

## Completed (draft PRs — not on `main`)

See `AXIOM_STATE.md` open PR stack (#17–#26 research loops; #27 superseded by this branch for landing).

## Blocked / founder gates

- **Merge strategy for draft research-loop PR stack** — required so GitHub `main` reflects built capabilities
- **GCP-2 / public deploy / publication** — remain founder-gated when relevant

## Highest priority (autonomous)

**MVP-AUTH (continue):** Project ownership isolation + onboarding polish.  
**FOUNDER-MERGE:** Authorize research-loop PR stack onto `main`.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
