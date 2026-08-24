# AXIOM Phase 15 — Computational Experiment & Verification Engine Architecture

## 1. Overview
AXIOM Phase 15 connects scientific reasoning to **Safe Computational Execution**. Instead of allowing unverified AI model claims, Phase 15 converts predictions into executable experiment plans, runs them in an isolated sandbox, verifies reproducibility and independent calculation, and updates hypothesis epistemic status.

---

## 2. Critical Epistemic Distinction
$$\text{COMPUTATIONAL OBSERVATION} \neq \text{MATHEMATICAL PROOF}$$

A finite numerical experiment testing $N$ cases confirms that no counterexample was found within the evaluated domain. It does **NOT** constitute a formal mathematical proof of a general proposition.

---

## 3. Secure Execution Sandbox & Defenses
- **Isolated Sandbox**: `axiom/experiment/sandbox.py` using AST validation and `sys.settrace()` runtime monitoring.
- **Resource Limits**: Wall-clock timeout (default 5.0s), memory limits (default 128MB), max output bytes (default 50KB).
- **Prohibited Operations**: Subprocess creation, filesystem traversal, environment secret access, and network sockets are blocked (`SECURITY_VIOLATION`).

---

## 4. Reproducibility & Independent Verification
- **Reproducibility Engine**: Runs identical experiments with recorded input/spec hashes and seeds (`REPRODUCIBLE`, `NONDETERMINISTIC`, `FAILED_REPRODUCTION`).
- **Independent Verifier**: Validates primary simulation results against independent analytical functions or alternative numerical methods (`VERIFIED`, `PARTIALLY_VERIFIED`, `FAILED_VERIFICATION`).

---

## 5. Status Lifecycle
- **Experiment Status**: `PLANNED`, `VALIDATED`, `RUNNING`, `COMPLETED`, `TIMEOUT`, `MEMORY_LIMIT_EXCEEDED`, `SECURITY_VIOLATION`, `FAILED`.
- **Observation Level**: `COMPUTATIONAL_OBSERVATION`, `EMPIRICAL_SUPPORT`, `FORMAL_VERIFICATION`, `MATHEMATICAL_PROOF`.

---

## 6. REST API Endpoints
- `POST /api/v1/experiment/design`: Formulate and validate a computational experiment plan.
- `POST /api/v1/experiment/{id}/run`: Execute experiment in safe sandbox and run verification pipeline.
- `GET /api/v1/experiment/project/{project_id}`: Retrieve project experiments and execution runs.

---

## 7. Database Schema & Migration
- Alembic Migration: `f5g67185a742_add_phase15_experiment_verification_tables.py`
- Relational tables with foreign key cascades to `projects.id` and index `project_id`, `hypothesis_id`, and `status`.
