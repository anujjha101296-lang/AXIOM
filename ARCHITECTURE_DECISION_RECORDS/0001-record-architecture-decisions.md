# ADR-0001: Record Architecture Decisions

**Status:** Accepted  
**Date:** 2026-08-06

## Context

AXIOM is a multi-subsystem research platform. Contributors need to understand why key choices were made without relying on chat history or tribal knowledge.

## Decision

We will use Architecture Decision Records (ADRs) stored in `docs/adr/`, indexed by `docs/adr/README.md`.

Each ADR is a short markdown file with context, decision, and consequences. ADRs are immutable once accepted; supersede with a new ADR rather than editing history.

## Consequences

- **Positive:** Faster onboarding; design rationale is searchable in git
- **Positive:** PRs that change architecture can reference or add ADRs
- **Negative:** Small overhead to write ADRs for significant changes
- **Neutral:** ADRs complement but do not replace `ARCHITECTURE.md` and `.axiom/ENGINEERING.md`
