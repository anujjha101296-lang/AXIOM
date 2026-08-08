# Research Kernel Plugin API

Domain plugins extend the Research Kernel without modifying core architecture. Implement the `ResearchDomainPlugin` protocol and register via `register_plugin()`.

## Protocol

```python
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class ResearchDomainPlugin(Protocol):
    plugin_id: str       # Unique identifier, e.g. "mathematics"
    domain: str          # Domain label, e.g. "mathematics"
    name: str            # Human-readable name
    version: str         # Semver, e.g. "1.0.0"
    description: str     # Short description

    def decompose_goal(self, objective: str, context: dict[str, Any]) -> dict[str, Any]: ...
    def research_plan(self, decomposition: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]: ...
    def acquire_evidence(self, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]: ...
    def orchestration_tasks(self, plan: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]: ...
    def verify(self, evidence: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]: ...
    def benchmarks(self) -> list[dict[str, Any]]: ...
    def run_benchmark(self, benchmark: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]: ...
    def generate_domain_report(self, context: dict[str, Any]) -> str: ...
```

## Method Contracts

### `decompose_goal(objective, context) → dict`

Called during **Stage 1: Goal Decomposition**.

**Returns:** Decomposition artifact stored in `run.context["decomposition"]`.

**Required keys (recommended):**
- `primary_question` — Restated research question
- `sub_goals` — List of actionable sub-goals
- `success_criteria` — Measurable completion criteria

### `research_plan(decomposition, context) → dict`

Called during **Stage 2: Research Planning**.

**Returns:** Plan artifact stored in `run.context["plan"]`.

### `acquire_evidence(plan, context) → dict`

Called during **Stage 3: Evidence Acquisition**.

**Returns:** Evidence artifact stored in `run.context["evidence"]`. Include `evidence_tier` key (`verified`, `simulated`, etc.).

### `orchestration_tasks(plan, context) → list[dict]`

Called during **Stage 4: Multi-Agent Orchestration**.

**Returns:** Task definitions for `WorkflowScheduler`. Each task dict:

```python
{
    "id": "unique_task_id",
    "title": "Task title",
    "description": "Optional description",
    "worker_type": "researcher",  # optional, default "researcher"
    "depends_on": ["prior_task_id"],
}
```

### `verify(evidence, context) → dict`

Called during **Stage 5: Verification Pipeline**.

**Returns:** Verification result stored in `run.context["verification"]`. Include `passed: bool`.

### `benchmarks() → list[dict]`

Called during **Stage 9: Benchmark Execution** setup.

**Returns:** Benchmark definitions. Each benchmark:

```python
{
    "id": "unique_benchmark_id",
    "name": "Human-readable name",
    "question": "What is being tested",
    "expected": "Expected outcome",
}
```

### `run_benchmark(benchmark, context) → dict`

Called once per benchmark during Stage 9.

**Returns:**
```python
{
    "benchmark_id": "...",
    "passed": True,
    "score": 1.0,
    "evidence_tier": "verified",
}
```

### `generate_domain_report(context) → str`

Called during **Stage 10: Report Generation**.

**Returns:** Markdown section appended to the kernel report. Access prior stage artifacts via `context` (e.g. `context["decomposition"]`, `context["verification"]`, `context["benchmark_results"]`).

## Registration

```python
from axiom.research_kernel import register_plugin

class MyDomainPlugin:
    plugin_id = "my_domain"
    domain = "my_domain"
    name = "My Domain Research"
    version = "1.0.0"
    description = "Custom research domain"
    # ... implement all methods

register_plugin(MyDomainPlugin())
```

Built-in plugins are registered in `axiom/research_kernel/registry.py`.

## Context Object

The `context` dict is shared across all stages for a run. The kernel populates:

| Key | Set By | Contents |
|-----|--------|----------|
| `decomposition` | Stage 1 | Goal decomposition |
| `plan` | Stage 2 | Research plan |
| `evidence` | Stage 3 | Acquired evidence |
| `orchestration` | Stage 4 | Workflow schedule summary |
| `verification` | Stage 5 | Domain verification |
| `truthfulness` | Stage 5 | Epistemic assignment |
| `memory` | Stage 6 | Working memory snapshot |
| `reflections` | Stage 7 | Reflection notes |
| `learning` | Stage 8 | Self-improvement audit |
| `benchmark_results` | Stage 9 | Benchmark scores |

Plugins may read and write additional keys in `context` during their methods.

## Example: Minimal Plugin

```python
class MinimalPlugin:
    plugin_id = "minimal"
    domain = "minimal"
    name = "Minimal Plugin"
    version = "1.0.0"
    description = "Smallest valid plugin"

    def decompose_goal(self, objective, context):
        return {"primary_question": objective, "sub_goals": ["investigate"], "success_criteria": ["done"]}

    def research_plan(self, decomposition, context):
        return {"phases": [{"name": "investigate"}]}

    def acquire_evidence(self, plan, context):
        return {"sources": [], "evidence_tier": "simulated"}

    def orchestration_tasks(self, plan, context):
        return [{"id": "t1", "title": "Investigate", "depends_on": []}]

    def verify(self, evidence, context):
        return {"passed": True, "verified_claims": 0}

    def benchmarks(self):
        return [{"id": "b1", "name": "Smoke test", "question": "pass?", "expected": "yes"}]

    def run_benchmark(self, benchmark, context):
        return {"benchmark_id": benchmark["id"], "passed": True, "score": 1.0, "evidence_tier": "simulated"}

    def generate_domain_report(self, context):
        return "## Minimal Domain\n\nNo findings.\n"
```

## Versioning

- Plugin `version` follows semver.
- Breaking protocol changes require a kernel major version bump.
- The kernel manifest (`GET /kernel/manifest`) lists all registered plugins and their versions.
