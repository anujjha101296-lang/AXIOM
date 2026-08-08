# Readiness Gates

Before a campaign advances to the next challenge tier, GCP verifies that required capability thresholds are met. Gates are **honest** — they use measured SCEP scores where available and explicitly flag estimated dimensions.

## Gate Overview

| Gate | From → To | Human Approval | Min Composite |
|------|-----------|----------------|---------------|
| gate_0_to_1 | Tier 0 → 1 | No | — |
| gate_1_to_2 | Tier 1 → 2 | **Yes** | 0.35 |
| gate_2_to_3 | Tier 2 → 3 | **Yes** | 0.45 |
| gate_3_to_4 | Tier 3 → 4 | **Yes** | 0.55 |
| gate_4_to_5 | Tier 4 → 5 | **Yes** | 0.60 |

## Gate 0 → 1: Toy to Known-Answer

**Description:** Complete Tier 0 toy challenges with measured evidence.

| Requirement | Threshold |
|-------------|-----------|
| Tier 0 challenges completed | >= 2 |
| Experiments run | >= 2 |
| Evidence records | >= 2 |
| Checkpoints saved | >= 1 |
| mathematical_reasoning score | >= 0.4 |
| Human approval | Not required |

**Rationale:** Tier 0 validates the campaign pipeline works. Tier 1 requires basic math reasoning demonstrated through SCEP auto-graded cases.

## Gate 1 → 2: Known-Answer to Paper Reproduction

**Description:** Demonstrate known-answer competence before paper reproduction.

| Requirement | Threshold |
|-------------|-----------|
| Tier 1 challenges completed | >= 3 |
| Experiments run | >= 5 |
| Evidence records | >= 5 |
| Checkpoints saved | >= 2 |
| Composite score | >= 0.35 |
| mathematical_reasoning | >= 0.5 |
| proof_verification | >= 0.3 |
| Human approval | **Required** |

**Rationale:** Paper reproduction requires demonstrated ability to verify known results. Proof verification may be simulated; evidence tier must be honestly disclosed.

**Warning:** If proof_verification score is estimated (not measured), gate evaluation emits a warning.

## Gate 2 → 3: Paper Reproduction to Small Open

**Description:** Reproduce methodology before attempting open questions.

| Requirement | Threshold |
|-------------|-----------|
| Tier 2 challenges completed | >= 2 |
| Experiments run | >= 8 |
| Evidence records | >= 8 |
| Checkpoints saved | >= 3 |
| Composite score | >= 0.45 |
| research_planning | >= 0.3 |
| literature_synthesis | >= 0.3 |
| Human approval | **Required** |

**Rationale:** Open research questions require demonstrated planning and synthesis capability.

## Gate 3 → 4: Small Open to Domain Grand

**Description:** Bounded open research before multi-year grand campaigns.

| Requirement | Threshold |
|-------------|-----------|
| Tier 3 challenges completed | >= 2 |
| Experiments run | >= 15 |
| Evidence records | >= 15 |
| Checkpoints saved | >= 5 |
| Composite score | >= 0.55 |
| conjecture_generation | >= 0.2 |
| research_planning | >= 0.4 |
| Human approval | **Required** |

**Rationale:** Grand campaigns require sustained research discipline. Conjecture threshold is intentionally low because scoring is heuristic.

## Gate 4 → 5: Domain Grand to Frontier

**Description:** Organizational maturity before frontier capability tests.

| Requirement | Threshold |
|-------------|-----------|
| Tier 4 challenges completed | >= 2 |
| Experiments run | >= 30 |
| Evidence records | >= 30 |
| Checkpoints saved | >= 10 |
| Composite score | >= 0.60 |
| mathematical_reasoning | >= 0.6 |
| proof_verification | >= 0.5 |
| knowledge_quality | >= 0.4 |
| Human approval | **Required** |

**Rationale:** Tier 5 assesses organizational readiness. It does **not** authorize prize solution attempts. Human must explicitly approve frontier-tier campaign activation.

## Evaluation API

```python
from axiom.grand_challenge import GrandChallengeEngine

engine = GrandChallengeEngine("axiom.db")
readiness = engine.evaluate_readiness(campaign_id)
# Returns: passed, checks, blockers, warnings

# Advance only if passed:
campaign = engine.advance_tier(campaign_id, human_approved=True)
```

REST: `GET /gcp/campaigns/{id}/readiness` and `POST /gcp/campaigns/{id}/advance`

## Check Structure

Each gate evaluation returns individual checks:

```json
{
  "check": "challenges_completed",
  "required": 2,
  "actual": 3,
  "passed": true
}
```

Dimension checks include an `estimated` flag when SCEP score is not measured:

```json
{
  "check": "dimension:proof_verification",
  "required": 0.3,
  "actual": 0.45,
  "passed": true,
  "estimated": true
}
```

## What Gates Do NOT Do

- Gates do not guarantee scientific discovery capability
- Gates do not authorize prize problem solution attempts
- Gates do not override human authority on external communication
- Passing a gate does not promote capability maturity in `CAPABILITIES.md` — that requires independent evidence review

## Current Honest Assessment

As of implementation, only Tier 0–1 gates can be partially evaluated automatically:
- **Tier 0 → 1:** Fully automatable with SCEP math reasoning benchmarks
- **Tier 1 → 2:** Requires human approval; proof verification may be simulated
- **Tier 2+:** Require workflow execution and human review not yet fully automated

Thresholds are set conservatively to avoid artificial capability inflation.
