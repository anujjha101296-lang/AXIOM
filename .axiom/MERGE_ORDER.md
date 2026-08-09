# Draft PR Merge Order

**Purpose:** Land built capabilities onto GitHub `main`.  
**Decision (2026-08-09):** Use **tip integration**, not bottom-up merges.

## Chosen path

Merge PR from branch `cursor/integrate-mainline-dc7e` into `main`.

That tip already contains:

- Fast-forward of `cursor/vfactory-verification-dc7e` (research stack #17–#26 lineage)
- Merge of `cursor/axiom-master-os-dc7e` (MASTER-OS + P0-WEB + MVP-AUTH)

## Superseded after land

Close as superseded once integrate PR merges: #17–#27 (and older overlapping drafts #1–#16 as applicable).

## Rejected alternative

Bottom-up merge of #17→#26 sequentially — higher cost, same end state, more conflict churn.

## Agent rule

Do not open new research-loop feature PRs. Improve the integration tip / `main` only.
