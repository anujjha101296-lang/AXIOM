# North Star Metrics

AXIOM measures organizational progress — not activity. Every metric has a definition, evidence source, and honest current status.

**Rule:** If not yet measured, status is `unavailable`. Never invent values.

---

## Product Metrics

| Metric | Definition | Target (aspirational) | Current status | Evidence source |
|--------|------------|----------------------|----------------|-----------------|
| Weekly active researchers | Unique users completing >= 1 research session per week | TBD when alpha launches | **unavailable** | Analytics (not instrumented) |
| Research sessions completed | Sessions reaching a saved outcome (note, report, Q&A) | TBD | **unavailable** | `/research` session logs |
| Time saved | Self-reported or observed time vs. manual baseline | TBD | **unavailable** | User interviews |
| User retention | % returning within 7 days | TBD | **unavailable** | Analytics (not instrumented) |
| Task completion rate | % of started workflows reaching completion | Internal baseline | **baseline** | Workflow engine status |

---

## Scientific Capability Metrics

| Metric | Definition | Current status | Evidence source |
|--------|------------|----------------|-----------------|
| SCEP composite score | Weighted average across 8 capability dimensions | **measured** (varies by run) | `python3 -m axiom.evaluation.run_benchmarks` |
| Benchmark improvement | Delta vs. prior SCEP run | **measured** | `docs/capability_delta_*.md`, eval DB |
| Verification accuracy | % of verification outcomes correctly tiered | **measured** (core tests) | `tests/test_verification_truthfulness.py` |
| Literature coverage | Retrieval precision on benchmark corpus | **baseline** | SCEP `literature_synthesis` |
| Autonomous task completion | Workflow campaigns completing without human intervention | **baseline** | GCP + workflow checkpoints |
| Hallucination / false claim rate | Claims marked formal without compiler evidence | **0 in core tests** | Truthfulness audit (S0-E3) |
| GCP tier progress | Highest campaign tier with passed readiness gate | **Tier 0** | `gcp_benchmark_results.json` |

### Capability dimensions (SCEP)

| Dimension | Weight | Measurement method |
|-----------|--------|-------------------|
| mathematical_reasoning | 0.20 | Auto-graded benchmark suite |
| proof_verification | 0.18 | SMT/simulated verification cases |
| conjecture_generation | 0.15 | Heuristic novelty scoring |
| knowledge_quality | 0.12 | Graph metrics + benchmarks |
| counterexample_search | 0.12 | Finite search cases |
| research_planning | 0.10 | Plan completeness scoring |
| literature_synthesis | 0.08 | Keyword/coverage scoring |
| research_productivity | 0.05 | Workflow artifact scoring |

---

## Engineering Metrics

| Metric | Definition | Current status | Evidence source |
|--------|------------|----------------|-----------------|
| Core test pass rate | `pytest tests/ --ignore=tests/e2e` | **171/171** (2026-08-08) | CI / local pytest |
| E2E test pass rate | Full e2e suite | **partial** (MDE surface gap) | `tests/e2e/` |
| Regression rate | New failures per release | **tracked** | CI history |
| Build stability | CI green on main | **monitored** | `.github/workflows/ci.yml` |
| Benchmark regression | SCEP score drop > threshold | **tracked** | eval delta reports |

---

## Research Metrics

| Metric | Definition | Current status | Evidence source |
|--------|------------|----------------|-----------------|
| Papers reproduced | Full methodology replication with artifacts | **0** (demo only) | GCP Tier 2 |
| Hypotheses evaluated | Count with documented evidence | **campaign-tracked** | GCP campaign journals |
| Failed hypotheses recorded | Failures logged as first-class outputs | **policy active** | `MEMORY.md`, campaign evidence |
| Verified contributions | Independently confirmed results | **0** | N/A — no claims made |
| Campaign experiments run | GCP experiments with evidence tier | **measured** | GCP store |

---

## Anti-Metrics (Do Not Optimize)

- Lines of code
- Number of AI agents or prompts
- Number of features shipped without benchmark evidence
- Capability scores without evidence tier disclosure
- Prize readiness scores presented as progress

---

## Review Cadence

| Frequency | Review |
|-----------|--------|
| Weekly | SCEP composite + test pass rate |
| Monthly | Full north star review in strategic loop |
| Quarterly | Public benchmark publication (human-approved only) |

Update this document when a metric transitions from `unavailable` to `baseline` or `measured`.
