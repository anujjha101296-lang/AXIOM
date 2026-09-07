# AXIOM Engineering Council

**Purpose:** Provide domain-specific review for each engineering cycle. Council roles are **logical review lenses**, not separate chat agents. One engineering review run inspects all domains and produces actionable recommendations.

---

## Council Roles

| Role | Domain | Inspects |
|------|--------|----------|
| **CTO** | Strategic alignment, integrity, sequencing | Task queue, evidence gates, integrity vs feature velocity |
| **Platform Lead** | Core platform, APIs, shared infrastructure | Router mounting, API surface vs e2e expectations |
| **Backend Lead** | Python services, persistence, data models | Store scoping, coverage, workflow engine |
| **Frontend Lead** | Next.js UI, UX, client integration | npm audit, waitlist, mode banners, UI deploy |
| **AI Systems Lead** | Model gateway, research loop, evaluation | Benchmark regressions, LLM wiring, eval evidence |
| **Infrastructure Lead** | CI/CD, containers, observability | Import performance, Grafana, governance CI |
| **Security Lead** | Auth, tenancy, secrets, dependencies | JWT enforcement, isolation, audit workflows |
| **QA Lead** | Test strategy, coverage, regression gates | Core/e2e split, coverage %, workflow tests |
| **Product Engineering Lead** | Research workspace wedge, MVP readiness | P0 blockers, contributor docs, demo honesty |

---

## Review Cycle

Each engineering cycle follows this sequence:

```
Observe → Collect evidence → Score health → Council review → Prioritize → Record
```

### 1. Observe

Run automated collectors across the repository:

```bash
make engineering-health
# or
python3 scripts/run_engineering_review.py
```

### 2. Collect evidence

| System | Collector | Answers |
|--------|-----------|---------|
| Technical debt tracking | `debt` | What is broken? What should be refactored/deleted? |
| Dependency health | `dependencies` | What packages are vulnerable or stale? |
| Code quality scoring | `code_quality` | What is duplicated? Lint/type issues? |
| Architecture consistency | `architecture` | Do routers, ADRs, and layers match contracts? |
| Performance regression | `performance` | What is slow? Import-time regressions? |
| Security scanning | `security` | What should be hardened before external access? |
| Documentation coverage | `documentation` | What should be documented? |
| Test coverage | `testing` | What should be tested? |
| Benchmark regression | `benchmarks` | What should be benchmarked? Regressions? |
| Repository dashboard | `dashboard.json` | Composite health snapshot |

### 3. Score health

Every cycle ends with eight scores (0–100):

- Engineering Health Score
- Product Health Score
- Research Capability Score
- Technical Debt Score (higher = more debt)
- Security Score
- Performance Score
- Developer Experience Score
- Repository Maturity Score

### 4. Council review

Each role produces **one primary recommendation** per cycle, recorded in `ENGINEERING_HEALTH.md`.

### 5. Prioritize

Findings are ranked into `TOP_25_PRIORITIES.md`. Exactly **ONE** highest-leverage initiative is selected per cycle.

### 6. Record

Update operational documents:

- `ENGINEERING_HEALTH.md`, `PRODUCT_HEALTH.md`, `RESEARCH_HEALTH.md`
- `TECH_DEBT_BOARD.md`, `TOP_25_PRIORITIES.md`
- `.axiom/governance/dashboard.json`
- `.axiom/CURRENT_STATE.md` (after meaningful cycles)

---

## Cadence

| Trigger | Action |
|---------|--------|
| Weekly (Monday 07:00 UTC) | CI governance workflow runs review |
| Before major releases | Manual `make engineering-health` |
| After engineering sprints | Update `.axiom/CURRENT_STATE.md` with scores |

---

## Human Authority

Per `.axiom/CONSTITUTION.md`, humans retain authority over production deployment, external communication, and strategic commitments. The council produces **recommendations**; humans approve irreversible actions.

---

*Part of the AXIOM Self-Evolving Engineering Organization initiative.*
