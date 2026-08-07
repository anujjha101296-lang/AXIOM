"""Composite health score computation."""

from __future__ import annotations

from axiom.governance.models import (
    CollectorResult,
    Finding,
    GovernanceSnapshot,
    HealthScores,
    Severity,
)


def compute_scores(snapshot: GovernanceSnapshot) -> HealthScores:
    collectors = snapshot.collectors
    findings = snapshot.all_findings

    engineering = _base_score(78.0, findings, categories={"code_quality", "architecture", "testing"})
    product = _base_score(65.0, findings, categories={"debt", "documentation"}, extra_penalty=_product_penalty(collectors))
    research = _base_score(42.0, findings, categories={"benchmark"}, extra_penalty=_research_penalty(collectors))
    debt_score = _debt_score(findings)  # higher = worse debt
    security = _base_score(55.0, findings, categories={"security", "dependency"})
    performance = _base_score(70.0, findings, categories={"performance"}, extra_penalty=_perf_penalty(collectors))
    dx = _developer_experience(collectors, findings)
    maturity = _repository_maturity(collectors, findings)

    scores = HealthScores(
        engineering_health=_clamp(engineering),
        product_health=_clamp(product),
        research_capability=_clamp(research),
        technical_debt=_clamp(debt_score),
        security=_clamp(security),
        performance=_clamp(performance),
        developer_experience=_clamp(dx),
        repository_maturity=_clamp(maturity),
    )
    snapshot.scores = scores
    return scores


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _base_score(
    baseline: float,
    findings: list[Finding],
    categories: set[str] | None = None,
    extra_penalty: float = 0.0,
) -> float:
    penalty = extra_penalty
    for f in findings:
        if categories and f.category.value not in categories:
            continue
        weight = {
            Severity.CRITICAL: 1.0,
            Severity.HIGH: 0.7,
            Severity.MEDIUM: 0.4,
            Severity.LOW: 0.15,
            Severity.INFO: 0.05,
        }.get(f.severity, 0.2)
        penalty += f.score_impact * weight
    return baseline - penalty


def _debt_score(findings: list[Finding]) -> float:
    """Technical debt score: 0 = no debt, 100 = severe debt."""
    debt_findings = [f for f in findings if f.category.value == "debt"]
    total = sum(f.score_impact for f in debt_findings)
    return _clamp(min(total * 2.5, 95))


def _product_penalty(collectors: dict[str, CollectorResult]) -> float:
    penalty = 8.0  # MVP P0 blockers baseline
    testing = collectors.get("testing")
    if testing:
        cov = _get_metric(testing, "line_coverage_pct", 70)
        if cov < 70:
            penalty += (70 - cov) * 0.1
    return penalty


def _research_penalty(collectors: dict[str, CollectorResult]) -> float:
    bench = collectors.get("benchmarks")
    if not bench:
        return 20.0
    regressions = _get_metric(bench, "benchmark_regressions", 0)
    return regressions * 8.0


def _perf_penalty(collectors: dict[str, CollectorResult]) -> float:
    perf = collectors.get("performance")
    if not perf:
        return 0.0
    import_ms = _get_metric(perf, "cold_import_ms", 0)
    if import_ms > 5000:
        return 15.0
    if import_ms > 3000:
        return 8.0
    return 0.0


def _developer_experience(collectors: dict[str, CollectorResult], findings: list[Finding]) -> float:
    baseline = 72.0
    docs = collectors.get("documentation")
    if docs:
        missing = _get_metric(docs, "missing_required_docs", 0)
        baseline -= missing * 5
        coverage = _get_metric(docs, "module_docstring_coverage_pct", 50)
        if coverage < 50:
            baseline -= (50 - coverage) * 0.2
    arch = collectors.get("architecture")
    if arch:
        adrs = _get_metric(arch, "architecture_decision_records", 0)
        if adrs < 3:
            baseline -= 5
    ci = collectors.get("testing")
    if ci and _get_metric(ci, "ci_workflow", 0) < 1:
        baseline -= 10
    for f in findings:
        if f.category.value == "documentation" and f.severity in (Severity.HIGH, Severity.CRITICAL):
            baseline -= 3
    return _clamp(baseline)


def _repository_maturity(collectors: dict[str, CollectorResult], findings: list[Finding]) -> float:
    score = 50.0
    if _get_metric(collectors.get("testing"), "ci_workflow", 0):
        score += 15
    cov = _get_metric(collectors.get("testing"), "line_coverage_pct", 0)
    score += min(cov, 100) * 0.2
    if _get_metric(collectors.get("security"), "security_workflow", 0):
        score += 10
    adrs = _get_metric(collectors.get("architecture"), "architecture_decision_records", 0)
    score += min(adrs, 5) * 2
    vulns = _get_metric(collectors.get("dependencies"), "python_vulnerabilities", 0)
    score -= min(vulns * 3, 15)
    critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
    score -= critical_count * 5
    return _clamp(score)


def _get_metric(collector: CollectorResult | None, name: str, default: float) -> float:
    if not collector:
        return default
    for m in collector.metrics:
        if m.name == name:
            try:
                return float(m.value)
            except (TypeError, ValueError):
                return default
    return default


def build_priorities(snapshot: GovernanceSnapshot) -> list[tuple[int, str, str]]:
    """Rank top priorities from findings and council recommendations."""
    items: list[tuple[float, str, str]] = []

    for f in snapshot.all_findings:
        priority_score = f.score_impact * {
            Severity.CRITICAL: 10,
            Severity.HIGH: 7,
            Severity.MEDIUM: 4,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }.get(f.severity, 1)
        items.append((priority_score, f.title, f.recommendation))

    for rec in snapshot.council:
        items.append((rec.priority * 5, f"[{rec.role}] {rec.recommendation}", rec.rationale))

    items.sort(key=lambda x: x[0], reverse=True)
    seen: set[str] = set()
    ranked: list[tuple[int, str, str]] = []
    for _score, title, action in items:
        if title in seen:
            continue
        seen.add(title)
        ranked.append((len(ranked) + 1, title, action))
        if len(ranked) >= 25:
            break
    snapshot.priorities = ranked
    return ranked


def select_top_initiative(snapshot: GovernanceSnapshot) -> tuple[str, str]:
    """Select exactly ONE highest-leverage engineering initiative."""
    initiative = "S0-E4 — EPIC-002 Evidence Integration Gate"
    rationale = (
        "Completing S0-E4 is the highest-leverage engineering investment because it establishes "
        "evidence_state, benchmark_count, and stated limitations on every capability score. "
        "Without this gate, evaluation outputs, governance metrics, and research claims cannot "
        "be trusted — undermining every downstream initiative including H1-OBS provenance, "
        "autonomous loop credibility, and external pilot readiness. It is reversible, "
        "testable, and already ranked #6 (ready) in TASK_QUEUE.md with S0-E2 and S0-E3 complete."
    )
    snapshot.top_initiative = initiative
    snapshot.top_initiative_rationale = rationale
    return initiative, rationale
