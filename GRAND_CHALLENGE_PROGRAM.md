# AXIOM Grand Challenge Program

The Grand Challenge Program (GCP) is AXIOM's permanent framework for managing long-term scientific campaigns — from educational toy problems to frontier capability tests. It does **not** solve prize problems. It manages the system that guides AXIOM from learning exercises to credible research participation.

## Purpose

AXIOM must progress through disciplined capability building before attempting frontier science. GCP provides:

1. **Challenge tiers** — six levels of increasing difficulty and scope
2. **Challenge registry** — full specifications for every challenge
3. **Campaign management** — long-running execution with evidence and journals
4. **Readiness gates** — capability thresholds before tier advancement

## Challenge Tiers

| Tier | Name | Purpose | Current Evidence |
|------|------|---------|------------------|
| 0 | Toy Reasoning | Pipeline validation | SCEP auto-graded (measured) |
| 1 | Known-Answer | Theorem/proof tasks with hidden answers | SCEP benchmarks (measured/simulated) |
| 2 | Paper Reproduction | Methodology replication | Workflow demos (baseline) |
| 3 | Small Open | Bounded novelty questions | Heuristic scoring |
| 4 | Domain Grand | Multi-year campaigns | Composite SCEP + checkpoints |
| 5 | Frontier | Organizational readiness tests | **Not a prize solver** |

## Architecture

```
Challenge Registry (tiers 0–5)
        ↓
Grand Challenge Engine (campaign management)
        ↓
┌───────┴────────┬──────────────┬─────────────┐
│  SCEP Benchmarks│ Workflow CP  │ Prize Readiness│
│  (capability)   │ (checkpoint) │ (assessment)   │
└───────┬────────┴──────────────┴─────────────┘
        ↓
   Readiness Gates → Tier Advancement
```

GCP reuses existing infrastructure:
- **SCEP** (`axiom/evaluation/`) — benchmark execution and capability scoring
- **Workflow checkpoints** (`axiom/workflow/checkpoints.py`) — long-running recovery
- **Prize readiness** — Tier 5 organizational assessment (not solution attempts)

## Campaign Management

| Feature | Implementation |
|---------|----------------|
| Campaign creation | `GrandChallengeEngine.create_campaign()` |
| Progress tracking | `challenges_completed`, `progress_fraction()` |
| Experiment tracking | `ExperimentRecord` per challenge run |
| Evidence collection | `EvidenceRecord` with explicit evidence tier |
| Hypothesis tracking | `HypothesisRecord` with confidence and status |
| Research journals | `JournalEntry` + `generate_campaign_journal()` |
| Checkpointing | `CampaignCheckpoint` + workflow checkpoint store |
| Long-running execution | Checkpoint/resume across campaign lifecycle |

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/gcp/manifest` | GET | Program manifest |
| `/gcp/challenges` | GET | List challenges (optional `?tier=N`) |
| `/gcp/gates` | GET | Readiness gate definitions |
| `/gcp/campaigns` | POST | Create campaign |
| `/gcp/campaigns/{id}/run-tier` | POST | Run all challenges in current tier |
| `/gcp/campaigns/{id}/checkpoint` | POST | Save checkpoint |
| `/gcp/campaigns/{id}/readiness` | GET | Evaluate readiness gate |
| `/gcp/campaigns/{id}/advance` | POST | Advance to next tier (if gate passed) |
| `/gcp/campaigns/{id}/journal` | GET | Research journal |

## Usage

```python
from axiom.grand_challenge import GrandChallengeEngine
from axiom.grand_challenge.models import ChallengeTier

engine = GrandChallengeEngine("axiom.db")
campaign = engine.create_campaign(
    name="Foundations Campaign",
    tier=ChallengeTier.TIER_1_KNOWN_ANSWER,
)
engine.activate_campaign(campaign.campaign_id)
engine.run_tier_batch(campaign.campaign_id)
print(engine.get_journal(campaign.campaign_id))
```

## Benchmark

```bash
make gcp-benchmark
```

## Recommended First Tier 1 Campaign

**Campaign: "Foundations of Known-Answer Mathematical Reasoning"**

| Field | Value |
|-------|-------|
| Tier | 1 |
| Challenges | `t1_fermat_little_theorem`, `t1_euler_identity`, `t1_proof_verification_basics` |
| Objective | Establish measured competence on undergraduate known-answer tasks before paper reproduction |
| Duration | 2-week bounded campaign |
| Success | >= 2/3 challenges pass with honest evidence tiers |
| Human review | Weekly review of evidence tier labels and experiment journal |

**Why this campaign:**
- Uses existing SCEP benchmarks with auto-grading (measured evidence)
- Bounded scope — no open research claims
- Exercises full campaign lifecycle: experiments, evidence, checkpoints, journal
- Proof verification challenge explicitly discloses simulated path when compilers absent
- Gate to Tier 2 requires human approval after demonstrated Tier 1 competence

**What this campaign does NOT claim:**
- No prize problem progress
- No formal proof certificates (unless compilers installed and verified)
- No frontier research capability

## Honest Capability Statement

Current GCP capabilities are **prototype** maturity:
- Tier 0–1 challenges use SCEP auto-graded benchmarks (measured for math reasoning)
- Proof verification may be simulated when formal compilers are absent
- Tier 2+ challenges require workflow execution and human review (not fully automated)
- Tier 5 is gated and requires human authorization

See `CHALLENGE_REGISTRY.md`, `READINESS_GATES.md`, and `ROADMAP_ALIGNMENT.md` for details.
