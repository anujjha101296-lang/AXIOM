# Engineering Contract

Read `CONSTITUTION.md`, `OPERATING_SYSTEM.md`, `CURRENT_STATE.md`, `TASK_QUEUE.md`, `DECISION_FRAMEWORK.md`, root `ENGINEERING.md`, and `ARCHITECTURE.md` before material engineering work.

## Mandate

Engineering turns validated needs and repository evidence into reliable, secure, observable, maintainable software. It owns technical execution—not unapproved product, scientific, or business commitments.

## Definition of done

- Clear acceptance criteria and an appropriately scoped diff.
- Tests for behavior and relevant failure paths, executed in the supported runtime.
- Input validation, configuration, logs, metrics, errors, and security reviewed as applicable.
- Public behavior, architecture, `CURRENT_STATE.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` updated when affected.
- No secrets, fabricated results, unrelated edits, or status inflation.

## Engineering rules

- Maintain explicit boundaries between interfaces, domain logic, persistence, and external adapters.
- Make formal proof status available only after actual prover/compiler success; label fallbacks as simulated or heuristic.
- Prefer additive, reversible migrations and testable adapters.
- Fix P0 data-loss, security, false-claim, and supported-build failures before feature expansion.
- Commit focused work using conventional commits; stage only files owned by the task.

## Handoff

Record the result, test evidence, known debt, and next runnable task in the operational documents. See `RESEARCH.md` for experimental software, `CAPABILITIES.md` for platform intent, and `PRIZE_TRACK.md` for scientific readiness constraints.
