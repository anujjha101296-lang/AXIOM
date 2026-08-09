"""Hypothesis generation and quality control for the Discovery Engine."""

from __future__ import annotations

from axiom.discovery.models import HypothesisRecord, ResearchOpportunity, _new_id

_TAUTOLOGY_MARKERS = ("equals itself", "is always itself", "all x are x")


def generate_competing_hypotheses(
    research_question: str,
    opportunity: ResearchOpportunity | None = None,
    *,
    context: str = "",
) -> list[HypothesisRecord]:
    """Generate multiple competing hypotheses (never a single path)."""
    topic = opportunity.title if opportunity else research_question
    base = research_question.strip() or topic

    candidates = [
        HypothesisRecord(
            hypothesis_id=_new_id("hyp"),
            statement=f"H1 (primary): {base} holds under the stated assumptions.",
            motivation="Primary affirmative reading of the research question.",
            assumptions=["Available evidence is representative", "No hidden confounding factors"],
            predictions=[
                f"Observable consequences of '{topic}' should appear in controlled tests.",
                "Boundary cases consistent with the claim should not immediately fail.",
            ],
            potential_counterexamples=[
                "Edge cases violating a hidden assumption",
                "Known negative results in related literature",
            ],
            required_experiments=["Small controlled computational check", "Literature consistency scan"],
            proof_strategy="Decompose into lemmas; attempt formalization if mathematical.",
            disproof_strategy="Search counterexamples and contradictory prior art.",
            expected_information_gain=0.7,
        ),
        HypothesisRecord(
            hypothesis_id=_new_id("hyp"),
            statement=f"H2 (null/alternative): {base} does not hold; observed patterns are coincidental or artifact.",
            motivation="Competing null that protects against false discovery.",
            assumptions=["Apparent support may be selection bias or insufficient search"],
            predictions=[
                "Controlled tests will fail to reproduce the claimed effect.",
                "At least one counterexample class exists.",
            ],
            potential_counterexamples=["Any confirmed instance of the claim"],
            required_experiments=["Adversarial / boundary-case search"],
            proof_strategy="N/A — seek refutation of H1.",
            disproof_strategy="Find reproducible supporting instances of H1.",
            expected_information_gain=0.75,
        ),
        HypothesisRecord(
            hypothesis_id=_new_id("hyp"),
            statement=(
                f"H3 (scoped): {base} holds only in a restricted regime "
                f"(parameter/domain subset), not generally."
            ),
            motivation="Partial-truth alternative common in scientific practice.",
            assumptions=["Claim may be over-generalized"],
            predictions=[
                "Tests succeed inside a bounded regime and fail outside it.",
            ],
            potential_counterexamples=["Instances outside the restricted regime"],
            required_experiments=["Parameter sweep across regime boundary"],
            proof_strategy="Characterize the regime formally.",
            disproof_strategy="Show failures inside the purported regime.",
            expected_information_gain=0.65,
        ),
        HypothesisRecord(
            hypothesis_id=_new_id("hyp"),
            statement=(
                f"H4 (insufficient evidence): Current knowledge is insufficient to decide '{base}'."
            ),
            motivation="Honest abstention is a valid scientific outcome.",
            assumptions=["Search or experiments so far are incomplete"],
            predictions=[
                "Neither strong support nor decisive counterexample will appear under current budget.",
            ],
            potential_counterexamples=[],
            required_experiments=["Information-gain maximizing pilot experiment"],
            proof_strategy="Defer; gather more evidence.",
            disproof_strategy="Defer.",
            expected_information_gain=0.5,
        ),
    ]

    if context.strip():
        for h in candidates:
            h.supporting_evidence_notes.append(f"Context snippet: {context.strip()[:240]}")

    return [quality_check(h) for h in candidates]


def quality_check(hypothesis: HypothesisRecord) -> HypothesisRecord:
    """Reject tautological / unclear / untestable / duplicate-like hypotheses."""
    stmt = hypothesis.statement.strip()
    if len(stmt) < 20:
        hypothesis.rejected = True
        hypothesis.rejection_reason = "Unclear / too short"
        return hypothesis
    if any(m in stmt.lower() for m in _TAUTOLOGY_MARKERS):
        hypothesis.rejected = True
        hypothesis.rejection_reason = "Tautological"
        return hypothesis
    if not hypothesis.predictions and "insufficient evidence" not in stmt.lower():
        hypothesis.rejected = True
        hypothesis.rejection_reason = "Untestable — no predictions"
        return hypothesis
    # Only reject the affirmative primary when the claim itself is labeled known-false.
    # Do not reject null / scoped / abstention hypotheses just because the research
    # question embeds a "(known false)" meta-marker — that would disable counterexample search.
    lower = stmt.lower()
    if stmt.startswith("H1") and (
        "already disproven" in lower or "known false" in lower or "always false" in lower
    ):
        hypothesis.rejected = True
        hypothesis.rejection_reason = "Marked as already disproven — do not pursue as affirmative discovery"
        return hypothesis
    return hypothesis


def active_hypotheses(hyps: list[HypothesisRecord]) -> list[HypothesisRecord]:
    return [h for h in hyps if not h.rejected]
