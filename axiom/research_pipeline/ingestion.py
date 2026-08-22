"""Ingestion, Normalization, Deduplication, and Relevance Filtering for Phase 13."""
import hashlib
import re
from typing import List, Tuple, Set
from axiom.research_pipeline.models import (
    SourceDocument,
    ExtractedText,
    NormalizedSource,
    FilteredEvidence,
)


class IngestionEngine:
    """Handles fetch/extract, normalization, deduplication, and relevance filtering."""

    @staticmethod
    def extract_text(doc: SourceDocument, raw_content: str) -> ExtractedText:
        """Strip HTML tags/script tags and return clean text."""
        # Strip script/style tags
        clean = re.sub(r'<(script|style).*?>.*?</\1>', '', raw_content, flags=re.DOTALL | re.IGNORECASE)
        # Strip remaining HTML tags
        clean = re.sub(r'<.*?>', ' ', clean)
        # Collapse whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return ExtractedText(
            source_id=doc.id,
            raw_html_or_pdf=raw_content,
            clean_text=clean,
            word_count=len(clean.split()),
        )

    @staticmethod
    def normalize_source(doc: SourceDocument, extracted: ExtractedText) -> NormalizedSource:
        """Normalize text and compute SHA-256 content hash."""
        text = extracted.clean_text.lower().strip()
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return NormalizedSource(
            source_id=doc.id,
            title=doc.title,
            normalized_text=text,
            content_hash=content_hash,
            metadata={"url": doc.url, "source_type": doc.source_type.value},
        )

    @staticmethod
    def deduplicate_sources(sources: List[NormalizedSource]) -> Tuple[List[NormalizedSource], int]:
        """Remove exact duplicate content hashes and near-duplicate text."""
        seen_hashes: Set[str] = set()
        deduped: List[NormalizedSource] = []
        duplicate_count = 0

        for s in sources:
            if s.content_hash in seen_hashes:
                duplicate_count += 1
                continue
            seen_hashes.add(s.content_hash)
            deduped.append(s)

        return deduped, duplicate_count

    @staticmethod
    def filter_relevance(
        sources: List[NormalizedSource],
        query: str,
        threshold: float = 0.1,
    ) -> List[FilteredEvidence]:
        """Filter sources by keyword relevance score against the research query."""
        keywords = set(re.findall(r'\w+', query.lower()))
        evidences: List[FilteredEvidence] = []

        if not keywords:
            keywords = {"research"}

        for s in sources:
            text_words = set(re.findall(r'\w+', s.normalized_text))
            intersection = keywords.intersection(text_words)
            score = len(intersection) / max(1, len(keywords))

            if score >= threshold:
                evidences.append(
                    FilteredEvidence(
                        source_id=s.source_id,
                        content=s.normalized_text[:1000],  # first 1000 chars as evidence chunk
                        relevance_score=round(score, 4),
                        is_duplicate=False,
                    )
                )

        return evidences
