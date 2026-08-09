# Roadmap Alignment

How the Grand Challenge Program maps to AXIOM's adaptive roadmap, capability maturity model, and prize track governance.

## Roadmap Track Mapping

| GCP Tier | AXIOM Roadmap Horizon | RVP Stage (when merged) | Capability Maturity Target |
|----------|------------------------|-------------------------|---------------------------|
| 0 | Horizon 0 — Trustworthy baseline | Infrastructure (0) | Prototype → measured (pipeline) |
| 1 | Horizon 0 — Trustworthy baseline | Known-answer (1) | Prototype → measured (benchmarks) |
| 2 | Horizon 1 — Measurable capability | Paper reproduction (2) | Prototype → reproducible |
| 3 | Horizon 1 — Measurable capability | Research assistant (3) | Measured → reproducible |
| 4 | Horizon 1 — Measurable capability | Long-running autonomous (5) | Reproducible → independently verified |
| 5 | Horizon 3 — Compounding discovery | Prize preparation (6) | Organizational readiness only |

## Track A — Research (Continuous)

### Horizon 0 — Trustworthy Baseline

**GCP contribution:** Tiers 0–1 provide structured campaigns that validate:
- SCEP benchmark execution with honest evidence tiers
- Campaign lifecycle (create → experiment → evidence → checkpoint → journal)
- Readiness gate enforcement before advancement

**Alignment with completed work:**
- S0-E4 evidence gate → GCP evidence tier model
- SCEP benchmarks → Tier 0–1 challenge execution
- Verification truthfulness audit → Tier 1 proof verification disclosure

**Gap:** Research Kernel (when merged) will provide execution engine for campaign experiments. Currently GCP delegates directly to SCEP.

### Horizon 1 — Measurable Research Capability

**GCP contribution:** Tiers 2–4 structure the path from paper reproduction to sustained campaigns:
- Tier 2: Workflow demo reproduction exercises planning and synthesis
- Tier 3: Open problem decomposition exercises hypothesis generation
- Tier 4: Multi-domain capability campaign exercises regression detection and checkpoint discipline

**Dependencies not yet met:**
- Full workflow worker execution for Tier 2 challenges
- SME-gated research sessions for Tier 3+ (on feature branch)
- H1-OBS provenance for campaign experiment records (on feature branch)

## Track B — Product (Continuous)

### Milestone 1 — Researcher Workflow MVP

GCP Tier 2 challenges (`t2_workflow_demo_reproduction`) directly support the researcher workflow MVP by providing a structured campaign template for end-to-end workflow execution with artifact checklist.

### Milestone 2 — Public Alpha

GCP campaign journals and evidence trails provide the honest documentation needed for public alpha demonstrations — showing what AXIOM can and cannot do at each tier.

## Track C — Company (Continuous)

### Horizon 3 — Compounding Discovery Organization

GCP Tier 5 (`t5_prize_readiness_assessment`) aligns with the prize track governance principle: measure organizational readiness without claiming prize progress. This is an internal capability test, not a public claim.

## Capability Map Alignment

From `.axiom/CAPABILITIES.md` maturity model: `Idea → prototype → measured → reproducible → independently verified → operationally reliable`

| GCP Action | Capability Impact |
|------------|-------------------|
| Tier 0 campaign completion | mathematical_reasoning: prototype → measured (if SCEP passes) |
| Tier 1 campaign completion | proof_verification: prototype (simulated path disclosed) |
| Tier 2 campaign completion | research_planning, literature_synthesis: remains prototype until human review |
| Tier 4 sustained campaign | Multiple dimensions: measured with regression monitoring |
| Tier 5 readiness assessment | Documents gaps; does not promote maturity |

**Rule:** GCP gate passage does not automatically update `CAPABILITIES.md`. Capability promotion requires independent evidence review per the capability maturity model.

## Prize Track Alignment

From `.axiom/PRIZE_TRACK.md`:

> Prize-backed problems are long-horizon capability tests, not near-term delivery promises.

GCP enforces this:
- Tier 5 challenges assess readiness; they do not attempt solutions
- `t5_prize_readiness_assessment` generates gap reports, not progress claims
- `t5_frontier_benchmark_participation` is gated (no external benchmark integrated)
- Human authorization required before any Tier 5 campaign activation

## Task Queue Alignment

| Task Queue Item | GCP Relationship |
|----------------|------------------|
| S0-E2 Test baseline | Tier 0 validates pipeline on passing test suite |
| S0-E4 Evidence gate | GCP evidence tier model inherits EPIC-002 states |
| RVP-1 (feature branch) | Tier 1 challenges map to RVP known-answer stage |
| SME-1 (feature branch) | Tier 3+ campaigns will require SME session linkage |
| ACA-1 (feature branch) | Tier 3+ reasoning delegates through ACA |
| RK-1 (feature branch) | Campaign experiments will execute through Research Kernel |
| P3-RL Research loop merge | Long-horizon discovery = Tier 4 campaigns |

## Recommended Sequencing

```
Now:     Tier 0 campaign (pipeline validation)
         ↓ gate_0_to_1
Next:    Tier 1 "Foundations of Known-Answer Mathematical Reasoning" campaign
         ↓ gate_1_to_2 (human approval)
Future:  Tier 2 paper reproduction (after workflow + SME merge)
         ↓
Future:  Tier 3–4 (after research kernel + research loop merge)
         ↓
Future:  Tier 5 readiness assessment (organizational maturity only)
```

## Integration Roadmap

| Integration | Status | GCP Impact |
|-------------|--------|------------|
| SCEP benchmarks | **On main** | Tier 0–1 execution |
| Workflow checkpoints | **On main** | Campaign checkpointing |
| Prize readiness scorer | **On main** | Tier 5 assessment |
| RVP known-answer dataset | Feature branch | Tier 1 challenge expansion |
| SME scientific method | Feature branch | Tier 3+ session governance |
| Research Kernel | Feature branch | Unified campaign execution |
| H1-OBS provenance | Feature branch | Experiment audit trail |

## What GCP Does Not Replace

- `ROADMAP.md` — strategic sequencing and horizons
- `CAPABILITIES.md` — independent capability maturity assessment
- `PRIZE_TRACK.md` — prize problem governance
- `TASK_QUEUE.md` — executable engineering work ranking
- `DECISION_FRAMEWORK.md` — task prioritization formula

GCP is the **operational framework** for running scientific campaigns within these governance documents.
