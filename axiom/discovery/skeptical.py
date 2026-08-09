"""Skeptical scientist — adversarial review that is not rewarded for agreement."""

from __future__ import annotations

from axiom.discovery.models import AttackRecord, Discovery, HypothesisRecord, _new_id


def skeptical_review(discovery: Discovery, hypothesis: HypothesisRecord) -> AttackRecord:
    """Produce an independent attack focused on weaknesses."""
    issues: list[str] = []

    if not hypothesis.assumptions:
        issues.append("No explicit assumptions listed — hidden assumptions likely.")
    else:
        issues.append(f"Assumptions to stress-test: {', '.join(hypothesis.assumptions[:3])}")

    if not hypothesis.potential_counterexamples:
        issues.append("No potential counterexamples proposed — claim may be overconfident.")
    if hypothesis.expected_information_gain < 0.4:
        issues.append("Low expected information gain — weak experimental leverage.")
    if discovery.novelty.status.value == "INSUFFICIENT_SEARCH":
        issues.append("Novelty search insufficient — prior art may exist.")
    if discovery.novelty.status.value in {"LIKELY_KNOWN", "POSSIBLY_KNOWN", "RELATED_WORK_FOUND"}:
        issues.append(
            f"Related prior work found ({discovery.novelty.status.value}) — "
            "do not treat as novel discovery."
        )
    if not hypothesis.predictions:
        issues.append("No testable predictions — hypothesis may be unfalsifiable.")

    # Always challenge the primary affirmative reading.
    issues.append("Require independent reproduction before any VERIFIED status.")
    issues.append("Computational evidence must not be labeled as formal proof.")

    outcome = "challenging"
    if "INSUFFICIENT_SEARCH" in discovery.novelty.status.value:
        outcome = "challenging"

    return AttackRecord(
        attack_id=_new_id("atk"),
        attack_type="skeptical",
        summary=" | ".join(issues),
        outcome=outcome,
    )
