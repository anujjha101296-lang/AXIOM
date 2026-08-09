"""Known-result and literature maps — categories never merged."""

from __future__ import annotations

from typing import Any

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
    if any(m in blob for m in ("historical", "historically", "classical conjecture")):
        results.append(
            KnownResult(
                result_id=_new_id("kr"),
                statement="Historical conjecture context — reproduce known resolution; do not claim novelty",
                bucket=KnowledgeBucket.UNKNOWN,
                kind=ResultKind.UNVERIFIED_CLAIM,
                evidence_notes="Level-3+ campaigns target reproduction of known history, not discovery",
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


def enrich_literature_map(
    problem: OpenProblem,
    *,
    db_path: str,
    seed_text: str = "",
    source_urls: list[str] | None = None,
) -> tuple[list[LiteratureEntry], list[KnownResult], list[str]]:
    """Enrich literature via SKAI + formal library search (no rebuild).

    Returns (literature, extra_known_results, gap_notes).
    WEB / seed acquisitions remain UNTRUSTED. Formal library hits are local catalog
    references — not independently re-proven.
    """
    entries = list(problem.literature) if problem.literature else build_literature_map(problem, seed_text)
    extra_kr: list[KnownResult] = []
    gaps: list[str] = []

    try:
        from axiom.skai.models import SourceType
        from axiom.skai.orchestrator import SkaiOrchestrator

        skai = SkaiOrchestrator(db_path)
        if seed_text.strip():
            skai.acquire_from_text(
                title=f"OPL seed: {problem.title[:80]}",
                content=seed_text,
                research_question=problem.informal_statement,
                source_type=SourceType.RESEARCHER_DOCUMENT,
                campaign_id=problem.campaign_ids[0] if problem.campaign_ids else None,
                bridge_to_egs=False,
                bridge_to_er=False,
            )

        for url in source_urls or []:
            url = (url or "").strip()
            if not url.startswith("https://"):
                gaps.append(f"Skipped non-HTTPS source URL: {url[:80]}")
                continue
            try:
                acq = skai.acquire_from_url(
                    url,
                    research_question=problem.informal_statement,
                    campaign_id=problem.campaign_ids[0] if problem.campaign_ids else None,
                    bridge_to_egs=False,
                    bridge_to_er=False,
                )
                entries.append(
                    LiteratureEntry(
                        entry_id=_new_id("lit"),
                        title=f"Allowlisted web acquisition: {url[:120]}",
                        url=getattr(acq, "source_url", None) or url,
                        claims=[f"acquisition_status={getattr(acq, 'status', 'unknown')}"],
                        methods=["skai.acquire_from_url", "allowlisted HTTPS fetch"],
                        limitations=[
                            "UNTRUSTED web content",
                            "Instruction-pattern scan applied at acquisition",
                            "Not peer-reviewed by AXIOM",
                        ],
                        provenance="skai_web",
                        untrusted=True,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                gaps.append(f"URL acquisition failed: {str(exc)[:160]}")

        synth = skai.synthesize_knowledge(
            problem.informal_statement,
            campaign_id=problem.campaign_ids[0] if problem.campaign_ids else None,
        )
        from axiom.skai.retrieval import retrieve_for_research

        survey = retrieve_for_research(
            skai.store,
            problem.informal_statement,
            goal_type="survey_literature",
            campaign_id=problem.campaign_ids[0] if problem.campaign_ids else None,
            limit=20,
        )
        retrieval = survey or synth.get("retrieval") or {}
        for ent in (retrieval.get("entities") or [])[:12]:
            if not isinstance(ent, dict):
                continue
            title = ent.get("title") or ent.get("name") or ent.get("entity_id") or "SKAI entity"
            claims = []
            if ent.get("statement"):
                claims.append(str(ent["statement"])[:400])
            if ent.get("content"):
                claims.append(str(ent["content"])[:400])
            entries.append(
                LiteratureEntry(
                    entry_id=_new_id("lit"),
                    title=str(title)[:200],
                    claims=claims or ["SKAI retrieved entity — see store"],
                    methods=["skai.retrieve_for_research(survey_literature)"],
                    limitations=["Local SKAI corpus only unless web URL acquired"],
                    provenance="skai_retrieve",
                    untrusted=True,
                )
            )
        for g in (synth.get("gaps") or [])[:8]:
            if isinstance(g, dict):
                gaps.append(str(g.get("description") or g.get("gap_type") or g)[:200])
            else:
                gaps.append(str(g)[:200])
        coverage = synth.get("coverage") or {}
        if coverage:
            entries.append(
                LiteratureEntry(
                    entry_id=_new_id("lit"),
                    title="SKAI coverage estimate",
                    claims=[f"coverage={coverage}"[:400]],
                    methods=["skai.estimate_coverage"],
                    limitations=["Coverage estimate is computational, not exhaustive prior art"],
                    provenance="skai_coverage",
                    untrusted=True,
                )
            )
    except Exception as exc:  # noqa: BLE001
        gaps.append(f"SKAI enrichment unavailable: {str(exc)[:160]}")

    # Formal theorem library (local catalog)
    try:
        from axiom.formal_math.library_search import search_library

        domain = problem.domain if problem.domain in {
            "algebra", "number_theory", "group_theory", "analysis", "topology",
        } else None
        hits = search_library(problem.informal_statement, domain=domain, limit=5)
        if not hits and problem.formal_statement:
            hits = search_library(problem.formal_statement, domain=domain, limit=5)
        for hit in hits:
            entries.append(
                LiteratureEntry(
                    entry_id=_new_id("lit"),
                    title=f"Formal library: {hit.get('name', 'entry')}",
                    claims=[str(hit.get("statement", ""))[:400]],
                    methods=["formal_math.library_search", f"strength={hit.get('strength')}"],
                    limitations=[
                        "Local catalog match — not Mathlib/Lean re-verification",
                        f"relevance_score={hit.get('relevance_score')}",
                    ],
                    provenance="formal_library",
                    untrusted=False,
                )
            )
            strength = str(hit.get("strength", "lemma")).lower()
            kind = ResultKind.THEOREM if strength == "theorem" else ResultKind.LEMMA
            extra_kr.append(
                KnownResult(
                    result_id=_new_id("kr"),
                    statement=str(hit.get("statement", hit.get("name", "")))[:300],
                    bucket=KnowledgeBucket.PROVEN,
                    kind=kind,
                    evidence_notes=(
                        "Matched local formal library catalog. "
                        "Not independently re-proven in this campaign."
                    ),
                    source_refs=[f"formal_library:{hit.get('name')}"],
                )
            )
        if not hits:
            gaps.append("Formal library search returned no catalog matches")
    except Exception as exc:  # noqa: BLE001
        gaps.append(f"Formal library search failed: {str(exc)[:160]}")

    # Drop placeholder once we have non-placeholder provenance
    real = [e for e in entries if e.provenance != "placeholder"]
    if real:
        entries = real
    else:
        # Keep honesty placeholder
        if not any(e.provenance == "placeholder" for e in entries):
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

    # Deduplicate by title+first claim
    seen: set[str] = set()
    deduped: list[LiteratureEntry] = []
    for e in entries:
        key = f"{e.title}|{(e.claims[0] if e.claims else '')[:80]}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    return deduped, extra_kr, gaps


def known_results_by_bucket(results: list[KnownResult]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {b.value: [] for b in KnowledgeBucket}
    for r in results:
        out[r.bucket.value].append(r.to_dict())
    return out


def literature_summary(entries: list[LiteratureEntry]) -> dict[str, Any]:
    return {
        "count": len(entries),
        "by_provenance": {
            p: sum(1 for e in entries if e.provenance == p)
            for p in sorted({e.provenance for e in entries})
        },
        "untrusted_count": sum(1 for e in entries if e.untrusted),
        "has_formal_library": any(e.provenance == "formal_library" for e in entries),
        "has_skai": any(e.provenance.startswith("skai") for e in entries),
        "placeholder_remaining": any(e.provenance == "placeholder" for e in entries),
    }
