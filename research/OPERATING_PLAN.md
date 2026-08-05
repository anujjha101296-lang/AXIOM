# AXIOM Research Operating Plan

**Status:** initial operating plan — 2026-08-05  
**Scope:** the research track that runs in parallel with product and company work.  
**Initial wedge:** trustworthy AI-assisted mathematical research workflows.  
**Authority:** this plan implements the research process defined in [`.axiom/RESEARCH.md`](../.axiom/RESEARCH.md). The constitution, current state, task queue, capability map, prize track, knowledge graph, and memory ledger remain the operational source of truth.

## Objective and boundaries

AXIOM is building an organization that can measurably help people solve hard problems. The first research program is not “solve a prize problem”; it is to establish a repeatable workflow in which a researcher can move from a bounded mathematical question to traceable evidence, attempted refutation, and an honestly labeled result.

This track must compound reusable assets: benchmark cases, provenance records, verification artifacts, corpus annotations, failed approaches, and researcher feedback. It must not turn a plausible script, a generated conjecture, a keyword score, or a model explanation into a scientific claim.

The present baseline is constrained by **S0-E2** in [`.axiom/TASK_QUEUE.md`](../.axiom/TASK_QUEUE.md): the locally discovered Python 3.9.6 runtime is below the repository's Python 3.10+ requirement. No full-suite baseline, capability promotion, or scientific-performance comparison is valid until that gate is resolved.

## Evidence from the repository

| Area | Existing artifact | What it establishes | What it does not establish |
|---|---|---|---|
| Knowledge representation | `axiom/core/knowledge_graph/`, `axiom/mip/knowledge/` | A SQLite/NetworkX graph and mathematical ontology are implemented and tested. | Corpus accuracy, coverage, provenance quality, or researcher utility. |
| Literature ingestion | `axiom/core/parser/arxiv_parser.py` | arXiv/LaTeX parsing infrastructure exists. | Extraction precision/recall against a labeled corpus. |
| Counterexample checks | `axiom/core/verification/smt_gateway.py`, `tests/test_verification_improvements.py` | Bounded modular, polynomial, and real-inequality checks have tests. | General mathematical refutation or validity beyond the encoded domain. |
| Proof tooling | `axiom/mip/formal/`, `axiom/core/verification/lean_exporter.py` | Lean, Coq, and Isabelle script generators/adapters exist. | Formal proof verification until an actual prover/compiler succeeds and its output is retained. |
| Reasoning and hypothesis generation | `axiom/core/reasoning/`, `axiom/mip/conjecture/generator.py` | MCTS-style simplification and candidate-generation code exists. | Research-relevant reasoning, mathematical novelty, or truth of a candidate. |
| Evaluation | `axiom/evaluation/`, `tests/test_benchmark.py`, `docs/scientific_capability_framework.md` | An 8-dimension scoring schema and runnable benchmark scaffold exist. | An external, independent capability evaluation; several checks are deterministic implementation checks or use formal-system simulation. |

The table is an audit of repository artifacts, not a capability score. Any stronger claim requires the evidence program below.

## Initial researcher workflow

Every research run is a bounded unit. It is stored beneath `research/runs/<run-id>/` once implementation begins; a run is never represented only by chat history.

1. **Frame the question.** Write a one-sentence question, domain, intended user, hypothesis, and a decision the result could change. Set a time/compute budget, success metric, and stop condition.
2. **Assemble sources.** Record source identifier, license/access status, date, version, extraction method, and known limitations. Preserve citations or local source hashes. Unverified source text is evidence of a source, not evidence that a mathematical claim is true.
3. **Create a claim map.** Ingest or manually add definitions, assumptions, claims, dependencies, and provenance to the epistemic graph. Mark each claim as imported, generated, checked, refuted, formally verified, or unresolved; do not collapse these states.
4. **Generate bounded candidates.** Use retrieval, decomposition, MCTS, or conjecture generation only within the declared question. Each candidate must retain inputs, prompt/configuration, generator version, source nodes, and uncertainty. Novelty is a triage signal, never validation.
5. **Try to refute before promoting.** Apply domain-appropriate counterexamples, symbolic checks, numerical sanity checks, and adversarial test cases. Record all failures and inconclusive results alongside apparent successes.
6. **Verify at the strongest available tier.** Use a real prover/compiler for formal status. If no real toolchain succeeds, label the result `simulated`, `heuristic`, or `inconclusive`; never label it formal or proven. Store command, runtime/tool version, input script, stdout/stderr, exit status, and artifact hash.
7. **Review and decide.** A researcher or designated skeptic assesses scope, reproducibility, sources, and counterarguments. The outcome is one of: retain as hypothesis, reproduce, revise, refute, park, or escalate for independent human review. Publication, external sharing, or customer use requires founder authorization under [`.axiom/CONSTITUTION.md`](../.axiom/CONSTITUTION.md).
8. **Record the learning.** Link durable evidence and hypotheses in [`.axiom/KNOWLEDGE_GRAPH.md`](../.axiom/KNOWLEDGE_GRAPH.md), record the chronological outcome in [`.axiom/MEMORY.md`](../.axiom/MEMORY.md), and update maturity only under [`.axiom/CAPABILITIES.md`](../.axiom/CAPABILITIES.md)'s rules.

## Benchmark and evidence program

### Evidence tiers

| Tier | Meaning | May support |
|---|---|---|
| E0 — proposal | A model-generated or human-stated idea without a runnable check. | Triage only. |
| E1 — internal check | A deterministic unit/integration test or bounded computation run in the supported environment. | Implementation behavior within its specified domain. |
| E2 — reproducible evaluation | Versioned cases, manifest, configuration, raw outputs, and repeatable run instructions. | A narrowly stated measured capability. |
| E3 — independent reproduction | E2 repeated by an independent reviewer/environment with materially matching results. | A stronger research-capability claim. |
| E4 — formal verification | Actual prover/compiler acceptance with retained toolchain and output artifacts. | The precise formal statement only. |
| E5 — expert review | A qualified external or independent domain review, with scope and conflicts recorded. | Research relevance or novelty assessment, never broader than the review. |

### Required benchmark families

| Family | Initial measure | Minimum evidence needed before promotion | Current gap |
|---|---|---|---|
| Ingestion and claim extraction | Precision, recall, and provenance completeness on a frozen human-labeled sample. | E2 with labels, source manifest, and error taxonomy. | No labeled corpus or measured extraction quality. |
| Knowledge graph quality | Typed-node/edge validity, dangling-link rate, provenance completeness, and claim precision on sampled nodes. | E2 plus sampled human audit; E3 for accuracy claims. | Existing tests cover structure, not real-corpus accuracy. |
| Bounded counterexample search | Recall of planted false claims, false-positive rate, latency, and domain boundary. | E2 with disjoint hidden cases and encoded assumptions. | Tests demonstrate selected examples, not a holdout suite. |
| Formal verification | Valid/invalid classification and actual compiler pass rate, separated by proof system and theorem class. | E4 per accepted proof; E2 for aggregate rates. | Evaluation currently includes simulator/structural checks. |
| Candidate generation | Validity rate after refutation, duplicate rate, source traceability, and expert-interest rate. | E2 for validity/duplication; E5 for interest or novelty. | Token-distance novelty is not a novelty measurement. |
| Research workflow utility | Researcher task completion, time-to-auditable result, error recovery, and qualitative evidence of insight. | Approved pilot and a preregistered task protocol; E3 where possible. | No researcher studies or approved pilots yet. |

### Benchmark controls

- Freeze case IDs, expected outcomes, source/version manifest, and scoring code before a comparison. Keep development and holdout cases separate.
- Record runtime, OS, Python version, package lock/version information, model/configuration identifiers, random seeds, hardware/compute limits, start/end times, and raw outputs for every run.
- Report denominator, failures, skipped cases, exclusions, confidence/uncertainty, and changes from the last comparable run. A score without its case count and evidence tier is not decision-grade.
- Treat `tests/test_benchmark.py` and `axiom/evaluation/benchmarks/suite.py` as implementation and framework baselines until their cases are independently curated and their simulation paths are separated from actual compiler evidence.
- Do not train or tune against a holdout set. When a benchmark becomes overfit or ambiguous, retire it with a written rationale rather than silently replacing it.

## Monthly evaluation cadence

This cadence starts after the supported-runtime gate is satisfied. Before then, only documentation, fixture design, and non-claiming audit work may proceed.

| Week | Activity | Required output |
|---|---|---|
| 1 — Baseline | Reproduce the last accepted benchmark snapshot; validate environment and manifests; triage regressions. | Run record with pass/fail, case counts, skipped cases, and comparability decision. |
| 2 — Experiment | Execute one to three bounded hypotheses chosen for uncertainty reduction, not demo value. | Experiment records with success thresholds and stop decisions. |
| 3 — Adversarial review | Run hidden/negative cases, inspect provenance, and seek counterexamples or verifier disagreement. | Skeptic report, failures, and proposed fixes or kills. |
| 4 — Decision | Compare only like-for-like snapshots; review capability maturity and product relevance. | Research review: continue, scale, revise, park, or kill; next month's queue. |

At month end, publish internally a one-page scorecard with: capability dimensions measured; evidence tier; sample size; success/failure/skip counts; reproducibility status; formal-verification count; material regressions; researcher-workflow evidence; and the decisions taken. Update the AOS only in the owning operational cycle; this plan itself does not supersede it.

## Milestones

### Months 1–2 — Trustworthy research baseline

**Outcome sought:** one small, auditable mathematical research workflow can be run end-to-end without overstating its result.

- Resolve and document a Python 3.10+ test/runtime baseline; rerun the full suite and retain results.
- Separate simulated proof checks from actual prover/compiler checks in evaluation outputs and API/result labels.
- Define a versioned benchmark manifest and an initial labeled corpus slice for one narrow domain (recommended: elementary algebra/number theory rather than prize-problem claims).
- Produce first E2 records for ingestion, bounded counterexample search, and graph provenance; establish an explicit `inconclusive` path.
- Install or containerize at least one actual proof toolchain, then capture E4 evidence only for statements that compile successfully.

**Exit evidence:** reproducible commands and manifests, raw artifacts for one end-to-end run, a clear evidence-tier report, and a documented failure/limitation list. This is a trust milestone, not proof of research utility.

### Months 3–6 — Research-workspace alpha

**Outcome sought:** a small number of approved researchers can use a traceable workflow on bounded real tasks and give actionable feedback.

- Expand the curated corpus and hidden evaluation set; measure extraction/graph quality rather than database growth alone.
- Support a researcher workspace that connects source → claim map → candidate → refutation/verification → run report.
- Compare AXIOM-assisted and baseline workflows on predefined tasks, recording completion time, error/rework, and user judgment without claiming causal impact from anecdote.
- Improve formal verification coverage for a restricted theorem class; keep actual and simulated metrics separate.
- Run an approved closed pilot only after human authorization for outreach, data handling, and external communication.

**Exit evidence:** repeated E2 runs, at least one independently reproduced workflow where feasible, a pilot report with limitations, and a prioritized evidence-backed product/research backlog.

### Months 6–12 — Measured research capability

**Outcome sought:** AXIOM has a dependable, domain-bounded research workflow with repeatable evidence and early signs of researcher value.

- Operate monthly benchmark snapshots with regression gates and retained provenance.
- Add a second domain only after the first domain has stable measurements and a named failure taxonomy.
- Demonstrate E4 formal proofs within the supported scope and independently reproduce selected results where practical.
- Measure whether AXIOM improves a defined research task relative to a baseline; distinguish platform reliability, researcher productivity, and scientific insight.
- Prepare a technical report only if results are reproducible, appropriately reviewed, and authorized; otherwise retain it as an internal evidence package.

**Exit evidence:** a maintained evidence ledger, reproducible cross-run comparisons, a limited-but-honest capability statement, and a decision on whether to deepen the wedge or redirect.

## Explicit non-claims

Until evidence at the stated tiers exists, AXIOM does **not** claim that it:

- solves, proves, disproves, or materially advances the Riemann Hypothesis or any Clay Millennium Prize Problem;
- is capable of autonomous scientific discovery, an autonomous research team, or self-improvement that produces validated scientific output;
- formally verifies a theorem when an actual formal prover/compiler has not accepted the exact script and artifact;
- generates mathematically novel, true, interesting, or publishable conjectures merely because a novelty heuristic, test, or model output says so;
- has achieved a scientific-capability level, composite readiness score, or prize-readiness score based on uncurated, simulated, keyword-driven, or non-reproducible evaluations;
- improves a researcher's productivity, insight, or outcomes without an appropriately designed, approved study; or
- has users, pilots, institutional validation, revenue, publication, or expert endorsement absent recorded, authorized evidence.

## Decision rules for the parallel tracks

- **Research track:** invest where a small experiment can materially reduce uncertainty about truthfulness, verification, or researcher value.
- **Product track:** expose only capabilities whose evidence tier and limitations can be shown honestly to users; unsafe or ambiguous result labels are P0 work.
- **Company track:** communicate the long-term ambition as an objective, not an achieved capability. Outreach, pilot recruitment, fundraising, publication, and material data access remain human-authorized actions.

The default decision is to narrow scope, preserve negative evidence, and improve measurement. Prize-adjacent work may be explored as a bounded research program only after the prerequisite capability and verification evidence is present in the AOS.

## First research queue after the runtime baseline

1. Audit all proof/verifier result states and ensure simulated, heuristic, compiler-verified, and inconclusive outcomes cannot be conflated.
2. Create a benchmark manifest schema and fixed, versioned case set for one restricted mathematical domain.
3. Build a reproducible run-record/provenance artifact for the existing evaluation framework.
4. Create a small labeled ingestion/claim-extraction sample and measure baseline precision/recall.
5. Stand up one real formal-prover execution path, add valid and invalid fixtures, and retain compiler artifacts.

Each item must be entered through [`.axiom/TASK_QUEUE.md`](../.axiom/TASK_QUEUE.md) with an owner, acceptance signal, dependencies, and knowledge-graph evidence link before implementation.
