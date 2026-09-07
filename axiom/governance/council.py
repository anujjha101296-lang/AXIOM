"""Engineering Council — domain review roles and recommendations."""

from __future__ import annotations

from axiom.governance.models import CollectorResult, CouncilRecommendation, GovernanceSnapshot

COUNCIL_ROLES = [
    ("CTO", "Strategic alignment, integrity, and sequencing"),
    ("Platform Lead", "Core platform, APIs, and shared infrastructure"),
    ("Backend Lead", "Python services, persistence, and data models"),
    ("Frontend Lead", "Next.js UI, UX, and client integration"),
    ("AI Systems Lead", "Model gateway, research loop, and evaluation"),
    ("Infrastructure Lead", "CI/CD, containers, observability, and deploy"),
    ("Security Lead", "Auth, tenancy, secrets, and dependency risk"),
    ("QA Lead", "Test strategy, coverage, and regression gates"),
    ("Product Engineering Lead", "Research workspace wedge and MVP readiness"),
]


def run_council_review(snapshot: GovernanceSnapshot) -> list[CouncilRecommendation]:
    collectors = snapshot.collectors
    recs: list[CouncilRecommendation] = []

    recs.append(_cto_review(collectors))
    recs.append(_platform_review(collectors))
    recs.append(_backend_review(collectors))
    recs.append(_frontend_review(collectors))
    recs.append(_ai_systems_review(collectors))
    recs.append(_infrastructure_review(collectors))
    recs.append(_security_review(collectors))
    recs.append(_qa_review(collectors))
    recs.append(_product_engineering_review(collectors))

    snapshot.council = recs
    return recs


def _cto_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    debt = collectors.get("technical_debt")
    s0_e4_open = any("S0-E4" in f.title for f in (debt.findings if debt else []))
    return CouncilRecommendation(
        role="CTO",
        domain="Strategic alignment, integrity, and sequencing",
        priority=1 if s0_e4_open else 2,
        recommendation="Complete S0-E4 EPIC-002 evidence integration gate before feature expansion.",
        rationale=(
            "Integrity gates compound: ungated capability scores undermine research credibility, "
            "eval API honesty, and governance metrics. S0-E4 unlocks H1-OBS provenance."
        ),
    )


def _platform_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    arch = collectors.get("architecture")
    mounted = _metric(arch, "mounted_routers", 0)
    return CouncilRecommendation(
        role="Platform Lead",
        domain="Core platform, APIs, and shared infrastructure",
        priority=2,
        recommendation="Audit router mounting in api_gateway/main.py; align e2e expectations with production surface.",
        rationale=f"{mounted} routers mounted; MDE and workflow routes partially exposed.",
    )


def _backend_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    testing = collectors.get("testing")
    cov = _metric(testing, "line_coverage_pct", 0)
    return CouncilRecommendation(
        role="Backend Lead",
        domain="Python services, persistence, and data models",
        priority=2,
        recommendation="Add user_id scoping to research store and workflow engine unit tests.",
        rationale=f"Line coverage at {cov}%; tenancy gap is the highest backend risk.",
    )


def _frontend_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    deps = collectors.get("dependencies")
    npm_vulns = _metric(deps, "npm_high_vulnerabilities", 0)
    return CouncilRecommendation(
        role="Frontend Lead",
        domain="Next.js UI, UX, and client integration",
        priority=3,
        recommendation="Fix waitlist form; add UI Dockerfile; wire demo/research mode banners consistently.",
        rationale=f"UI npm high/critical vulns: {npm_vulns}; landing waitlist is non-functional.",
    )


def _ai_systems_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    bench = collectors.get("benchmarks")
    regressions = _metric(bench, "benchmark_regressions", 0)
    return CouncilRecommendation(
        role="AI Systems Lead",
        domain="Model gateway, research loop, and evaluation",
        priority=1 if regressions else 2,
        recommendation="Wire ModelClient to research loop workers; gate eval scores with evidence_state per S0-E4.",
        rationale=f"Benchmark regressions: {regressions}; loop workers remain heuristic without LLM path.",
    )


def _infrastructure_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    perf = collectors.get("performance")
    import_ms = _metric(perf, "cold_import_ms", 0)
    return CouncilRecommendation(
        role="Infrastructure Lead",
        domain="CI/CD, containers, observability, and deploy",
        priority=3,
        recommendation="Complete Grafana provisioning; add governance CI job; lazy-import heavy scientific libs.",
        rationale=f"Cold import {import_ms:.0f}ms; compose stack incomplete for full observability.",
    )


def _security_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    sec = collectors.get("security")
    workflow = _metric(sec, "security_workflow", 0)
    return CouncilRecommendation(
        role="Security Lead",
        domain="Auth, tenancy, secrets, and dependency risk",
        priority=1,
        recommendation="Block production startup on default JWT secret; implement per-user data isolation.",
        rationale=f"Security workflow present: {bool(workflow)}; tenancy is P0 for any external access.",
    )


def _qa_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    testing = collectors.get("testing")
    collected = _metric(testing, "tests_collected", 0)
    return CouncilRecommendation(
        role="QA Lead",
        domain="Test strategy, coverage, and regression gates",
        priority=2,
        recommendation="Maintain 70% coverage gate; add workflow tests; track e2e gap separately in governance reports.",
        rationale=f"{collected} core tests collected; e2e documents platform surface debt honestly.",
    )


def _product_engineering_review(collectors: dict[str, CollectorResult]) -> CouncilRecommendation:
    docs = collectors.get("documentation")
    missing = _metric(docs, "missing_required_docs", 0)
    return CouncilRecommendation(
        role="Product Engineering Lead",
        domain="Research workspace wedge and MVP readiness",
        priority=2,
        recommendation="Ship contributor onboarding docs; resolve P0 MVP blockers before public alpha.",
        rationale=f"Missing required docs: {missing}; workspace wedge is demo-ready, not production-ready.",
    )


def _metric(collector: CollectorResult | None, name: str, default: float) -> float:
    if not collector:
        return default
    for m in collector.metrics:
        if m.name == name:
            try:
                return float(m.value)
            except (TypeError, ValueError):
                return default
    return default
