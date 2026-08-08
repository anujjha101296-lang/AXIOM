# Technical Debt Register

**Last updated:** 2026-08-08

Honest inventory of known debt. P0 items block trust or builds; P1 items reduce velocity; P2 items are cleanup.

| ID | Priority | Area | Description | Mitigation |
|----|----------|------|-------------|------------|
| TD-001 | P1 | E2E | 26 e2e failures — MDE API surface gap vs test expectations | Align MDE routes or update e2e suite |
| TD-002 | P1 | Verification | Proof verification benchmarks use simulated Lean4 path | Integrate real Lean4/Coq when toolchain available |
| TD-003 | P2 | Docs | Thousands of `docs/capability_delta_*.md` artifacts from eval runs | Gitignore or archive; milestone deltas only |
| TD-004 | P1 | Provenance | RVP provenance hooks reserved; RVP not on main | Integrate when RVP merges |
| TD-005 | P1 | Kernel | Research Kernel on feature branch `cursor/research-kernel-dc7e` | Merge PR #15 after integration review |
| TD-006 | P2 | Landing | Public landing page still in progress (`P0-WEB`) | Complete honest capability disclosure |
| TD-007 | P2 | CI | Full suite 334/360 — e2e excluded from core gate | Document and track e2e repair separately |

## Review cadence

Weekly during Layer 2 engineering loop. Update when debt is paid or new debt is introduced.
