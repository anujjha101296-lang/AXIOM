# Research Memory

## Campaign memory (per iteration)

After each cycle, FRCE records:
- What was learned
- What failed
- Assumptions that changed
- Exhausted vs promising approaches
- New questions
- Tools that worked / models that failed
- What AXIOM should never repeat

## Global memory compounding

When a campaign ends (abandon, complete, or compound explicitly):
- Useful results flow to `frce_global_memory` table
- Provenance preserved: `provenance_note: "Derived from campaign memory; not established fact"`
- Future campaigns can query `/frce/global-memory`

## Knowledge graph integration

Campaign evidence links to E&R claims with `campaign_id`.
EGS knowledge graph remains parallel — campaign memory does not auto-promote to established facts.

## Institutional scientific memory

This is where AXIOM develops organizational learning across campaigns.
Campaign B can benefit from Campaign A without conflating speculative ideas with verified knowledge.
