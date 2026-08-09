"""Verification score calculation — never hide missing verification."""

from __future__ import annotations

from axiom.vfactory.models import (
    CapabilityRecord,
    VerificationDomain,
    VerificationScore,
    VerificationState,
)


def _score_domain(caps: list[CapabilityRecord], domain: str) -> VerificationScore:
    """Score capabilities in a domain (0.0–1.0)."""
    domain_caps = [c for c in caps if c.domain == domain]
    if not domain_caps:
        return VerificationScore(
            domain=VerificationDomain(domain) if domain in VerificationDomain._value2member_map_ else VerificationDomain.OVERALL,
            score=0.0,
            passing=0,
            total=0,
            untested=0,
            regressions=0,
            details={"note": "no capabilities registered"},
        )

    passing = sum(
        1 for c in domain_caps
        if c.status in (VerificationState.VERIFIED, VerificationState.PASSING)
    )
    partial = sum(1 for c in domain_caps if c.status == VerificationState.PARTIAL)
    untested = sum(
        1 for c in domain_caps
        if c.status in (VerificationState.UNTESTED, VerificationState.UNKNOWN)
    )
    regressions = sum(1 for c in domain_caps if c.status == VerificationState.REGRESSION)

    # Partial counts as half credit
    score = (passing + partial * 0.5) / len(domain_caps)

    return VerificationScore(
        domain=VerificationDomain(domain) if domain in VerificationDomain._value2member_map_ else VerificationDomain.OVERALL,
        score=round(score, 4),
        passing=passing,
        total=len(domain_caps),
        untested=untested,
        regressions=regressions,
        details={"partial": partial},
    )


def compute_all_scores(caps: list[CapabilityRecord]) -> list[VerificationScore]:
    """Compute per-domain and overall verification scores."""
    domains = sorted({c.domain for c in caps})
    scores = [_score_domain(caps, d) for d in domains]

    if caps:
        passing = sum(
            1 for c in caps
            if c.status in (VerificationState.VERIFIED, VerificationState.PASSING)
        )
        partial = sum(1 for c in caps if c.status == VerificationState.PARTIAL)
        untested = sum(
            1 for c in caps
            if c.status in (VerificationState.UNTESTED, VerificationState.UNKNOWN)
        )
        regressions = sum(1 for c in caps if c.status == VerificationState.REGRESSION)
        overall_score = (passing + partial * 0.5) / len(caps)
        scores.append(
            VerificationScore(
                domain=VerificationDomain.OVERALL,
                score=round(overall_score, 4),
                passing=passing,
                total=len(caps),
                untested=untested,
                regressions=regressions,
                details={"partial": partial},
            )
        )
    return scores
