# Draft PR Merge Order

**Purpose:** Land built capabilities onto GitHub `main` without more orphan branches.  
**Created:** 2026-08-09 under AXIOM-MASTER-001  
**Founder gate:** Approve this order (or an alternate squash of a designated tip).

## Independent (merge anytime)

| Order | PR | Branch | Why safe |
|------:|----|--------|----------|
| A | #27 | `cursor/p0-web-landing-dc7e` | UI-only honest landing; no research-loop deps |

## Research / OS stack (bottom-up)

Merge **only after** CI green on each step. Do not open new parallel loop PRs until this lands.

| Order | PR | Branch | Contents (summary) |
|------:|----|--------|--------------------|
| 1 | #17 | `cursor/axiom-operating-system-dc7e` | OS v1.0, GCP, S0-E4, CEL |
| 2 | #18 | `cursor/tss-security-loop-dc7e` | TSS security loop |
| 3 | #19 | `cursor/erl-evidence-repro-dc7e` | Evidence & Reproducibility |
| 4 | #20 | `cursor/simr-model-routing-dc7e` | Model routing |
| 5 | #21 | `cursor/fmtp-formal-math-dc7e` | Formal math |
| 6 | #22 | `cursor/sec-experiment-compute-dc7e` | Experiment sandbox |
| 7 | #23 | `cursor/frce-campaign-engine-dc7e` | Campaign engine |
| 8 | #24 | `cursor/skai-knowledge-acquisition-dc7e` | Knowledge acquisition |
| 9 | #25 | `cursor/master-build-evolution-dc7e` | Capability audit + harness fixes |
| 10 | #26 | `cursor/vfactory-verification-dc7e` | Verification Factory |

## Alternate: single squash tip

If bottom-up is too costly, founder may authorize squashing the tip of `#26` (VFACTORY) onto `main` after conflict resolution and a full core-suite + health-gate run. Record the decision in `MEMORY.md`.

## Older / overlapping drafts

PRs #1–#16 and other milestone drafts may be superseded by the stack above. Close as superseded after LAND-1 rather than merging blindly.

## Agent rule

Until FOUNDER-MERGE completes: **no new research-loop feature PRs**. Only: land OS/product, fix main, MVP-AUTH, MVP-EVIDENCE, or unblock merge conflicts on the ordered stack.
