"""Known-result and literature maps — categories never merged."""

from __future__ import annotations

from axiom.open_problems.models import (
    KnowledgeBucket,
    KnownResult,
    LiteratureEntry,
    OpenProblem,
    ResultKind,
    _new_id,
)


def build_known_result_map(problem: OpenProblem, seed_text: str = "") -> list[KnownResult]:
    """Separate proven / disproven / conjectured / empirical / unknown."""
    results: list[KnownResult] = []
    blob = f"{problem.informal_statement}\n{seed_text}\n{problem.known_status}".lower()

    if any(m in blob for m in ("known false", "always false", "disproven", "counterexample")):
        results.append(
            KnownResult(
                result_id=_new_id("kr"),
                statement="Claim marked as known-false / disproven in intake material",
                bucket=KnowledgeBucket.DISPROVEN,
                kind=ResultKind.DISPROOF,
                evidence_notes="Intake markers only — not independent verification yet",
            )
        )
    if "conjecture" in blob or "open" in blob:
        results.append(
            KnownResult(
                result_id=_new_id("kr"),
                statement=problem.understanding.required_conclusion or problem.informal_statement[:200],
                bucket=KnowledgeBucket.CONJECTURED,
                kind=ResultKind.CONJECTURE,
                evidence_notes="Treated as conjecture until verified or refuted",
            )
        )
    if any(m in blob for m in ("theorem", "lemma", "proven", "proved")):
        results.append(
            KnownResult(
                result_id=_new_id("kr"),
                statement="Prior theorem/lemma referenced in statement",
                bucket=KnowledgeBucket.PROVEN,
                kind=ResultKind.THEOREM,
                evidence_notes="Referenced as known — not re-proven here",
            )
        )
    if any(m in blob for m in ("numerical", "empiric", "observed", "simulation")):
        results.append(
            KnownResult(
                result_id=_new_id("kr"),
                statement="Empirical / numerical observation referenced",
                bucket=KnowledgeBucket.EMPIRICALLY_OBSERVED,
                kind=ResultKind.NUMERICAL_EVIDENCE,
                evidence_notes="Computational evidence ≠ proof",
            )
        )

    # Always record residual unknown
    results.append(
        KnownResult(
            result_id=_new_id("kr"),
            statement="What remains unknown after intake",
            bucket=KnowledgeBucket.UNKNOWN,
            kind=ResultKind.UNVERIFIED_CLAIM,
            evidence_notes="Default residual unknown bucket",
        )
    )
    return results


def build_literature_map(problem: OpenProblem, seed_text: str = "") -> list[LiteratureEntry]:
    """Seed literature entries from provided text — marked UNTRUSTED until curated."""
    entries: list[LiteratureEntry] = []
    if seed_text.strip():
        entries.append(
            LiteratureEntry(
                entry_id=_new_id("lit"),
                title=f"Seed material for: {problem.title[:80]}",
                claims=[seed_text.strip()[:400]],
                methods=["researcher-provided seed"],
                limitations=["Not peer-reviewed acquisition; treat as UNTRUSTED"],
                provenance="intake_seed",
                untrusted=True,
            )
        )
    entries.append(
        LiteratureEntry(
            entry_id=_new_id("lit"),
            title="External literature search incomplete",
            claims=[],
            methods=[],
            limitations=["Missing retrieval is not novelty"],
            provenance="placeholder",
            untrusted=True,
        )
    )
    return entries


def known_results_by_bucket(results: list[KnownResult]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {b.value: [] for b in KnowledgeBucket}
    for r in results:
        out[r.bucket.value].append(r.to_dict())
    return out
