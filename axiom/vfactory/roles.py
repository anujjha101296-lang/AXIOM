"""Multi-agent verification team — controlled worker roles (VF §3)."""

from __future__ import annotations

from typing import Any

from axiom.vfactory.models import VerificationRole


def default_verification_roles() -> list[dict[str, Any]]:
    """Logical verification roles with scope and budgets — not unlimited agents."""
    return [
        {
            "role": VerificationRole.TEST_ARCHITECT.value,
            "scope": "Full verification pyramid and registry",
            "test_objectives": ["Map capabilities to tests", "Define acceptance criteria"],
            "allowed_tools": ["registry", "pyramid", "scorer"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 300,
            "expected_output": "Verification plan and score",
        },
        {
            "role": VerificationRole.BACKEND_QA.value,
            "scope": "API and service integration",
            "test_objectives": ["API contract", "Health endpoints", "Auth"],
            "allowed_tools": ["httpx", "pytest", "health_checks"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 600,
        },
        {
            "role": VerificationRole.FRONTEND_QA.value,
            "scope": "UI routes and workflows",
            "test_objectives": ["Route reachability", "No dead buttons"],
            "allowed_tools": ["playwright", "route_scan"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 600,
        },
        {
            "role": VerificationRole.DATABASE_QA.value,
            "scope": "Migrations, constraints, isolation",
            "test_objectives": ["Fresh install", "Migration", "FK integrity"],
            "allowed_tools": ["sqlite", "postgres", "migration_runner"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 300,
        },
        {
            "role": VerificationRole.AI_QA.value,
            "scope": "LLM outputs and regression sets",
            "test_objectives": ["Fixed eval sets", "Regression detection"],
            "allowed_tools": ["ai_regression", "golden_sets"],
            "resource_budget_usd": 1.0,
            "timeout_seconds": 900,
        },
        {
            "role": VerificationRole.AGENT_QA.value,
            "scope": "Agent safety and termination",
            "test_objectives": ["Loop detection", "Budget exhaustion", "Cancellation"],
            "allowed_tools": ["agent_harness", "chaos"],
            "resource_budget_usd": 0.5,
            "timeout_seconds": 600,
        },
        {
            "role": VerificationRole.SECURITY_TESTER.value,
            "scope": "Auth, isolation, injection",
            "test_objectives": ["Tenant isolation", "Secret exposure", "Injection"],
            "allowed_tools": ["security_scan", "auth_tests"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 300,
        },
        {
            "role": VerificationRole.INFRASTRUCTURE_TESTER.value,
            "scope": "Docker, K8s, health probes",
            "test_objectives": ["Container build", "Health check", "Restart"],
            "allowed_tools": ["docker", "k8s_validate"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 600,
        },
        {
            "role": VerificationRole.PERFORMANCE_TESTER.value,
            "scope": "Latency and throughput baselines",
            "test_objectives": ["API latency", "Search latency"],
            "allowed_tools": ["locust", "benchmark"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 900,
        },
        {
            "role": VerificationRole.RESEARCH_EVALUATOR.value,
            "scope": "Scientific capability benchmarks",
            "test_objectives": ["Known input/expected result", "Evidence quality"],
            "allowed_tools": ["research_benchmarks", "campaign_fixtures"],
            "resource_budget_usd": 0.5,
            "timeout_seconds": 900,
        },
        {
            "role": VerificationRole.SCIENTIFIC_INTEGRITY.value,
            "scope": "Formal proofs and reproducibility",
            "test_objectives": ["Theorem prover validation", "Proof reproduction"],
            "allowed_tools": ["fmtp_suite", "proof_compiler"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 600,
        },
        {
            "role": VerificationRole.RELEASE_ENGINEER.value,
            "scope": "Release candidate gates",
            "test_objectives": ["All gates pass", "Block on critical failure"],
            "allowed_tools": ["release_gates", "ci"],
            "resource_budget_usd": 0.0,
            "timeout_seconds": 1800,
        },
    ]
