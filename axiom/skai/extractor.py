"""Paper structure extraction (SKAI §5)."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from axiom.skai.models import EntityType, KnowledgeEntity, _new_id


MATH_ENVIRONMENTS = {
    "theorem": EntityType.THEOREM,
    "thm": EntityType.THEOREM,
    "lemma": EntityType.LEMMA,
    "corollary": EntityType.THEOREM,
    "definition": EntityType.DEFINITION,
    "defn": EntityType.DEFINITION,
    "conjecture": EntityType.CONJECTURE,
    "proposition": EntityType.THEOREM,
}

EXPERIMENTAL_SECTIONS = {
    "hypothesis": EntityType.HYPOTHESIS,
    "method": EntityType.METHOD,
    "experiment": EntityType.EXPERIMENT,
    "result": EntityType.RESULT,
    "limitation": EntityType.LIMITATION,
}


def extract_from_latex(tex_content: str, source_id: str) -> list[KnowledgeEntity]:
    """Extract mathematical structure from LaTeX content."""
    entities: list[KnowledgeEntity] = []
    pattern = re.compile(
        r"\\begin\{(theorem|thm|lemma|corollary|definition|defn|conjecture|proposition)\}"
        r"(?:\[([^\]]*)\])?"
        r"(.*?)\\end\{\1\}",
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(tex_content):
        env = match.group(1).lower()
        label = (match.group(2) or "").strip()
        body = re.sub(r"\s+", " ", match.group(3).strip())[:2000]
        if not body:
            continue
        entity_type = MATH_ENVIRONMENTS.get(env, EntityType.THEOREM)
        title = label or f"{env.title()} {len(entities) + 1}"
        entities.append(KnowledgeEntity(
            entity_id=_new_id("ent"),
            entity_type=entity_type,
            title=title,
            statement=body,
            source_id=source_id,
            confidence=0.7,
            metadata={"extraction": "latex_environment", "environment": env},
        ))
    return entities


def extract_from_text(text: str, source_id: str) -> list[KnowledgeEntity]:
    """Extract structure from plain text (PDF extraction fallback)."""
    entities: list[KnowledgeEntity] = []
    section_pattern = re.compile(
        r"(?i)^(theorem|lemma|definition|conjecture|hypothesis|method|result|limitation)\s*[:\d.]*\s*(.+)$",
        re.MULTILINE,
    )
    for match in section_pattern.finditer(text):
        keyword = match.group(1).lower()
        body = match.group(2).strip()[:2000]
        entity_type = MATH_ENVIRONMENTS.get(keyword) or EXPERIMENTAL_SECTIONS.get(keyword, EntityType.RESULT)
        entities.append(KnowledgeEntity(
            entity_id=_new_id("ent"),
            entity_type=entity_type,
            title=keyword.title(),
            statement=body,
            source_id=source_id,
            confidence=0.5,
            metadata={"extraction": "text_pattern"},
        ))
    return entities


def extract_citation_keys(tex_content: str) -> list[str]:
    """Extract BibTeX citation keys from LaTeX."""
    return list(set(re.findall(r"\\cite\{([^}]+)\}", tex_content)))


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()[:16]


def extract_document_structure(content: str, source_id: str, *, is_latex: bool = True) -> dict[str, Any]:
    """Full structure extraction pipeline."""
    if is_latex:
        entities = extract_from_latex(content, source_id)
        if not entities:
            entities = extract_from_text(content, source_id)
        citations = extract_citation_keys(content)
    else:
        entities = extract_from_text(content, source_id)
        citations = []
    return {
        "entities": entities,
        "citation_keys": citations,
        "content_hash": content_hash(content),
        "entity_count": len(entities),
    }
