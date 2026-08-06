# AXIOM Labs — YC Application Draft

> Document Type: Internal preparation document
> Status: Draft

---

## Company Description (50 words)

AXIOM is the AI workspace for frontier mathematical and scientific research.
It gives researchers a verifiable, graph-based environment to connect knowledge, explore hypotheses, run formal proofs, and measure their distance from the world's hardest open problems—with every reasoning step tracked and auditable.

---

## What We Do

AXIOM is building the world's first Scientific Discovery Platform.

It is not a chatbot. It is not a literature summarizer. It is a complete research infrastructure for mathematicians and scientists who need to:

- Track hypotheses, proofs, conjectures, and counterexamples in a structured, verifiable graph
- Generate and test candidate conjectures automatically from existing knowledge
- Run formal proof verification (Lean 4, Coq, Isabelle)
- Measure their scientific capability objectively, with benchmarks that run every sprint

Our first product: the AI workspace for frontier mathematical research.
Our long-term goal: a platform that makes genuine contributions to unsolved scientific problems.

---

## Problem

Modern AI tools for research have a fundamental honesty problem.

When you ask an LLM to help with a mathematical proof, it:
- Makes up plausible-sounding steps
- Cannot tell you what it actually verified vs. what it hallucinated
- Loses context across sessions
- Has no memory of failed attempts
- Produces no auditable reasoning trail

Researchers need the opposite: a system where the difference between "proved", "conjectured", "simulated", and "speculated" is explicit at every step.

---

## Solution

AXIOM makes reasoning explicit and verification visible.

Every claim in the system has an epistemic status: `CONJECTURED`, `VERIFIED`, `REFUTED`, `ESTIMATED`. Every proof step is traceable back to its source. Every sprint's progress is measured by an objective benchmark suite, not self-assessment.

Key capabilities:
1. **Knowledge Graph**: Typed mathematical entities (theorems, lemmas, definitions, conjectures) with dependency edges
2. **Proof Pipeline**: Lean 4 / Coq / Isabelle compilation with tactic suggestion
3. **SMT Gateway**: Z3-backed counterexample search over bounded parameter domains
4. **MCTS Search**: Monte Carlo Tree Search for algebraic proof exploration
5. **SCEP Benchmarks**: 32 auto-graded capability benchmarks across 8 scientific dimensions
6. **Prize Readiness Engine**: Evidence-based scoring toward the Clay Millennium Prize Problems

---

## Market

**Primary**: Research mathematicians, theoretical computer scientists, and formal methods engineers
**Secondary**: Graduate research programs, university math departments
**Long-term**: Any organization funding frontier scientific R&D

The global R&D market is $2.5T+. Even a 0.1% capture of the research tooling layer represents a $2.5B opportunity.

More importantly: if AXIOM's research track succeeds in contributing to recognized prize-backed problems, the platform becomes uniquely valuable as evidence of AI-augmented discovery.

---

## Traction

- EPIC-001 complete: Mathematical Intelligence Platform (124 files, 14,069 insertions)
- EPIC-002 complete: Scientific Capability Evaluation Platform (32 benchmarks, 0 regressions)
- Composite scientific capability score: 0.80 (up from 0.0 at project start)
- Prize readiness scores tracking for all 6 Clay Millennium Prize Problems
- 5/5 integration tests passing

---

## Why Now

Three converging trends make this the right moment:

1. **Formal proof tooling has matured**: Lean 4, Mathlib, and large proof libraries make automated proof checking practical for the first time.
2. **LLM reasoning has improved dramatically**: Modern language models can generate plausible proof tactics that serve as useful starting points for MCTS search.
3. **Research reproducibility crisis**: Scientific institutions are actively seeking tools that make reasoning auditable and reproducible.

---

## Why Us

We are building with evaluation-first principles from day one.

Every sprint is measured. Every capability is benchmarked. Every prize readiness score is grounded in evidence, not optimism.

We have an independent Chief Skeptic layer that rejects progress that isn't real.

This rigor is our competitive advantage. It is also what the hardest scientific problems demand.

---

## Ask

Seeking seed funding to:
1. Hire 2-3 senior ML/formal verification engineers
2. Build the first institutional pilot programs with research universities
3. Accelerate Track A (Artificial Scientist) development
4. Launch the public product with a strong user research methodology
