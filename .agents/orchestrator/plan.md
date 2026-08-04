# High-Level Orchestration Plan for AXIOM

## Objectives
Deliver AXIOM (AI Scientific Discovery Platform) fulfilling all requirements:
- R1. Epistemic Ingest & Parser (EIE): arXiv LaTeX ingestion, math environments, citation extraction -> JSON graph format (>95% extraction rate).
- R2. Logical Reasoning & Proof Exporter (LRK): Translate LaTeX claims into compilable Lean 4 theorem declarations (0 syntax errors).
- R3. Verification & SMT Gateway (AVT): Z3/SMT counterexample sweeps (<60s detection), local Lean 4 compiler proof checking.
- R4. Graph Store & Storage (EGS): SQLite graph database storing entities, dependency edges, circular reference checks.
- R5. Autonomous Discovery Loop & MCTS Proof Search (DRSP): MCTS exploring Lean proof tactics to auto-generate valid proofs for simple algebra lemmas.
- R6. Spatial Canvas Dashboard (UI): Next.js/React spatial canvas visualizing graph, nodes, citations, verification statuses.

## Phases
1. **Phase 0: Survey & Infrastructure Setup**
   - 3 Explorers map codebase, existing tools/dependencies, environment state.
   - Project Orchestrator creates `PROJECT.md` and `TEST_INFRA.md`.
2. **Phase 1: Dual Track Launch**
   - E2E Testing Orchestrator builds 4-tier requirement-driven opaque-box test suite (`TEST_READY.md`).
   - Implementation Sub-orchestrators execute milestone implementation loops.
3. **Phase 2: Milestone Iterations & Gating**
   - Explorer -> Worker -> Reviewer -> Challenger -> Auditor per milestone.
4. **Phase 3: Integration & Tier 5 Adversarial Testing**
   - End-to-end integration verification (Tiers 1-4 passing 100%).
   - Tier 5 white-box adversarial testing (Challenger-driven gap analysis).
5. **Phase 4: Completion Attestation**
   - Final audit and handoff to Sentinel.
