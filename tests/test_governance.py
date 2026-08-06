"""Tests for engineering governance system."""

from __future__ import annotations

from pathlib import Path

from axiom.governance.collectors.debt import collect_debt
from axiom.governance.council import run_council_review
from axiom.governance.review import EngineeringReview
from axiom.governance.scoring import build_priorities, compute_scores, select_top_initiative

WORKSPACE = Path(__file__).resolve().parent.parent


def test_debt_collector_returns_findings():
    result = collect_debt(WORKSPACE)
    assert result.name == "technical_debt"
    assert len(result.findings) > 0
    assert any("isolation" in f.title.lower() or "MDE" in f.title for f in result.findings)


def test_engineering_review_run_produces_scores():
    review = EngineeringReview(WORKSPACE)
    snapshot = review.run()
    scores = snapshot.scores.as_dict()
    assert "engineering_health" in scores
    assert 0 <= scores["engineering_health"] <= 100
    assert len(snapshot.collectors) == 9


def test_council_produces_nine_recommendations():
    review = EngineeringReview(WORKSPACE)
    snapshot = review.run()
    run_council_review(snapshot)
    assert len(snapshot.council) == 9
    roles = {r.role for r in snapshot.council}
    assert "CTO" in roles
    assert "Security Lead" in roles


def test_priorities_and_single_initiative():
    review = EngineeringReview(WORKSPACE)
    snapshot = review.run()
    compute_scores(snapshot)
    run_council_review(snapshot)
    build_priorities(snapshot)
    initiative, rationale = select_top_initiative(snapshot)
    assert "S0-E4" in initiative
    assert len(rationale) > 50
    assert len(snapshot.priorities) <= 25


def test_write_reports():
    review = EngineeringReview(WORKSPACE)
    snapshot = review.run()
    written = review.write_reports(snapshot)
    assert "ENGINEERING_HEALTH.md" in written
    assert written["ENGINEERING_HEALTH.md"].exists()
    content = written["ENGINEERING_HEALTH.md"].read_text()
    assert "Engineering Health Report" in content
    assert "S0-E4" in content
    assert written[".axiom/governance/dashboard.json"].exists()


def test_top_initiative_is_exactly_one():
    review = EngineeringReview(WORKSPACE)
    snapshot = review.run()
    select_top_initiative(snapshot)
    assert "EPIC-002" in snapshot.top_initiative
