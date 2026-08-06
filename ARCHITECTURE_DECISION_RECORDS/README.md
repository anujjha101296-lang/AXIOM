# Architecture Decision Records (ADR)

This directory records important design decisions for AXIOM. ADRs help contributors understand **why** the codebase is shaped the way it is.

## Format

Each ADR follows [Michael Nygard's template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions):

- **Status** — Proposed | Accepted | Deprecated | Superseded
- **Context** — What forces are at play?
- **Decision** — What did we decide?
- **Consequences** — What becomes easier or harder?

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-python-310-runtime-baseline.md) | Python 3.10+ runtime baseline | Accepted |
| [0003](0003-demo-vs-research-modes.md) | Demo Mode vs Research Mode | Accepted |
| [0004](0004-verification-truthfulness.md) | Verification truthfulness labeling | Accepted |
| [0005](0005-sqlite-persistence-strategy.md) | SQLite persistence strategy | Accepted |

## When to Write an ADR

Create a new ADR when a decision:

- Affects multiple modules or teams
- Is hard to reverse (auth, data model, verification tiers)
- Has significant trade-offs worth documenting
- Would confuse a new contributor without context

Number sequentially: `0006-short-title.md`. Submit with your PR.
