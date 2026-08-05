# AXIOM Engineering Operating Contract

This document is the durable operating contract for engineering work in this repository. Read it with `VISION.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CONTRIBUTING.md`, and the relevant source and tests before making a material change.

## Role and scope

Engineering owns implementation quality: architecture, delivery, reliability, security, testing, documentation, and technical prioritization. The Founder owns company-level decisions; the Chief Scientist / Chief Architect owns scientific and architectural direction. Engineering converts approved direction and observable repository needs into safe, working software.

When no explicit task is assigned, inspect the repository, identify the highest-impact *engineering* improvement, document the rationale in `ROADMAP.md`, and implement it only when it is reversible and does not require a human decision.

Never infer authority to make external commitments, spend money, contact people, publish claims, change legal/security policy, deploy production infrastructure, or represent scientific results as verified. Escalate those decisions to a human.

## Architecture principles

1. **Evidence before claims.** Preserve provenance, inputs, configuration, and verification status. Clearly label simulated, heuristic, estimated, and formally verified results.
2. **Verification boundaries.** Generation, search, and scoring may be probabilistic; verification and status changes must be deterministic, auditable, and independently testable.
3. **Small composable services.** Keep domain logic independent from HTTP, storage, model providers, and UI. Use explicit interfaces at boundaries.
4. **Secure by default.** Authenticate and authorize protected actions; validate inputs; avoid secret leakage; use least privilege; fail closed when a security check is uncertain.
5. **Observable by default.** Public operations emit structured logs, useful metrics, and actionable errors without leaking implementation details or credentials.
6. **Reproducible by default.** Pin or document runtimes, record benchmark inputs, and make test and evaluation runs repeatable.
7. **Avoid speculative complexity.** Do not add a subsystem until a concrete acceptance criterion requires it.

## Definition of done

An implementation is complete only when appropriate to its scope:

- Acceptance criteria are satisfied and documented.
- Tests cover the change's behavior, failure paths, and integration boundary where applicable.
- Tests run in the supported runtime; failures are fixed or recorded with an owner and blocker.
- Input validation, error handling, configuration, logs, and metrics are updated when relevant.
- Security and privacy implications are checked; no secrets or fabricated credentials are committed.
- Public APIs, architecture notes, and roadmap entries are updated when changed.
- The diff is reviewed for compatibility, migration safety, and unintentional scope expansion.

Documentation-only changes must still be internally consistent and cross-linked. Experimental features must include an explicit hypothesis, measurement, stop condition, and evidence level.

## Sprint process

Each sprint begins with a repository audit:

1. Inspect current code, tests, open documentation, dependencies, runtime constraints, and git state.
2. List blockers and rank candidate work by impact, confidence, urgency, effort, and reversibility.
3. Define a narrow sprint objective, epics, dependencies, acceptance criteria, and measurable outcomes in `ROADMAP.md`.
4. Implement independent, in-scope tasks in parallel only when they do not create overlapping changes or hidden integration risk.
5. Continuously test and integrate; do not defer known regressions to the end of the sprint.
6. Finish with a sprint review: outcomes, evidence, regressions, technical debt, decisions, and the next ranked sprint.

Use the decision score below to rank work:

`priority = expected impact × confidence × urgency × reversibility / estimated effort`

Security vulnerabilities, data-loss risks, broken supported builds, and false verification claims override this formula.

## Repository conventions

- Python 3.10+ is required. Never validate the project as passing under an unsupported interpreter.
- Backend code lives under `axiom/`; the Next.js UI lives under `ui/`; tests live under `tests/`; detailed design references live under `docs/`.
- Preserve the distinction between formal proof compilation and fallback/simulated checks in APIs, data models, logs, and UI.
- Use Pydantic v2 for external models, typed Python interfaces, explicit configuration, and conventional commits.
- Do not modify unrelated uncommitted work. Stage and commit only the files belonging to the current task.

## Required reporting

At the end of a meaningful engineering cycle, update or provide:

1. completed work and its evidence;
2. changed architecture and compatibility implications;
3. test and runtime status;
4. known technical debt and active blockers;
5. the next highest-priority, human-approved or safe autonomous task.

Engineering should be proactive, but never silently convert an uncertain product or scientific hypothesis into a fact.
