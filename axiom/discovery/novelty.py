"""Conservative literature novelty assessment — never claims discovery from missing retrieval."""

from __future__ import annotations

import re

from axiom.discovery.models import NoveltyAssessment, NoveltyStatus
from axiom.skai.store import SkaiStore


def assess_novelty(
    statement: str,
    store: SkaiStore | None,
    *,
    external_search_performed: bool = False,
) -> NoveltyAssessment:
    """
    Assess novelty against local SKAI sources only unless external search is confirmed.

    Default: INSUFFICIENT_SEARCH — absence of local hits is NOT novelty.
    """
    if store is None:
        return NoveltyAssessment(
            status=NoveltyStatus.INSUFFICIENT_SEARCH,
            search_notes="No knowledge store available; cannot assess novelty.",
        )

    tokens = [t.lower() for t in re.findall(r"[a-zA-Z]{4,}", statement)]
    tokens = tokens[:20]
    sources = store.list_sources(limit=200)
    related_ids: list[str] = []
    related_titles: list[str] = []

    for src in sources:
        blob = f"{src.title} {src.identifier or ''} {src.location or ''}".lower()
        hits = sum(1 for t in tokens if t in blob)
        if hits >= 2:
            related_ids.append(src.source_id)
            related_titles.append(src.title)

    entities = store.list_entities(limit=300)
    for ent in entities:
        blob = f"{ent.title} {ent.statement}".lower()
        hits = sum(1 for t in tokens if t in blob)
        if hits >= 3 and ent.source_id not in related_ids:
            related_ids.append(ent.source_id)
            related_titles.append(ent.title)

    if related_ids:
        status = (
            NoveltyStatus.RELATED_WORK_FOUND
            if len(related_ids) < 3
            else NoveltyStatus.POSSIBLY_KNOWN
        )
        if len(related_ids) >= 5:
            status = NoveltyStatus.LIKELY_KNOWN
        return NoveltyAssessment(
            status=status,
            related_source_ids=related_ids[:20],
            related_titles=related_titles[:20],
            search_notes=(
                f"Local literature/knowledge scan matched {len(related_ids)} related items. "
                "This is NOT a claim that AXIOM discovered something new."
            ),
        )

    if not external_search_performed:
        return NoveltyAssessment(
            status=NoveltyStatus.INSUFFICIENT_SEARCH,
            search_notes=(
                "No local matches found, but external literature search was not completed. "
                "Do NOT treat missing retrieval as novelty."
            ),
        )

    return NoveltyAssessment(
        status=NoveltyStatus.NO_RELEVANT_PRIOR_WORK_FOUND,
        search_notes=(
            "External search reported no relevant prior work in the queried sources. "
            "Still not a discovery claim — search coverage may be incomplete."
        ),
    )
